import unittest

from futuretwin_my_future import (
    _prevalence_limit,
    build_career_details,
    build_recommendations,
    empty_state,
    read_state,
    validate_state,
)
from futuretwin_occupation_api import _load_esco
from futuretwin_skills_profile import merge_stored_profile, public_profile


def profile_with_skills(confirmed_uris, unconfirmed_uris=()):
    occupations, _, relations = _load_esco()
    labels = {}
    for groups in relations.values():
        for relation in ("essential", "optional"):
            for skill in groups[relation]:
                labels.setdefault(skill["uri"], skill["label"])
    rows = []
    for uri in confirmed_uris:
        rows.append({
            "value": labels[uri],
            "evidence": "",
            "origin": "user_added",
            "esco_candidates": [{"uri": uri, "label": labels[uri]}],
            "selected_esco_uri": uri,
            "confirmed": True,
        })
    for uri in unconfirmed_uris:
        rows.append({
            "value": labels[uri],
            "evidence": "",
            "origin": "user_added",
            "esco_candidates": [{"uri": uri, "label": labels[uri]}],
            "selected_esco_uri": uri,
            "confirmed": False,
        })
    return {"schema_version": 2, "skills": rows}


class MyFutureMatchingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.occupations, _, cls.relations = _load_esco()
        cls.skill_frequency = {}
        for occupation_uri, groups in cls.relations.items():
            for relation in ("essential", "optional"):
                for skill in groups[relation]:
                    cls.skill_frequency.setdefault(skill["uri"], set()).add(
                        occupation_uri
                    )
        cls.limit = _prevalence_limit(len(cls.occupations))

    def test_only_confirmed_esco_ids_are_used(self):
        target_uri = next(
            uri for uri in self.occupations
            if self.relations.get(uri, {}).get("essential")
            or self.relations.get(uri, {}).get("optional")
        )
        groups = self.relations[target_uri]
        skill_uri = next(
            skill["uri"]
            for relation in ("essential", "optional")
            for skill in groups[relation]
            if len(self.skill_frequency.get(skill["uri"], ())) <= self.limit
        )
        unconfirmed_uri = next(
            skill["uri"]
            for relation in ("essential", "optional")
            for skill in groups[relation]
            if skill["uri"] != skill_uri
        )
        profile = profile_with_skills([skill_uri], [unconfirmed_uri])
        result = build_recommendations(profile, empty_state())
        self.assertIn(result["status"], {"ok", "no_matches"})
        for career in result["recommendations"]:
            self.assertNotIn(
                unconfirmed_uri,
                {item["uri"] for item in career["matched_skills"]},
            )

    def test_common_skills_do_not_create_broad_recommendations(self):
        most_common = max(self.skill_frequency, key=lambda uri: len(self.skill_frequency[uri]))
        self.assertGreater(len(self.skill_frequency[most_common]), self.limit)
        result = build_recommendations(profile_with_skills([most_common]))
        self.assertEqual(result["status"], "skills_too_broad")
        self.assertEqual(result["recommendations"], [])

    def test_missing_confirmed_skills_returns_empty_state(self):
        result = build_recommendations(
            profile_with_skills([], [next(iter(self.skill_frequency))])
        )
        self.assertEqual(result["status"], "no_confirmed_skills")
        self.assertEqual(result["recommendations"], [])

    def test_coverage_uses_unique_official_relations(self):
        occupation_uri = next(
            uri for uri, groups in self.relations.items()
            if len(groups["essential"]) + len(groups["optional"]) >= 2
        )
        matched_uri = self.relations[occupation_uri]["essential"][0]["uri"]
        details = build_career_details(
            occupation_uri, profile_with_skills([matched_uri]), empty_state()
        )
        all_skill_uris = {
            item["uri"]
            for group in ("essential", "optional")
            for item in self.relations[occupation_uri][group]
        }
        self.assertEqual(details["skill_coverage"]["matched_count"], 1)
        self.assertEqual(details["skill_coverage"]["total_count"], len(all_skill_uris))
        self.assertNotIn(
            matched_uri,
            {item["uri"] for item in details["missing_essential"]},
        )

    def test_learning_progress_must_match_the_saved_career(self):
        occupation_uri, groups = next(
            (uri, groups) for uri, groups in self.relations.items()
            if groups["essential"] or groups["optional"]
        )
        skill_uri = (groups["essential"] or groups["optional"])[0]["uri"]
        state = validate_state({
            "preferences": {
                "career_areas": [],
                "interests": ["design"],
                "target_occupation_uri": occupation_uri,
            },
            "saved_occupations": [],
            "roadmap_progress": {occupation_uri: [skill_uri]},
        })
        self.assertIn(occupation_uri, state["saved_occupations"])
        self.assertEqual(state["roadmap_progress"][occupation_uri], [skill_uri])
        with self.assertRaises(ValueError):
            validate_state({
                "preferences": {},
                "saved_occupations": [],
                "roadmap_progress": {occupation_uri: ["not-an-esco-skill"]},
            })

    def test_learning_goals_are_validated_returned_and_backward_compatible(self):
        occupation_uri, groups = next(
            (uri, groups) for uri, groups in self.relations.items()
            if groups["essential"] or groups["optional"]
        )
        goal_uri = (groups["essential"] or groups["optional"])[0]["uri"]
        state = validate_state({
            "preferences": {
                "career_areas": [],
                "interests": [],
                "target_occupation_uri": occupation_uri,
            },
            "saved_occupations": [],
            "roadmap_progress": {},
            "roadmap_goals": {occupation_uri: [goal_uri]},
        })
        self.assertEqual(state["roadmap_goals"][occupation_uri], [goal_uri])
        self.assertEqual(read_state(state)["roadmap_goals"][occupation_uri], [goal_uri])
        details = build_career_details(
            occupation_uri, profile_with_skills([]), state
        )
        self.assertIn(goal_uri, details["roadmap_goals"])

        legacy = {
            "preferences": {
                "career_areas": [],
                "interests": [],
                "target_occupation_uri": None,
            },
            "saved_occupations": [],
            "roadmap_progress": {},
        }
        self.assertEqual(read_state(legacy)["roadmap_goals"], {})

        with self.assertRaises(ValueError):
            validate_state({
                "preferences": {},
                "saved_occupations": [],
                "roadmap_goals": {occupation_uri: ["not-an-esco-skill"]},
            })

    def test_future_state_survives_legacy_profile_upgrade(self):
        future = {
            "preferences": {"career_areas": [], "interests": [], "target_occupation_uri": None},
            "saved_occupations": [],
            "roadmap_progress": {},
        }
        previous = {"education": ["legacy data"], "my_future": future}
        upgraded = merge_stored_profile(previous, {"skills": []})
        self.assertEqual(upgraded["my_future"], future)
        self.assertEqual(upgraded["_legacy_profile"], previous)

    def test_my_future_settings_are_not_exposed_by_the_passport_api_projection(self):
        profile = public_profile({
            "schema_version": 2,
            "skills": [],
            "my_future": {"saved_occupations": ["private-to-owner"]},
        })
        self.assertNotIn("my_future", profile)
        self.assertNotIn("saved_occupations", profile)


if __name__ == "__main__":
    unittest.main()
