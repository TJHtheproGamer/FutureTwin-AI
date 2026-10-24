"""Direct Passport confirmations: local catalog, append-only, session-owned."""
import copy
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from flask import Flask
import futuretwin_resume_api as api
from futuretwin_skills_profile import (
    ProfileValidationError, append_confirmed_skills, public_profile,
)


URI = "urn:test:python"


def skill(uri=URI, label="Python", confirmed=True):
    return {"value": label, "evidence": "", "origin": "user_added",
            "confirmed": confirmed, "selected_esco_uri": uri,
            "esco_candidates": [{"uri": uri, "label": label}]}


class QuickAddTests(unittest.TestCase):
    def setUp(self):
        self.env = patch.dict(os.environ, {"SESSION_SECRET": "synthetic-quick-add-only"})
        self.env.start()
        self.addCleanup(self.env.stop)
        self.app = Flask(__name__)
        api.register_resume_routes(self.app)
        self.client = self.app.test_client()
        with self.client.session_transaction() as sess:
            sess["ft_profile_csrf"] = "test-csrf"
        self.headers = {"X-CSRF-Token": "test-csrf"}
        self.catalog = patch.object(api, "_catalog_skill", side_effect=lambda uri:
            {"uri": URI, "label": "Python"} if uri == URI else None)
        self.catalog.start()
        self.addCleanup(self.catalog.stop)
        self.documents = {}
        self.save = patch.object(api, "_save_profile", side_effect=self.persist)
        self.save_mock = self.save.start()
        self.addCleanup(self.save.stop)
        self.load = patch.object(api, "_load_profile", side_effect=lambda owner:
            public_profile(self.documents[owner]) if owner in self.documents else None)
        self.load.start()
        self.addCleanup(self.load.stop)

    def persist(self, owner, document, *, append, confirm_existing):
        self.assertTrue(append)
        self.assertTrue(confirm_existing)
        merged, added, duplicates = append_confirmed_skills(
            self.documents.get(owner, {}), document, confirm_existing=True)
        self.documents[owner] = merged
        return {**public_profile(merged), "_added_count": added,
                "_duplicate_count": duplicates}

    def post(self, **overrides):
        return self.client.post("/api/profile/skills/confirm",
            json={"skill_uri": URI, "confirmed": True, **overrides},
            headers=self.headers)

    def test_add_is_persisted_and_uses_server_canonical_label(self):
        result = self.post(label="Fabricated qualification", evidence="invented")
        self.assertEqual(result.status_code, 200)
        self.assertTrue(result.json["added"])
        saved = self.client.get("/api/profile").json["profile"]["skills"][0]
        self.assertEqual(saved["value"], "Python")
        self.assertEqual(saved["evidence"], "")
        self.assertTrue(saved["confirmed"])
        self.assertEqual(result.json["confirmed_skills"], [{"uri": URI, "label": "Python"}])
        self.assertNotIn("proficiency", saved)

    def test_repeated_clicks_are_idempotent(self):
        self.post()
        again = self.post()
        self.assertFalse(again.json["added"])
        self.assertEqual(len(self.client.get("/api/profile").json["profile"]["skills"]), 1)

    def test_csrf_and_confirmation_are_required(self):
        no_csrf = self.client.post("/api/profile/skills/confirm",
            json={"skill_uri": URI, "confirmed": True})
        self.assertEqual(no_csrf.status_code, 403)
        for confirmed in (False, "true", None):
            self.assertEqual(self.post(confirmed=confirmed).status_code, 400)
        self.save_mock.assert_not_called()

    def test_unknown_or_invalid_identity_is_rejected(self):
        for uri in ("unknown", "", [], None, "x" * 501):
            self.assertEqual(self.post(skill_uri=uri).status_code, 400)
        self.save_mock.assert_not_called()

    def test_ownership_and_refresh(self):
        self.post()
        other = self.app.test_client()
        self.assertIsNone(other.get("/api/profile").json["profile"])
        self.assertEqual(len(self.client.get("/api/profile").json["profile"]["skills"]), 1)

    def test_pending_confirmation_preserves_all_original_data(self):
        original = {"schema_version": 2, "skills": [
            {**skill(confirmed=False), "value": "My Python work",
             "evidence": "I used Python in a project.", "origin": "explicit"},
            skill("urn:test:sql", "SQL")],
            "my_future": {"saved_occupations": ["example"]}, "private": {"keep": True}}
        before = copy.deepcopy(original)
        merged, added, _ = append_confirmed_skills(
            original, {"skills": [skill()]}, confirm_existing=True)
        self.assertEqual(added, 1)
        self.assertEqual(len(merged["skills"]), 2)
        self.assertTrue(merged["skills"][0]["confirmed"])
        for key in ("value", "evidence", "origin"):
            self.assertEqual(merged["skills"][0][key], before["skills"][0][key])
        self.assertEqual(merged["my_future"], original["my_future"])
        self.assertEqual(merged["private"], original["private"])
        self.assertEqual(original, before)

    def test_full_profile_fails_without_mutation_but_can_confirm_pending(self):
        old = {"schema_version": 2, "skills": [
            skill(f"urn:test:{i}", f"Skill {i}") for i in range(40)]}
        before = copy.deepcopy(old)
        with self.assertRaises(ProfileValidationError):
            append_confirmed_skills(old, {"skills": [skill()]}, confirm_existing=True)
        self.assertEqual(old, before)
        old["skills"][0]["confirmed"] = False
        confirmed, count, _ = append_confirmed_skills(
            old, {"skills": [skill("urn:test:0", "Skill 0")]}, confirm_existing=True)
        self.assertEqual(count, 1)
        self.assertEqual(len(confirmed["skills"]), 40)

    def test_failure_is_explicit_and_profile_limit_is_bad_request(self):
        self.save_mock.side_effect = RuntimeError("synthetic storage failure")
        response = self.post()
        self.assertEqual(response.status_code, 503)
        self.assertIn("could not be saved", response.json["error"])
        self.assertNotIn("synthetic storage", response.json["error"])
        self.save_mock.side_effect = ProfileValidationError("Remove an item first.")
        self.assertEqual(self.post().status_code, 400)

    def test_resume_append_default_does_not_auto_confirm_pending(self):
        old = {"schema_version": 2, "skills": [skill(confirmed=False)]}
        merged, added, duplicates = append_confirmed_skills(old, {"skills": [skill()]})
        self.assertFalse(merged["skills"][0]["confirmed"])
        self.assertEqual((added, duplicates), (0, 1))


if __name__ == "__main__":
    unittest.main()
