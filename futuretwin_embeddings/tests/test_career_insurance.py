import unittest
from unittest.mock import patch

from futuretwin_career_insurance import build_insurance, clean_alternatives, _diverse
from futuretwin_my_future import (
    MyFutureValidationError, _unique_relations, empty_state, read_state, validate_state,
)
from futuretwin_occupation_api import get_esco_occupation_catalog


def detail_for(uri, occupations, relations, confirmed=()):
    essential, optional = _unique_relations(relations.get(uri, {}))
    return {
        "occupation": occupations[uri],
        "matched_essential": [s for s in essential if s["uri"] in confirmed],
        "matched_optional": [s for s in optional if s["uri"] in confirmed],
        "missing_essential": [s for s in essential if s["uri"] not in confirmed],
        "missing_optional": [s for s in optional if s["uri"] not in confirmed],
    }


class InsuranceRankingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.occupations, _, cls.relations = get_esco_occupation_catalog()
        cls.cv = next(u for u, o in cls.occupations.items()
                      if o["label"] == "computer vision engineer")

    def build(self, uri=None, confirmed=(), state=None):
        uri = uri or self.cv
        return build_insurance(
            detail_for(uri, self.occupations, self.relations, confirmed),
            dict.fromkeys(confirmed), self.occupations, self.relations, state,
        )

    def test_real_cv_preparation_is_essential_contextual_and_diverse(self):
        result = self.build()
        self.assertEqual(len(result["prepare"]), 3)
        self.assertTrue(all(s["relation"] == "essential" for s in result["prepare"]))
        self.assertTrue(any(s["why"]["label_overlap"] for s in result["prepare"]))
        self.assertEqual(len({s["theme"] for s in result["prepare"]}), 3)
        self.assertTrue(all(s["description"] for s in result["prepare"]))
        self.assertTrue(all(s["status"] == "Not yet confirmed" for s in result["priorities"]))
        self.assertLessEqual(len(result["options"]), 3)
        self.assertEqual(result["comparison"]["denominator"], 3)

    def test_confirmed_skills_are_not_suggested_and_core_is_scenario_independent(self):
        before = self.build()
        confirmed = [s["uri"] for s in before["prepare"]]
        after = self.build(confirmed=confirmed)
        self.assertFalse(set(confirmed) & {s["uri"] for s in after["priorities"]})

    def test_manual_alternatives_exact_denominator_and_empty_selection(self):
        alternative = next(u for u, o in self.occupations.items()
                           if o["label"] == "data scientist")
        state = {"insurance_alternatives": {self.cv: [alternative]}}
        result = self.build(state=state)
        self.assertEqual(result["comparison"]["mode"], "user_selected")
        self.assertEqual(result["comparison"]["denominator"], 1)
        for skill in result["options"]:
            self.assertEqual(skill["comparison_denominator"], 1)
            self.assertEqual(skill["other_careers"][0]["uri"], alternative)
            ids = {s["uri"] for k in ("essential", "optional")
                   for s in self.relations[alternative][k]}
            self.assertIn(skill["uri"], ids)
        empty = self.build(state={"insurance_alternatives": {self.cv: []}})
        self.assertEqual(empty["options"], [])
        self.assertEqual(empty["comparison"]["denominator"], 0)
        self.assertTrue(empty["prepare"])

    def test_saved_career_and_exact_interest_are_meaningful_default_preferences(self):
        scientist = next(u for u, o in self.occupations.items()
                         if o["label"] == "data scientist")
        result = self.build(state={"saved_occupations": [scientist]})
        self.assertEqual(result["comparison"]["alternatives"][0]["uri"], scientist)
        self.assertEqual(result["comparison"]["alternatives"][0]["source"], "saved_career")
        interests = self.build(state={"preferences": {"interests": ["data scientist"]}})
        self.assertEqual(interests["comparison"]["alternatives"][0]["uri"], scientist)

    def test_real_different_targets_and_sparse_profiles(self):
        for name in ("nurse responsible for general care", "primary school teacher", "data analyst"):
            targets = [u for u, o in self.occupations.items() if o["label"] == name]
            for uri in targets:
                result = self.build(uri=uri)
                self.assertTrue(result["prepare"])
                target_ids = {s["uri"] for k in ("essential", "optional")
                              for s in self.relations[uri][k]}
                self.assertTrue(all(s["uri"] in target_ids for s in result["priorities"]))

    def test_diversity_first_pass_and_fill_are_deterministic(self):
        rows = [{"uri": str(i), "theme": theme}
                for i, theme in enumerate(("Software", "Software", "Data", "People"))]
        self.assertEqual([r["uri"] for r in _diverse(rows)], ["0", "2", "3"])
        self.assertEqual([r["uri"] for r in _diverse(rows[:2])], ["0", "1"])

    def test_selection_validation_persistence_and_legacy_defaults(self):
        other = next(u for u in self.occupations if u != self.cv)
        state = empty_state()
        state["insurance_alternatives"] = {self.cv: [other]}
        self.assertEqual(read_state(validate_state(state))["insurance_alternatives"],
                         {self.cv: [other]})
        legacy = dict(state)
        legacy.pop("insurance_alternatives")
        self.assertEqual(read_state(legacy)["insurance_alternatives"], {})
        for choices in ([self.cv], ["not-an-esco-uri"], [None]):
            state["insurance_alternatives"] = {self.cv: choices}
            with self.assertRaises(MyFutureValidationError):
                validate_state(state)
        self.assertEqual(clean_alternatives({self.cv: []}, self.occupations),
                         {self.cv: []})

    def test_missing_official_descriptions_are_not_fabricated(self):
        with patch("futuretwin_career_insurance.skill_descriptions", return_value={}):
            self.assertTrue(all(not s["description"] for s in self.build()["priorities"]))


if __name__ == "__main__":
    unittest.main()
