"""Synthetic-only tests: no provider calls, real personal data or audio uploads."""
import os
import sys
import unittest
from pathlib import Path
from io import BytesIO
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from flask import Flask
import futuretwin_resume_api as api
from futuretwin_transcription import VoiceRequestError
from futuretwin_skills_profile import (
    ProfileValidationError, append_confirmed_skills, clean_user_profile,
)


def match(value, top_k=3):
    return [{"skill_uri": "esco:python" if "python" in value.lower() else "esco:sql",
             "skill": "Python" if "python" in value.lower() else "SQL"}]


def skill(value="Python", uri="esco:python", **extra):
    return {"value": value, "evidence": f"I used {value}.", "origin": "explicit",
            "source": "experience", "confirmed": True, "selected_esco_uri": uri,
            "esco_candidates": [{"uri": uri, "label": value}], **extra}


class AppendAndPrivacyTests(unittest.TestCase):
    def test_preserves_existing_and_skips_duplicates_by_identity_and_wording(self):
        old = {"schema_version": 2, "skills": [skill()], "_legacy_profile": {"private": "retained"}}
        result, added, duplicates = append_confirmed_skills(old, {
            "skills": [skill("python"), skill("Python programming"), skill("SQL", "esco:sql")]
        })
        self.assertEqual((added, duplicates), (1, 2))
        self.assertEqual(result["skills"][0], old["skills"][0])
        self.assertEqual(result["_legacy_profile"], old["_legacy_profile"])
        self.assertEqual(len(old["skills"]), 1)

    def test_legacy_data_archived_without_erasing_skills(self):
        old = {"skills": [{"value": "Python"}], "education": [{"value": "private"}]}
        result, added, _ = append_confirmed_skills(old, {"skills": [skill("SQL", "esco:sql")]})
        self.assertEqual(added, 1)
        self.assertEqual(result["_legacy_profile"], old)
        self.assertEqual(len(result["skills"]), 2)

    def test_pending_experience_cannot_be_saved_through_generic_endpoint(self):
        with self.assertRaises(ProfileValidationError):
            clean_user_profile({"skills": [skill(confirmed=False)]}, match)

    def test_quotes_require_explicit_consent(self):
        for consent, expected in ((False, ""), (True, "I used Python.")):
            result = clean_user_profile({"skills": [skill(evidence_consent=consent)]}, match)
            self.assertEqual(result["skills"][0]["evidence"], expected)
            self.assertEqual(result["skills"][0]["source"], "experience")
        result = clean_user_profile({"skills": [skill(evidence_consent="true")]}, match)
        self.assertEqual(result["skills"][0]["evidence"], "")

    def test_profile_limit_fails_atomically(self):
        old = {"schema_version": 2, "skills": [
            skill(f"skill-{i}", f"esco:{i}") for i in range(40)
        ]}
        with self.assertRaises(ProfileValidationError):
            append_confirmed_skills(old, {"skills": [skill()]})
        self.assertEqual(len(old["skills"]), 40)


class ExperienceRouteTests(unittest.TestCase):
    def setUp(self):
        self.env = patch.dict(os.environ, {"SESSION_SECRET": "synthetic-voice-tests-only"})
        self.env.start()
        self.addCleanup(self.env.stop)
        self.app = Flask(__name__)
        api.register_resume_routes(self.app)
        self.client = self.app.test_client()
        with self.client.session_transaction() as sess:
            sess["ft_profile_csrf"] = "test-csrf"
        self.headers = {"X-CSRF-Token": "test-csrf"}

    def post(self, path="/api/profile/experience", **payload):
        return self.client.post(path, json=payload, headers=self.headers)

    def test_voice_capabilities_advertise_local_transcription_and_validate_consent(self):
        capability = self.client.get("/api/profile/voice")
        self.assertTrue(capability.json["transcription_available"])
        self.assertEqual(capability.json["provider"], "self-hosted faster-whisper")
        self.assertEqual(set(capability.json["languages"]), {"en", "ms", "zh", "auto"})
        response = self.client.post("/api/profile/voice", data={"language": "en"})
        self.assertEqual(response.status_code, 403)
        response = self.client.post("/api/profile/voice", data={"consent": "false"},
                                    headers=self.headers)
        self.assertEqual(response.status_code, 400)
        self.assertIn("no-store", response.headers["Cache-Control"])

    def post_voice(self, audio=b"synthetic audio", mime="audio/webm", language="en", consent="true"):
        return self.client.post(
            "/api/profile/voice",
            data={
                "consent": consent,
                "language": language,
                "audio": (BytesIO(audio), "recording.webm", mime),
            },
            content_type="multipart/form-data",
            headers=self.headers,
        )

    def test_voice_transcribes_in_temporary_storage_and_deletes_audio(self):
        seen = {}

        def fake_transcribe(path, language):
            path = Path(path)
            self.assertTrue(path.exists())
            seen.update(path=path, contents=path.read_bytes(), language=language)
            return {"transcript": "I helped customers and trained new staff.", "language": "en"}

        with patch("futuretwin_experience_api.validate_audio_file", return_value=12.0), \
             patch("futuretwin_experience_api.transcribe_audio_file", side_effect=fake_transcribe):
            response = self.post_voice(audio=b"synthetic webm bytes")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["transcript"], "I helped customers and trained new staff.")
        self.assertFalse(response.json["audio_retained"])
        self.assertEqual(seen["contents"], b"synthetic webm bytes")
        self.assertEqual(seen["language"], "en")
        self.assertFalse(seen["path"].exists())
        self.assertIn("no-store", response.headers["Cache-Control"])

    def test_voice_validates_size_language_format_and_duration(self):
        self.assertEqual(self.post_voice(language="xx").status_code, 400)
        self.assertEqual(self.post_voice(mime="video/webm").status_code, 415)
        self.assertEqual(self.post_voice(audio=b"x" * (8 * 1024 * 1024 + 1)).status_code, 413)
        with patch("futuretwin_experience_api.validate_audio_file",
                   side_effect=VoiceRequestError("Recordings must be 2 minutes or shorter.", 413)):
            response = self.post_voice()
        self.assertEqual(response.status_code, 413)
        self.assertIn("2 minutes", response.json["error"])

    def test_voice_model_errors_are_generic_and_audio_is_deleted(self):
        seen = {}

        def fail_transcribe(path, _language):
            seen["path"] = Path(path)
            raise RuntimeError("private transcript and model details")

        with patch("futuretwin_experience_api.validate_audio_file", return_value=1.0), \
             patch("futuretwin_experience_api.transcribe_audio_file", side_effect=fail_transcribe):
            response = self.post_voice()
        self.assertEqual(response.status_code, 503)
        self.assertNotIn("private transcript", response.text)
        self.assertFalse(seen["path"].exists())

    def test_voice_rate_limit_is_per_browser_session(self):
        import time
        with self.client.session_transaction() as sess:
            sess["ft_voice_transcribe_times"] = [time.time()] * 5
        with patch("futuretwin_experience_api.validate_audio_file") as validate, \
             patch("futuretwin_experience_api.transcribe_audio_file") as transcribe:
            response = self.post_voice()
        self.assertEqual(response.status_code, 429)
        validate.assert_not_called()
        transcribe.assert_not_called()

    def test_csrf_consent_and_text_limits(self):
        self.assertEqual(self.client.post("/api/profile/experience", json={}).status_code, 403)
        self.assertEqual(self.post(transcript="Python", consent=False).status_code, 400)
        self.assertEqual(self.post(transcript="  ", consent=True).status_code, 400)
        self.assertEqual(self.post(transcript=7, consent=True).status_code, 400)
        self.assertEqual(self.post(transcript="a" * 12001, consent=True).status_code, 413)
        self.assertEqual(self.post("/api/profile/experience/save", skills=[], consent=True).status_code, 400)

    def test_extraction_is_grounded_pending_and_never_saved(self):
        raw = {"explicit_skills": [
            {"value": "Python", "evidence": "I used Python."},
            {"value": "invented", "evidence": "invented"},
        ], "work_activities": []}
        with patch.object(api, "_extract_skills_local", return_value=raw) as llm, \
             patch("futuretwin_skill_api.match_skills", side_effect=match), \
             patch.object(api, "_save_profile") as save:
            response = self.post(transcript="I used Python.", consent=True)
        self.assertEqual(response.status_code, 200)
        rows = response.json["draft"]["skills"]
        self.assertEqual(len(rows), 1)
        self.assertFalse(rows[0]["confirmed"])
        self.assertFalse(rows[0]["evidence_consent"])
        self.assertEqual(rows[0]["evidence"], "I used Python.")
        llm.assert_called_once_with("I used Python.", "experience")
        save.assert_not_called()
        with self.client.session_transaction() as sess:
            self.assertNotIn("Python", str(dict(sess)))

    def test_extraction_uses_local_minilm_candidates_without_saving(self):
        raw = {"explicit_skills": [
            {"value": "Python", "evidence": "I use Python to automate reports."},
        ], "work_activities": []}
        with patch.object(api, "_extract_skills_local", return_value=raw) as llm, \
             patch.object(api, "_save_profile") as save:
            response = self.post(transcript="I use Python to automate reports.", consent=True)
        self.assertEqual(response.status_code, 200)
        rows = response.json["draft"]["skills"]
        self.assertEqual(len(rows), 1)
        self.assertFalse(rows[0]["confirmed"])
        self.assertTrue(rows[0]["esco_candidates"])
        self.assertEqual(rows[0]["esco_candidates"][0]["label"], "Python (computer programming)")
        self.assertTrue(rows[0]["esco_candidates"][0]["uri"].startswith("http"))
        llm.assert_called_once_with("I use Python to automate reports.", "experience")
        save.assert_not_called()

    def test_provider_error_does_not_expose_transcript_or_error_detail(self):
        with patch.object(api, "_extract_skills_local", side_effect=RuntimeError("sensitive marker")):
            response = self.post(transcript="I used Python.", consent=True)
        self.assertEqual(response.status_code, 502)
        self.assertNotIn("sensitive marker", response.text)
        self.assertNotIn("Python", response.text)

    def test_rate_limit(self):
        with self.client.session_transaction() as sess:
            import time
            sess["ft_experience_extract_times"] = [time.time()] * 5
        self.assertEqual(self.post(transcript="Python", consent=True).status_code, 429)

    def test_save_rejects_unconfirmed_rows(self):
        response = self.post("/api/profile/experience/save", skills=[skill(confirmed=False)], consent=True)
        self.assertEqual(response.status_code, 400)

    def test_save_uses_additive_mode_and_drops_quotes_and_unknown_fields(self):
        with patch("futuretwin_skill_api.match_skills", side_effect=match), \
             patch.object(api, "_save_profile", return_value={
                 "skills": [], "_added_count": 1, "_duplicate_count": 0,
             }) as save:
            response = self.post("/api/profile/experience/save", skills=[skill()],
                                 consent=True, transcript="never store this", save_quotes=False)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["added_count"], 1)
        profile = save.call_args.args[1]
        self.assertNotIn("transcript", profile)
        self.assertEqual(profile["skills"][0]["evidence"], "")
        self.assertTrue(save.call_args.kwargs["append"])

    def test_transactional_append_encrypts_preserved_and_new_skills(self):
        connection = MagicMock()
        connection.__enter__.return_value = connection
        old = {"schema_version": 2, "skills": [skill()]}
        connection.execute.return_value.fetchone.side_effect = [
            (api._encrypt_profile(old),), (None, None),
        ]
        with patch.object(api, "_database_connection", return_value=connection):
            result = api._save_profile(b"x" * 32, {"skills": [skill("SQL", "esco:sql")]}, append=True)
        calls = connection.execute.call_args_list
        self.assertIn("pg_advisory_xact_lock", calls[0].args[0])
        stored = api._decrypt_profile(calls[2].args[1][2])
        self.assertEqual([row["value"] for row in stored["skills"]], ["Python", "SQL"])
        self.assertEqual(result["_added_count"], 1)


if __name__ == "__main__":
    unittest.main()
