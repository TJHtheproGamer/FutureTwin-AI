import unittest
from unittest.mock import patch

import numpy as np

from futuretwin_job_matching import (
    classify_semantic_candidates,
    exact_title_matches,
    normalize_title,
    semantic_candidates_batch,
    _signature,
)
from futuretwin_job_text import plain_job_text, relevant_responsibilities
from jobmarket_store import content_hash


class JobOccupationMatchingTests(unittest.TestCase):
    def test_escaped_html_and_company_intro_do_not_replace_duties(self):
        text = "&lt;h2&gt;About us&lt;/h2&gt;Employer boilerplate." \
               "&lt;h2&gt;What you'll do&lt;/h2&gt;&lt;p&gt;Build data pipelines.&lt;/p&gt;"
        self.assertNotIn("<h2>", plain_job_text(text))
        self.assertIn("Build data pipelines", relevant_responsibilities(text))
        self.assertNotIn("Employer boilerplate", relevant_responsibilities(text))

    def test_signature_is_stable_with_unordered_skill_sets(self):
        a = [{"skills": {"a", "b"}}]
        b = [{"skills": {"b", "a"}}]
        self.assertEqual(_signature("model", a), _signature("model", b))

    def test_different_locations_or_duties_are_not_collapsed(self):
        intro = "Same company introduction. " * 100
        self.assertNotEqual(
            content_hash("Engineer", "Company", intro + "Build pipes", "London"),
            content_hash("Engineer", "Company", intro + "Build roads", "London"),
        )
        self.assertNotEqual(
            content_hash("Engineer", "Company", intro, "London"),
            content_hash("Engineer", "Company", intro, "Paris"),
        )

    def test_normalizes_seniority_and_title_levels_without_rewriting_role(self):
        self.assertEqual(
            normalize_title("Senior Software Engineer II"),
            "software engineer",
        )
        self.assertEqual(
            normalize_title("Lead, Computer Vision Engineer"),
            "computer vision engineer",
        )
        self.assertEqual(
            normalize_title("Artificial Intelligence Engineer"),
            "artificial intelligence engineer",
        )

    def test_exact_match_accepts_preferred_and_alternate_title(self):
        occupations = {
            "esco:1": {
                "label": "software developer",
                "aliases": ["software engineer"],
            },
        }
        preferred = exact_title_matches("Senior Software Developer", occupations)
        alternate = exact_title_matches("Software Engineer", occupations)
        self.assertEqual(preferred[0]["method"], "normalized_exact_preferred_title")
        self.assertEqual(alternate[0]["method"], "normalized_exact_alternate_title")

    def test_semantic_candidates_use_local_embedding_rank_and_skill_evidence(self):
        class FakeModel:
            def encode(self, _texts, **_kwargs):
                return np.asarray([[1.0, 0.0]], dtype=np.float32)

        rows = [
            {"uri": "esco:1", "label": "A", "skill_uris": {
                "essential": {"skill:1"}, "optional": set()}},
            {"uri": "esco:2", "label": "B", "skill_uris": {
                "essential": set(), "optional": set()}},
            {"uri": "esco:3", "label": "C", "skill_uris": {
                "essential": set(), "optional": set()}},
        ]
        vectors = np.asarray([[0.8, 0.6], [0.9, 0.1], [0.2, 0.9]], dtype=np.float32)
        with patch("futuretwin_job_matching.load_occupation_index",
                   return_value=(FakeModel(), rows, vectors, "test-signature")):
            result, signature = semantic_candidates_batch(
                [{
                    "source": "himalayas", "source_posting_id": "job-1",
                    "title": "Engineer", "description_text": "Build computer vision systems",
                }],
                {("himalayas", "job-1"): {
                    "skill:1": {"uri": "skill:1", "label": "machine learning"},
                }},
            )
        self.assertEqual(signature, "test-signature")
        self.assertEqual([row["uri"] for row in result[0]], ["esco:2", "esco:1", "esco:3"])
        self.assertEqual(result[0][1]["supporting_skill_uris"], ["skill:1"])

    def test_uncalibrated_candidates_fail_closed_as_uncertain(self):
        candidates = [
            {"uri": "esco:1", "cosine_similarity": 0.8},
            {"uri": "esco:2", "cosine_similarity": 0.7},
        ]
        with patch("futuretwin_job_matching.thresholds", return_value=None):
            classified = classify_semantic_candidates(candidates)
        self.assertTrue(all(row["status"] == "uncertain" for row in classified))


if __name__ == "__main__":
    unittest.main()
