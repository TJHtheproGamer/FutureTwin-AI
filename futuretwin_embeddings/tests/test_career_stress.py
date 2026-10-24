import copy
import unittest
from futuretwin_career_stress import build_stress_test


class CareerStressTests(unittest.TestCase):
    def setUp(self):
        self.occupations = {
            uri: {"uri": uri, "label": label}
            for uri, label in (("target", "Target"), ("other", "Related"), ("unrelated", "Other"))
        }
        self.a = {"uri": "a", "label": "Analyse data"}
        self.b = {"uri": "b", "label": "Build reports"}
        self.relations = {
            "target": {"essential": [self.a, self.b], "optional": []},
            "other": {"essential": [self.a, self.b], "optional": []},
            "unrelated": {"essential": [{"uri": "x", "label": "Other"}]},
        }
        self.detail = {
            "occupation": self.occupations["target"],
            "matched_essential": [self.a], "matched_optional": [],
            "missing_essential": [self.b], "missing_optional": [],
            "ai_impact": {"task_groups": [{
                "task": "Join data tables", "score": 42, "model": "Stored model",
                "skills": [{"skill_uri": "a"}, {"skill_uri": "irrelevant"}],
                "independently_verified": False,
            }]},
        }

    def build(self):
        return build_stress_test(self.detail, {"a": self.a}, self.occupations, self.relations)

    def test_three_hypotheses_share_observed_evidence_not_invented_predictions(self):
        result = self.build()
        self.assertEqual(len(result["scenarios"]), 3)
        self.assertEqual(len({s["assumption"] for s in result["scenarios"]}), 3)
        self.assertEqual(len({s["prepare"][0] for s in result["scenarios"]}), 3)
        for scenario in result["scenarios"]:
            self.assertEqual(scenario["changes"][0]["skills"], [self.a])
            self.assertIn("not verified", scenario["changes"][0]["relationship"])
            self.assertEqual(scenario["valuable"][0]["uri"], "a")
            self.assertNotIn("automation_probability", scenario)
        self.assertEqual(result["evidence"]["benchmark_baseline"], self.detail["ai_impact"])

    def test_insurance_uses_unconfirmed_exact_relations_and_shared_options(self):
        result = self.build()
        plan = result["insurance"]
        self.assertIn("does not mean", plan["notice"])
        self.assertEqual([s["uri"] for s in plan["priorities"]], ["b"])
        self.assertEqual(plan["priorities"][0]["shared_career_count"], 1)
        self.assertEqual(
            [{k: c[k] for k in ("uri", "label")} for c in result["evidence"]["related_careers"]],
            [self.occupations["other"]],
        )
        self.assertFalse(plan["priorities"][0]["confirmed"])

    def test_missing_evidence_is_explicit_and_inputs_are_not_mutated(self):
        self.detail["ai_impact"] = {}
        original = copy.deepcopy(self.detail)
        result = self.build()
        self.assertEqual(self.detail, original)
        self.assertEqual(result["scenarios"][0]["changes"], [])
        self.assertIn("Not enough task evidence for this career.", result["scenarios"][0]["limitations"])
        self.assertEqual(len(result["evidence"]["labour_market"]), 8)
        for evidence in result["evidence"]["labour_market"]:
            self.assertEqual(evidence["status"], "unavailable")
            self.assertIsNone(evidence["value"])

    def test_no_confirmed_skills_or_no_associations_do_not_fake_transferability(self):
        self.detail.update(matched_essential=[], missing_essential=[])
        result = build_stress_test(self.detail, {}, self.occupations, self.relations)
        self.assertEqual(result["scenarios"][0]["valuable"], [])
        self.assertEqual(result["insurance"]["priorities"], [])

    def test_duplicate_tasks_are_deduplicated_and_unknown_skills_excluded(self):
        group = self.detail["ai_impact"]["task_groups"][0]
        self.detail["ai_impact"]["task_groups"].append(copy.deepcopy(group))
        result = self.build()
        self.assertEqual(len(result["scenarios"][0]["changes"]), 1)
        self.assertEqual(len(result["evidence"]["benchmark_baseline"]["task_groups"]), 2)

    def test_scenario_profiles_select_different_real_steps_and_candidate_scope(self):
        from futuretwin_career_scenarios import build_scenarios, SCENARIO_PROFILES
        self.detail["missing_essential"].append({"uri": "c", "label": "Review work"})
        practice = [self.a, self.b, {"uri": "c", "label": "Review work"}]
        changes = [
            {"task": f"Stored task {i}", "skills": [skill],
             "relationship": "semantic_candidate"}
            for i, skill in enumerate(practice)
        ]
        insurance = {"prepare": [{**s, "relation": "essential"} for s in practice]}
        result = build_scenarios(self.detail, insurance, changes, [])
        self.assertEqual([len(s["workflow"]["steps"]) for s in result], [1, 2, 3])
        self.assertEqual([len(s["changes"]) for s in result], [1, 2, 3])
        self.assertEqual(len({s["profile"]["scope"] for s in result}), 3)
        self.assertEqual(len({s["prepare"][0] for s in result}), 3)
        self.assertTrue(all("Hypothetical" in s["workflow"]["note"] for s in result))
        # Profiles can be changed without altering the benchmark or skill data.
        custom = ({**SCENARIO_PROFILES[0], "max_workflow_steps": 2},)
        changed = build_scenarios(self.detail, insurance, changes, [], profiles=custom)
        self.assertEqual(len(changed[0]["workflow"]["steps"]), 2)
        self.assertEqual(len(changes), 3)

    def test_sparse_scenarios_never_invent_steps_or_benchmark_evidence(self):
        from futuretwin_career_scenarios import build_scenarios
        detail = {"occupation": self.detail["occupation"]}
        scenarios = build_scenarios(detail, {"prepare": []}, [], [])
        for scenario in scenarios:
            self.assertEqual(scenario["workflow"]["steps"], [])
            self.assertEqual(scenario["changes"], [])
            self.assertEqual(scenario["valuable"], [])
            self.assertIn("Not enough task evidence for this career.", scenario["limitations"])


if __name__ == "__main__":
    unittest.main()
