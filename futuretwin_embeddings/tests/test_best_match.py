import unittest
from unittest.mock import patch

from futuretwin_best_match import (
    effective_weights,
    load_config,
    rank_best_match,
)


def candidate(uri, label, essential=(1, 1), optional=(0, 0)):
    matched = essential[0] + optional[0]
    total = essential[1] + optional[1]
    return {
        "uri": uri,
        "title": label,
        "essential_match_count": essential[0],
        "matched_skill_count": matched,
        "interest_matches": [],
        "skill_coverage": {
            "matched_count": matched,
            "total_count": total,
            "percentage": matched / total * 100 if total else None,
            "essential": {"matched_count": essential[0], "total_count": essential[1]},
            "optional": {"matched_count": optional[0], "total_count": optional[1]},
        },
    }


def task_row(share, numerator=5, denominator=10):
    return {
        "mapping_status": "exact",
        "task_inventory_ready": True,
        "truncated_count": 0,
        "lower_exposure_eligible": True,
        "classified_count": denominator,
        "e1_count": numerator,
        "e2_count": 0,
        "predicted_task_exposure_share": share,
    }


def purpose_link(goal, direction):
    return {
        "occupation_uri": "career-a",
        "strength": "direct",
        "direction": direction,
        "review_status": "assistant_desk_reviewed",
        "target": {
            "goal_code": goal,
            "target_code": goal + ".1",
            "target_title": "Example UN target",
        },
    }


class BestMatchTests(unittest.TestCase):
    def setUp(self):
        self.config = load_config()

    def rank(self, items, *, goals=None, slider=30, tasks=None, links=None, confirmed=3):
        return rank_best_match(
            items,
            purpose_preferences={
                "goals": goals or [],
                "purpose_weight": slider,
                "skill_weight": 100 - slider,
            },
            task_inventory=tasks or {},
            task_metadata={"source": "Test O*NET inventory"},
            confirmed_count=confirmed,
            specific_count=2,
            config=self.config,
            purpose_links=links or {},
            purpose_review_scope="unit-test source review",
        )

    def test_saved_purpose_slider_cannot_change_three_factor_weights(self):
        for slider in (0, 30, 100):
            weights, _ = effective_weights({"purpose_weight": slider}, self.config)
            self.assertEqual(weights["skill_compatibility"], 65)
            self.assertNotIn("purpose_alignment", weights)
            self.assertEqual(weights["ai_task_exposure"], 25)
            self.assertEqual(weights["ai_benchmark_evidence"], 10)
            self.assertEqual(sum(weights.values()), 100)

    def test_skill_lists_are_normalized_separately(self):
        one = candidate("career-a", "A", essential=(1, 1), optional=(0, 10))
        two = candidate("career-b", "B", essential=(7, 10), optional=(2, 2))
        ranked, _ = self.rank([one, two])
        values = {row["uri"]: row["best_match"]["components"]["skill_compatibility"]["score"]
                  for row in ranked}
        self.assertAlmostEqual(values["career-a"], 0.7)
        self.assertAlmostEqual(values["career-b"], 0.79)

    def test_incomplete_occupation_skill_categories_are_not_grouped_as_comparable(self):
        essential_only = candidate("career-a", "A", essential=(1, 2), optional=(0, 0))
        both_lists = candidate("career-b", "B", essential=(1, 2), optional=(0, 3))
        ranked, _ = self.rank([essential_only, both_lists])
        groups = {row["uri"]: row["best_match"]["evidence_group"]["id"] for row in ranked}
        self.assertNotEqual(groups["career-a"], groups["career-b"])

    def test_missing_components_are_omitted_and_scores_use_separate_groups(self):
        with_task = candidate("career-a", "A", essential=(1, 2))
        without_task = candidate("career-b", "B", essential=(1, 2))
        ranked, metadata = self.rank(
            [with_task, without_task],
            tasks={"career-a": task_row(100)},
        )
        results = {row["uri"]: row["best_match"] for row in ranked}
        self.assertEqual(results["career-b"]["score"], 50)
        self.assertEqual(results["career-b"]["component_coverage"], {"available": 1, "total": 3})
        self.assertEqual(results["career-b"]["components"]["ai_task_exposure"]["status"], "unavailable")
        self.assertNotEqual(
            results["career-a"]["evidence_group"]["id"],
            results["career-b"]["evidence_group"]["id"],
        )
        self.assertTrue(all(group["score_comparable_within_group_only"] for group in metadata["groups"]))
        self.assertEqual(results["career-a"]["components"]["ai_benchmark_evidence"]["status"], "unavailable")

    def test_only_complete_exact_task_exposure_is_scored(self):
        items = [candidate("career-a", "A", essential=(1, 2))]
        bad = task_row(0)
        bad["lower_exposure_eligible"] = False
        bad["task_inventory_ready"] = False
        ranked, _ = self.rank(items, tasks={"career-a": bad})
        component = ranked[0]["best_match"]["components"]["ai_task_exposure"]
        self.assertEqual(component["status"], "unavailable")
        self.assertIsNone(component["score"])

        ranked, _ = self.rank(
            [candidate("career-a", "A", essential=(1, 2))],
            tasks={"career-a": task_row(20, numerator=2)},
        )
        component = ranked[0]["best_match"]["components"]["ai_task_exposure"]
        self.assertEqual(component["status"], "available")
        self.assertAlmostEqual(component["score"], 0.8)
        self.assertIn("not job-replacement probability", component["note"])

    def test_partial_purpose_evidence_is_not_a_best_match_factor(self):
        items = [candidate("career-a", "A", essential=(1, 2))]
        links = {"career-a": {"7": [purpose_link("7", "positive")]}}
        ranked, _ = self.rank(items, goals=["7", "1"], links=links)
        self.assertNotIn("purpose_alignment", ranked[0]["best_match"]["components"])
        self.assertEqual(ranked[0]["best_match"]["weighted_components"], ["skill_compatibility"])

    def test_purpose_priorities_reviews_and_slider_cannot_change_scores_or_order(self):
        items = [
            candidate("career-a", "A", essential=(3, 5)),
            candidate("career-b", "B", essential=(7, 10)),
        ]
        links = {
            "career-a": {"7": [purpose_link("7", "positive")],
                         "1": [purpose_link("1", "negative")]},
            "career-b": {"7": [purpose_link("7", "negative")],
                         "1": [purpose_link("1", "positive")]},
        }
        import copy
        goal7, meta7 = self.rank(copy.deepcopy(items), goals=["7"], slider=100, links=links)
        goal1, meta1 = self.rank(copy.deepcopy(items), goals=["1"], links=links)
        self.assertEqual(goal7[0]["uri"], "career-b")
        self.assertEqual(goal1[0]["uri"], "career-b")
        no_purpose, meta0 = self.rank(copy.deepcopy(items), goals=["7"], slider=0, links={})
        self.assertEqual(no_purpose[0]["uri"], "career-b")
        self.assertEqual(goal7, goal1)
        self.assertEqual(goal7, no_purpose)
        self.assertEqual(meta7, meta1)
        self.assertEqual(meta7, meta0)

    def test_actual_recommendation_candidates_change_with_confirmed_passport_skills(self):
        import futuretwin_intelligence
        import futuretwin_my_future as my_future
        import futuretwin_ranking_evidence
        import futuretwin_task_exposure

        occupations = {
            "career-a": {"label": "Career A", "description": "", "isco_group": "1"},
            "career-b": {"label": "Career B", "description": "", "isco_group": "2"},
        }
        relations = {
            "career-a": {"essential": [
                {"uri": "shared-skill", "label": "Shared"},
                {"uri": "skill-a", "label": "Skill A"},
            ], "optional": []},
            "career-b": {"essential": [
                {"uri": "shared-skill", "label": "Shared"},
                {"uri": "skill-b", "label": "Skill B"},
            ], "optional": []},
        }
        ranking = {"effective": "best_match", "options": [], "tie_breakers": []}
        no_exposure = ({}, {"reason": "No task data in this unit test."})
        with (
            patch.object(my_future, "get_esco_occupation_catalog",
                         return_value=(occupations, {}, relations)),
            patch.object(my_future, "_prevalence_limit", return_value=2),
            patch.object(my_future, "_confirmed_skills", side_effect=lambda profile: profile),
            patch.object(futuretwin_intelligence, "ranking_metadata", return_value=ranking),
            patch.object(futuretwin_intelligence, "hiring_unavailable", return_value={}),
            patch.object(futuretwin_ranking_evidence, "task_inventory", return_value=no_exposure),
            patch.object(futuretwin_ranking_evidence, "career_ranking_eligibility", return_value={}),
            patch.object(futuretwin_task_exposure, "safe_occupation_exposure",
                         return_value={"status": "not_enough_data"}),
        ):
            state = my_future.empty_state()
            first = my_future.build_recommendations({
                "shared-skill": {"uri": "shared-skill", "label": "Shared"},
                "skill-a": {"uri": "skill-a", "label": "Skill A"},
            }, state, sort="best_match")
            second = my_future.build_recommendations({
                "shared-skill": {"uri": "shared-skill", "label": "Shared"},
                "skill-b": {"uri": "skill-b", "label": "Skill B"},
            }, state, sort="best_match")
        self.assertEqual(first["recommendations"][0]["uri"], "career-a")
        self.assertEqual(second["recommendations"][0]["uri"], "career-b")


if __name__ == "__main__":
    unittest.main()
