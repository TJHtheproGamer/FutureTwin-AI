"""Repeatable synthetic tests; never call an LLM or use real personal data."""
from __future__ import annotations

import copy
import io
import json
import os
from pathlib import Path
import sys
import unittest
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from docx import Document
from flask import Flask
import futuretwin_resume_api as api
from futuretwin_skills_profile import (
    ProfileValidationError, clean_user_profile, enrich_skills,
    merge_stored_profile, public_profile, validated_extraction,
)

SOURCE = """Synthetic Example
Education: BSc Computer Science, Example University, CGPA 3.8
Skills: Python, SQL, React
Projects: Built interactive dashboards using Python and SQL.
Experience: Automated weekly reporting to reduce manual work.
Interests: hiking
"""
RAW = {
    "explicit_skills": [
        {"value": x, "evidence": "Skills: Python, SQL, React"}
        for x in ("Python", "SQL", "React")
    ],
    "work_activities": [
        {"value": "Built interactive dashboards using Python and SQL.",
         "evidence": "Projects: Built interactive dashboards using Python and SQL."},
        {"value": "Automated weekly reporting to reduce manual work.",
         "evidence": "Experience: Automated weekly reporting to reduce manual work."},
    ],
}


def fake_match(value, top_k=3):
    return [
        {"skill_uri": f"urn:synthetic:skill:{i}", "skill": f"Synthetic candidate {i}",
         "cosine_similarity": .9 - i / 10}
        for i in range(1, top_k + 1)
    ]


def docx_bytes():
    doc = Document()
    for line in SOURCE.splitlines():
        doc.add_paragraph(line)
    out = io.BytesIO()
    doc.save(out)
    return out.getvalue()


class SkillsSchemaTests(unittest.TestCase):
    def test_only_skills_and_activities_are_extracted(self):
        result = validated_extraction({**RAW, "education": [{"value": "BSc"}]}, SOURCE)
        self.assertEqual(set(result), {"schema_version", "skills"})
        self.assertEqual(len(result["skills"]), 5)
        self.assertEqual({r["origin"] for r in result["skills"]},
                         {"explicit", "activity_suggestion"})
        self.assertNotIn("University", json.dumps(result))
        self.assertNotIn("CGPA", json.dumps(result))
        for row in result["skills"]:
            self.assertIn(row["value"], SOURCE)
            self.assertIn(row["evidence"], SOURCE)
            self.assertFalse(row["confirmed"])
            self.assertIsNone(row["selected_esco_uri"])

    def test_unsupported_facts_and_academic_metadata_rejected(self):
        raw = copy.deepcopy(RAW)
        raw["explicit_skills"].extend([
            {"value": "Java", "evidence": "Skills: Python, SQL, React"},
            {"value": "BSc Computer Science",
             "evidence": "Education: BSc Computer Science, Example University, CGPA 3.8"},
            {"value": "Example University",
             "evidence": "Education: BSc Computer Science, Example University, CGPA 3.8"},
            {"value": "CGPA 3.8",
             "evidence": "Education: BSc Computer Science, Example University, CGPA 3.8"},
        ])
        raw["work_activities"].append({
            "value": "data visualization", "evidence": "Built interactive dashboards using Python and SQL."
        })
        result = validated_extraction(raw, SOURCE)
        self.assertEqual(len(result["skills"]), 5)

    def test_contaminated_quote_reduced_to_exact_skill_phrase(self):
        source = "Example University: Python"
        result = validated_extraction({
            "explicit_skills": [{"value": "Python", "evidence": source}],
            "work_activities": [],
        }, source)
        self.assertEqual(result["skills"][0]["evidence"], "Python")

    def test_normalisation_duplicate_and_fake_confirmation(self):
        raw = {"explicit_skills": [
            {"value": " python ", "evidence": "Skills: Python, SQL, React", "confirmed": True},
            {"value": "Python", "evidence": "Skills: Python, SQL, React"},
        ], "work_activities": []}
        result = validated_extraction(raw, SOURCE)
        self.assertEqual(len(result["skills"]), 1)
        self.assertFalse(result["skills"][0]["confirmed"])

    def test_malformed_list_rejected_and_missing_list_empty(self):
        with self.assertRaises(ValueError):
            validated_extraction({"explicit_skills": "Python"}, SOURCE)
        self.assertEqual(validated_extraction({}, SOURCE)["skills"], [])

    def test_minilm_adapter_keeps_order_not_scores_or_auto_selection(self):
        rows = validated_extraction(RAW, SOURCE)["skills"]
        enriched = enrich_skills(rows, fake_match)
        self.assertEqual([x["uri"] for x in enriched[0]["esco_candidates"]],
                         ["urn:synthetic:skill:1", "urn:synthetic:skill:2", "urn:synthetic:skill:3"])
        self.assertEqual(set(enriched[0]["esco_candidates"][0]), {"uri", "label"})
        self.assertFalse(enriched[0]["confirmed"])

    def test_save_only_skills_no_proficiency_or_new_private_fields(self):
        result = clean_user_profile({
            "education": [{"value": "New private data"}], "university": "Do not persist",
            "skills": [{"value": "Python", "evidence": "Skills: Python",
                        "origin": "explicit", "proficiency": "expert"}],
        }, fake_match)
        self.assertEqual(set(result), {"schema_version", "skills"})
        self.assertNotIn("proficiency", result["skills"][0])
        self.assertFalse(result["skills"][0]["confirmed"])

    def test_confirmation_requires_real_candidate_and_boolean(self):
        row = {"value": "Python", "origin": "explicit", "confirmed": True}
        for changes in ({}, {"selected_esco_uri": "urn:invented"},
                        {"confirmed": "true"}, {"origin": []}):
            with self.subTest(changes=changes), self.assertRaises(ProfileValidationError):
                clean_user_profile({"skills": [{**row, **changes}]}, fake_match)
        saved = clean_user_profile({"skills": [{
            **row, "selected_esco_uri": "urn:synthetic:skill:2",
        }]}, fake_match)
        self.assertTrue(saved["skills"][0]["confirmed"])

    def test_legacy_public_view_and_non_destructive_save(self):
        legacy = {
            "education": [{"value": "Original private education"}],
            "experience": [{"value": "Original private experience"}],
            "projects": [{"value": "Original private project"}],
            "interests": [], "custom": {"keep": True},
            "skills": [{"value": "Python", "evidence": "Python",
                        "esco_candidates": [{"uri": "urn:synthetic:skill:1", "label": "Example"}],
                        "selected_esco_uri": "urn:synthetic:skill:1"}],
        }
        original = copy.deepcopy(legacy)
        view = public_profile(legacy)
        self.assertNotIn("education", view)
        self.assertNotIn("experience", view)
        self.assertEqual(view["skills"][0]["origin"], "legacy")
        self.assertFalse(view["skills"][0]["confirmed"])
        reviewed = clean_user_profile({"skills": view["skills"]}, fake_match)
        merged = merge_stored_profile(legacy, reviewed)
        self.assertEqual(legacy, original)
        self.assertEqual(merged["_legacy_profile"], original)
        edited = merge_stored_profile(merged, {"skills": []})
        self.assertEqual(edited["_legacy_profile"], original)
        self.assertEqual(public_profile(edited)["skills"], [])
        self.assertTrue(public_profile(edited)["has_legacy_data"])


class SecurityAndRouteTests(unittest.TestCase):
    def setUp(self):
        self.environment = patch.dict(os.environ, {"SESSION_SECRET": "synthetic-unit-test-only"})
        self.environment.start()
        self.addCleanup(self.environment.stop)
        self.app = Flask(__name__)
        api.register_resume_routes(self.app)
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()
        with patch.object(api, "_load_profile", return_value=None):
            self.csrf = self.client.get("/api/profile").get_json()["csrf_token"]
        self.headers = {"X-CSRF-Token": self.csrf}

    def test_encryption_uses_fresh_nonce_and_authenticated_roundtrip(self):
        profile = {"schema_version": 2, "skills": [{"value": "Synthetic confidential skill"}]}
        first, second = api._encrypt_profile(profile), api._encrypt_profile(profile)
        self.assertNotEqual(first, second)
        self.assertNotIn(b"Synthetic confidential", first)
        self.assertEqual(api._decrypt_profile(first), profile)
        tampered = first[:-1] + bytes([first[-1] ^ 1])
        with self.assertRaises(Exception):
            api._decrypt_profile(tampered)

    def test_legacy_data_stays_encrypted_during_database_save(self):
        previous = {"education": [{"value": "Keep privately"}], "skills": []}
        connection = MagicMock()
        connection.__enter__.return_value = connection
        timestamp = datetime(2026, 1, 1, tzinfo=timezone.utc)
        connection.execute.return_value.fetchone.side_effect = [
            (api._encrypt_profile(previous),), (timestamp, timestamp),
        ]
        with patch.object(api, "_database_connection", return_value=connection):
            result = api._save_profile(b"x" * 32, {"schema_version": 2, "skills": []})
        stored_blob = connection.execute.call_args_list[2].args[1][2]
        self.assertEqual(api._decrypt_profile(stored_blob)["_legacy_profile"], previous)
        self.assertTrue(result["has_legacy_data"])
        self.assertNotIn("education", result)

    def test_csrf_required_on_every_mutation(self):
        for method, path in (
            ("post", "/api/profile/extract"), ("post", "/api/profile/match"),
            ("post", "/api/profile"), ("delete", "/api/profile"),
        ):
            with self.subTest(path=path):
                response = getattr(self.client, method)(path, json={})
                self.assertEqual(response.status_code, 403)

    def test_consent_required_and_invalid_pdf_rejected_before_llm(self):
        with patch.object(api, "_extract_resume_skills") as llm:
            response = self.client.post("/api/profile/extract", headers=self.headers, data={
                "resume": (io.BytesIO(docx_bytes()), "synthetic.docx"),
            })
            self.assertEqual(response.status_code, 400)
            response = self.client.post("/api/profile/extract", headers=self.headers, data={
                "consent": "true", "resume": (io.BytesIO(b"fake pdf"), "fake.pdf"),
            })
            self.assertEqual(response.status_code, 400)
            llm.assert_not_called()

    def test_synthetic_docx_extraction_preserves_work_evidence_only(self):
        with patch.object(api, "_extract_resume_skills", return_value=RAW), \
                patch("futuretwin_skill_api.match_skills", side_effect=fake_match), \
                patch.object(api, "_save_profile") as save:
            response = self.client.post("/api/profile/extract", headers=self.headers, data={
                "consent": "true", "resume": (io.BytesIO(docx_bytes()), "synthetic.docx"),
            })
        self.assertEqual(response.status_code, 200)
        draft = response.get_json()["draft"]
        self.assertEqual(set(draft), {"schema_version", "skills"})
        self.assertEqual(draft["schema_version"], 2)
        self.assertEqual(len(draft["skills"]), 5)
        self.assertTrue(any(r["origin"] == "activity_suggestion" for r in draft["skills"]))
        self.assertNotIn("University", json.dumps(draft))
        for row in draft["skills"]:
            self.assertIn(row["value"], SOURCE)
            self.assertIn(row["evidence"], SOURCE)
            self.assertFalse(row["confirmed"])
            self.assertIsNone(row["selected_esco_uri"])
            self.assertNotIn("proficiency", row)
        save.assert_not_called()

    def test_rematch_and_confirmation_validation(self):
        with patch("futuretwin_skill_api.match_skills", side_effect=fake_match):
            matches = self.client.post("/api/profile/match", headers=self.headers,
                                       json={"value": "Python"}).get_json()
            self.assertEqual(len(matches["esco_candidates"]), 3)
            bad = self.client.post("/api/profile", headers=self.headers, json={
                "skills": [{"value": "Python", "confirmed": True}],
            })
            self.assertEqual(bad.status_code, 400)

    def test_delete_is_owner_scoped_and_clears_owner_session(self):
        with patch.object(api, "_delete_profile", return_value=True) as delete:
            response = self.client.delete("/api/profile", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(delete.call_args.args[0]), 32)
        with self.client.session_transaction() as session:
            self.assertNotIn("ft_profile_owner", session)


if __name__ == "__main__":
    unittest.main()
