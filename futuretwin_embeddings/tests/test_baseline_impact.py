"""Baseline impact unit tests and Flask route parity regression coverage."""
from pathlib import Path
from unittest.mock import patch
import sys
import types
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import futuretwin_baseline_impact as base

SAMPLE = {
    "source": "swebench",
    "benchmark_name": "SWE-bench Verified",
    "benchmark_version": "2026",
    "task": "software_bug_fix",
    "domain": "Coding",
    "task_text": "Resolve software bugs with code patches",
    "model_name": "ExampleModel",
    "score": 45.0,
    "score_direction": "higher_better",
    "score_unit": "percent",
    "source_url": "https://example.com/eval",
    "evaluation_date": "2026-10-01",
    "model_release_date": "",
    "collected_at": "2026-10-02T08:30:00+00:00",
    "candidates": [
        {
            "skill_uri": "esco:python",
            "skill": "use programming languages",
            "cosine_similarity": 0.58,
        },
        {
            "skill_uri": "esco:not-rel",
            "skill": "unrelated",
            "cosine_similarity": 0.88,
        },
    ],
}


class TestBaseline(unittest.TestCase):
    def setUp(self):
        api = types.ModuleType("futuretwin_occupation_api")
        api._load_esco = lambda: (
            {},
            [],
            {
                "esco:developer": {
                    "essential": [
                        {"uri": "esco:python", "label": "programming"}
                    ],
                    "optional": [],
                },
                "esco:unrelated": {
                    "essential": [
                        {"uri": "esco:other", "label": "unrelated skill"}
                    ],
                    "optional": [],
                },
            },
        )
        self.original = sys.modules.get("futuretwin_occupation_api")
        sys.modules["futuretwin_occupation_api"] = api

    def tearDown(self):
        if self.original is None:
            sys.modules.pop("futuretwin_occupation_api", None)
        else:
            sys.modules["futuretwin_occupation_api"] = self.original

    def test_baseline_works_without_advancement_events(self):
        with patch.object(base, "_task_skill_candidates", return_value=(SAMPLE,)):
            result = base.get_occupation_baseline("esco:developer")
        self.assertEqual(result["status"], "possible_links")
        self.assertEqual(result["basis"], "current_benchmark_baseline")
        self.assertEqual(len(result["links"]), 1)
        self.assertEqual(result["links"][0]["skill_uri"], "esco:python")
        self.assertEqual(len(result["task_groups"]), 1)
        group = result["task_groups"][0]
        self.assertEqual(group["task"], SAMPLE["task_text"])
        self.assertEqual(group["model"], "ExampleModel")
        self.assertEqual(group["score"], 45.0)
        self.assertEqual(group["score_direction"], "higher_better")
        self.assertEqual(group["date_label"], "Evaluation date")
        self.assertEqual(group["date_value"], "2026-10-01")
        self.assertEqual(group["relationship_type"], "semantic_candidate")
        self.assertFalse(group["independently_verified"])
        self.assertNotIn("classification", group)

    def test_groups_skills_under_task_and_separates_distinct_tasks(self):
        api = sys.modules["futuretwin_occupation_api"]
        occupation_skills = {
            "essential": [
                {"uri": "esco:python", "label": "programming"},
                {"uri": "esco:datasets", "label": "create data sets"},
                {"uri": "esco:unstructured", "label": "work with unstructured data"},
            ],
            "optional": [],
        }
        first = {
            **SAMPLE,
            "candidates": [
                {"skill_uri": "esco:python", "skill": "programming", "cosine_similarity": 0.58},
                {"skill_uri": "esco:datasets", "skill": "create data sets", "cosine_similarity": 0.51},
                {"skill_uri": "esco:unstructured", "skill": "work with unstructured data", "cosine_similarity": 0.43},
            ],
        }
        second = {
            **first,
            "task": "another_task",
            "task_text": "Prepare a separate software testing report",
        }
        with (
            patch.object(
                api,
                "_load_esco",
                return_value=({}, [], {"esco:developer": occupation_skills}),
            ),
            patch.object(base, "_task_skill_candidates", return_value=(first, second)),
        ):
            result = base.get_occupation_baseline("esco:developer")

        self.assertEqual(len(result["task_groups"]), 2)
        grouped = next(group for group in result["task_groups"]
                       if group["benchmark_task_id"] == "software_bug_fix")
        self.assertEqual(
            {skill["skill_uri"] for skill in grouped["skills"]},
            {"esco:python", "esco:datasets", "esco:unstructured"},
        )
        self.assertTrue(all(
            skill["relationship_type"] == "semantic_candidate"
            and not skill["independently_verified"]
            for skill in grouped["skills"]
        ))

    def test_record_collection_date_is_not_mislabeled_as_evaluation_date(self):
        api = sys.modules["futuretwin_occupation_api"]
        no_eval_date = {
            **SAMPLE,
            "evaluation_date": None,
            "model_release_date": None,
            "collected_at": "2026-10-02T08:30:00+00:00",
        }
        with (
            patch.object(base, "_task_skill_candidates", return_value=(no_eval_date,)),
            patch.object(
                api,
                "_load_esco",
                return_value=(
                    {},
                    [],
                    {"esco:developer": {
                        "essential": [{"uri": "esco:python", "label": "programming"}],
                        "optional": [],
                    }},
                ),
            ),
        ):
            result = base.get_occupation_baseline("esco:developer")

        group = result["task_groups"][0]
        self.assertEqual(group["evaluation_date"], "")
        self.assertEqual(group["date_label"], "Record collected")
        self.assertEqual(group["date_value"], "2026-10-02")

    def test_no_overlap_does_not_claim_no_impact(self):
        with patch.object(base, "_task_skill_candidates", return_value=(SAMPLE,)):
            result = base.get_occupation_baseline("esco:unrelated")
        self.assertEqual(result["status"], "not_enough_data")
        self.assertIn("does not mean AI has no effect", result["note"])

    def test_missing_benchmark_records(self):
        with patch.object(base, "_task_skill_candidates", return_value=()):
            result = base.get_occupation_baseline("esco:developer")
        self.assertEqual(result["status"], "not_enough_data")

    def test_local_inference_failure_reported_as_unavailable(self):
        with patch.object(
            base, "_task_skill_candidates", side_effect=RuntimeError("fake")
        ):
            result = base.get_occupation_baseline("esco:developer")
        self.assertEqual(result["status"], "unavailable")
        self.assertNotIn("fake", result["note"])


class TestOccupationExploreApiParity(unittest.TestCase):
    def test_flask_response_matches_direct_occupation_result(self):
        import futuretwin_occupation_api as occupation_api
        from futuretwin_dashboard import app

        uri = "http://data.europa.eu/esco/occupation/f2b15a0e-e65a-438a-affb-29b9d50b77d1"
        occupations = {
            uri: {
                "uri": uri,
                "label": "software developer",
                "isco_group": "2512",
                "description": "Develops and maintains software.",
            }
        }
        skills = {
            uri: {
                "essential": [
                    {"uri": "esco:programming", "label": "programming"}
                ],
                "optional": [],
            }
        }
        ai_impact = {
            "status": "possible_links",
            "basis": "current_benchmark_baseline",
            "benchmark_tasks_considered": 36,
            "links": [
                {
                    "benchmark": f"Benchmark {index + 1}",
                    "skill": f"Skill {index + 1}",
                    "task": f"Task evidence {index + 1}",
                }
                for index in range(6)
            ],
            "task_groups": [
                {
                    "task": "Task evidence",
                    "benchmark": "Benchmark",
                    "skills": [{"skill": "Skill", "skill_uri": "esco:programming"}],
                    "relationship_type": "semantic_candidate",
                    "independently_verified": False,
                }
            ],
            "note": "Baseline evidence; not a job-loss prediction.",
        }
        job_demand = {
            "status": "not_enough_data",
            "note": "No recent group-level figure is available.",
        }

        with (
            patch.object(
                occupation_api,
                "_load_esco",
                return_value=(occupations, [], skills),
            ),
            patch.object(
                occupation_api, "_occupation_ai_evidence", return_value=ai_impact
            ),
            patch.object(
                occupation_api,
                "_occupation_market_context",
                return_value=job_demand,
            ),
        ):
            direct = occupation_api.explore_occupation(uri)
            response = app.test_client().get(
                "/api/occupations/explore", query_string={"uri": uri}
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), direct)
        self.assertEqual(response.get_json()["ai_impact"]["status"], "possible_links")
        self.assertEqual(len(response.get_json()["ai_impact"]["links"]), 6)


if __name__ == "__main__":
    unittest.main()
