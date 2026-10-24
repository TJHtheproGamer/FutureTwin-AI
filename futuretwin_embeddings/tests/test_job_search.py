import unittest
from unittest.mock import patch

from futuretwin_job_search import search_job_postings


class JobSearchTests(unittest.TestCase):
    def test_exact_passport_mentions_rank_first_without_claiming_missing_skills(self):
        rows = [
            {
                "source": "himalayas", "source_posting_id": "one",
                "title": "Designer", "employer": "Example", "url": "https://example.org/one",
                "posted_date": "2026-10-23", "explicit_skills": [],
                "remote": True, "location": "Malaysia",
                "description": "Company introduction: create an account to apply.",
            },
            {
                "source": "himalayas", "source_posting_id": "two",
                "title": "Analyst", "employer": "Example", "url": "https://example.org/two",
                "posted_date": "2026-10-22",
                "explicit_skills": [{"uri": "skill:1", "label": "Python",
                                     "evidence_quote": "Python required"}],
                "remote": True, "location": "Malaysia",
            },
        ]
        passport = {"skill:1": {"label": "Python"}, "skill:2": {"label": "Writing"}}
        with patch("futuretwin_job_search._posting_rows", return_value=rows), \
                patch("futuretwin_job_search.get_esco_occupation_catalog",
                      return_value=({}, {}, {})):
            result = search_job_postings(confirmed_skills=passport)
            filtered = search_job_postings(
                confirmed_skills=passport, skill_uri="skill:1", workplace="remote")
            incidental = search_job_postings(q="account")
            title_search = search_job_postings(q="analyst")
        self.assertEqual(result["postings"][0]["source_posting_id"], "two")
        self.assertEqual(result["postings"][0]["confirmed_skill_match_count"], 1)
        self.assertEqual(result["postings"][0]["passport_skills_not_mentioned"],
                         [{"uri": "skill:2", "label": "Writing"}])
        self.assertNotIn("missing_skills", result["postings"][0])
        self.assertEqual(filtered["count"], 1)
        self.assertEqual(incidental["count"], 0)
        self.assertEqual(title_search["count"], 1)


if __name__ == "__main__":
    unittest.main()
