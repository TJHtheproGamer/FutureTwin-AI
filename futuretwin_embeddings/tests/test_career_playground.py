import copy
import unittest
from unittest.mock import patch

from futuretwin_playground import (
    build_career_map, career_experience, CV_OCCUPATION, IMAGE_PROCESSING,
    DATA_ANALYST_OCCUPATION, DATA_QUALITY_ASSESSMENT,
    CUSTOMER_SERVICE_OCCUPATION, IDENTIFY_CUSTOMER_NEEDS,
    PRIMARY_TEACHER_OCCUPATION, ASSESS_STUDENTS,
)
from futuretwin_career_insurance import build_insurance
from futuretwin_occupation_api import get_esco_occupation_catalog
from test_career_insurance import detail_for


class CareerMapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.occupations, _, cls.relations = get_esco_occupation_catalog()
        cls.cv = next(u for u, o in cls.occupations.items()
                      if o["label"] == "computer vision engineer")

    def build(self, confirmed=(), state=None):
        detail = detail_for(self.cv, self.occupations, self.relations, confirmed)
        detail["stress_test"] = {"insurance": build_insurance(
            detail, dict.fromkeys(confirmed), self.occupations, self.relations, state
        )}
        snapshot = copy.deepcopy(detail)
        graph = build_career_map(
            detail, dict.fromkeys(confirmed), self.occupations, self.relations
        )
        self.assertEqual(snapshot, detail)
        return graph

    def test_real_cv_map_edges_are_exact_and_complete_in_scope(self):
        graph = self.build()
        self.assertEqual(graph["occupation"]["uri"], self.cv)
        self.assertEqual(len(graph["occupations"]), 4)
        self.assertEqual(len(graph["skills"]), 52)
        selected = {o["uri"] for o in graph["occupations"]}
        for skill in graph["skills"]:
            self.assertFalse(skill["confirmed"])
            actual = {edge["occupation_uri"]: edge["relation"]
                      for edge in skill["connections"]}
            expected = {}
            for uri in selected:
                for relation in ("optional", "essential"):
                    if any(s["uri"] == skill["uri"]
                           for s in self.relations[uri][relation]):
                        expected[uri] = relation
            self.assertEqual(actual, expected)

    def test_confirmation_uses_identity_and_is_prioritized(self):
        uri = self.relations[self.cv]["optional"][0]["uri"]
        graph = self.build([uri, "not-a-real-uri"])
        self.assertEqual(graph["skills"][0]["uri"], uri)
        self.assertTrue(graph["skills"][0]["confirmed"])
        self.assertNotIn("not-a-real-uri", {s["uri"] for s in graph["skills"]})

    def test_explicit_no_comparisons_has_no_alternative_edges(self):
        graph = self.build(state={"insurance_alternatives": {self.cv: []}})
        self.assertEqual(len(graph["occupations"]), 1)
        self.assertTrue(all(
            s["connections"] == [
                {"occupation_uri": self.cv, "relation": s["relation"]}
            ] for s in graph["skills"]
        ))

    def test_confirmed_alternative_only_skill_has_no_target_edge(self):
        alternative = self.build()["occupations"][1]["uri"]
        target_ids = {s["uri"] for rows in self.relations[self.cv].values() for s in rows}
        extra = next(s["uri"] for rows in self.relations[alternative].values()
                     for s in rows if s["uri"] not in target_ids)
        graph = self.build([extra], {"insurance_alternatives": {self.cv: [alternative]}})
        row = next(s for s in graph["skills"] if s["uri"] == extra)
        self.assertIsNone(row["relation"])
        self.assertTrue(row["confirmed"])
        self.assertEqual({edge["occupation_uri"] for edge in row["connections"]},
                         {alternative})

    def test_empty_relations_and_duplicate_identity(self):
        occupations = {"a": {"uri": "a", "label": "Career A"}}
        detail = {"occupation": occupations["a"]}
        with patch("futuretwin_playground.skill_descriptions", return_value={}):
            graph = build_career_map(detail, {}, occupations, {})
            self.assertEqual(graph["skills"], [])
            rows = {"a": {"essential": [{"uri": "s", "label": "Same"}],
                          "optional": [{"uri": "s", "label": "Same"}]}}
            graph = build_career_map(detail, {"s": {}}, occupations, rows)
            self.assertEqual(len(graph["skills"]), 1)
            self.assertEqual(graph["skills"][0]["relation"], "essential")
            self.assertEqual(graph["skills"][0]["description"], "")

    def test_experience_is_bound_to_real_esco_relation(self):
        experience = career_experience(
            self.occupations[self.cv], self.relations[self.cv]
        )
        self.assertEqual(self.cv, CV_OCCUPATION)
        self.assertEqual(experience["status"], "available")
        self.assertEqual(experience["source"]["skill"]["uri"], IMAGE_PROCESSING)
        self.assertIn("contrast stretching",
                      experience["source"]["skill"]["description"])
        self.assertEqual(experience["kind"], "illustrative_practice")
        self.assertNotIn("score", experience)
        self.assertEqual(sum(c["supported"] for c in experience["choices"]), 1)
        pixels = experience["image"]["pixels"]
        self.assertEqual(len(pixels), experience["image"]["width"] *
                         experience["image"]["height"])
        self.assertTrue(all(0 <= value <= 255 for value in pixels))
        stretched = [round(255 * (p - min(pixels)) / (max(pixels) - min(pixels)))
                     for p in pixels]
        self.assertEqual(set(stretched), {0, 255})

    def test_additional_local_exercises_use_exact_essential_esco_skills(self):
        examples = [
            (DATA_ANALYST_OCCUPATION, DATA_QUALITY_ASSESSMENT, "data quality assessment"),
            (CUSTOMER_SERVICE_OCCUPATION, IDENTIFY_CUSTOMER_NEEDS, "identify customer's needs"),
            (PRIMARY_TEACHER_OCCUPATION, ASSESS_STUDENTS, "assess students"),
        ]
        for occupation_uri, skill_uri, expected_label in examples:
            with self.subTest(occupation=occupation_uri):
                experience = career_experience(
                    self.occupations[occupation_uri], self.relations[occupation_uri]
                )
                self.assertEqual(experience["status"], "available")
                self.assertEqual(experience["source"]["skill"]["uri"], skill_uri)
                self.assertEqual(
                    experience["source"]["skill"]["label"].casefold(), expected_label
                )
                self.assertEqual(experience["source"]["skill"]["relation"], "essential")
                self.assertEqual(experience["kind"], "illustrative_practice")
                self.assertNotIn("score", experience)
                self.assertEqual(sum(c["supported"] for c in experience["choices"]), 1)
                self.assertIn(experience["activity"]["type"], {"table", "scenario"})
                self.assertIn("synthetic", experience["notice"].casefold())

    def test_experience_unavailable_for_unvalidated_careers(self):
        supported = {
            CV_OCCUPATION, DATA_ANALYST_OCCUPATION,
            CUSTOMER_SERVICE_OCCUPATION, PRIMARY_TEACHER_OCCUPATION,
        }
        other = next(o for o in self.occupations.values() if o["uri"] not in supported)
        self.assertEqual(career_experience(other, self.relations[self.cv])["status"],
                         "unavailable")
        self.assertEqual(career_experience(self.occupations[self.cv], {})["status"],
                         "unavailable")


if __name__ == "__main__":
    unittest.main()
