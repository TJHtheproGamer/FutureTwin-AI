"""Synthetic local-only extraction checks, including evidence and privacy."""
import unittest
from unittest.mock import patch

from futuretwin_local_extraction import extract_local_skills
from futuretwin_skills_profile import validated_extraction


class LocalExtractionTests(unittest.TestCase):
    def test_literal_mentions_and_activity_are_source_grounded_without_network(self):
        text = "Skills: Python, SQL.\nBuilt reports and analysed customer data."
        with patch("socket.socket.connect", side_effect=AssertionError("No network")):
            raw = extract_local_skills(text)
        values = [s["value"] for s in raw["explicit_skills"]]
        self.assertIn("Python", values)
        self.assertIn("SQL", values)
        self.assertTrue(raw["work_activities"])
        checked = validated_extraction(raw, text)
        self.assertTrue(checked["skills"])
        for item in checked["skills"]:
            self.assertIn(item["value"], text)
            self.assertIn(item["evidence"], text)
            self.assertFalse(item["confirmed"])
            self.assertIsNone(item["selected_esco_uri"])

    def test_negation_privacy_and_unrelated_information(self):
        text = ("No experience in Python.\nEmail: synthetic@example.test\n"
                "Studied at Example University, CGPA 3.8.\n"
                "Managed orders for a small shop.")
        result = extract_local_skills(text, "experience")
        self.assertNotIn("Python", [s["value"] for s in result["explicit_skills"]])
        combined = validated_extraction(result, text)["skills"]
        self.assertTrue(any("Managed orders" in s["value"] for s in combined))
        for row in combined:
            self.assertNotIn("@", row["evidence"])
            self.assertNotIn("University", row["evidence"])
            self.assertNotIn("CGPA", row["evidence"])

    def test_empty_oversized_and_unknown_sources(self):
        self.assertEqual(extract_local_skills(""), {"explicit_skills": [], "work_activities": []})
        with self.assertRaises(ValueError):
            extract_local_skills("x" * 30_001)
        with self.assertRaises(ValueError):
            extract_local_skills("Python", "unsupported")


if __name__ == "__main__":
    unittest.main()
