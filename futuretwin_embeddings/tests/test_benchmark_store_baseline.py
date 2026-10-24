"""Regression coverage for current benchmark baseline provenance and routing."""
from datetime import date, datetime, timezone
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import benchmark_store


def result_row(
    *,
    model_id,
    model_name,
    score,
    version="v2",
    unit="percent",
    direction="higher_better",
    current_rank=2,
    history_rank=2,
    evaluation_date=None,
    collected_at=None,
):
    return {
        "source": "livebench",
        "benchmark_name": "LiveBench",
        "benchmark_version": version,
        "domain": "Coding",
        "task": "code_generation",
        "task_text": "Generate and repair code.",
        "model_id": model_id,
        "model_name": model_name,
        "score": score,
        "score_direction": direction,
        "score_unit": unit,
        "evaluation_date": evaluation_date,
        "model_release_date": None,
        "source_url": "https://livebench.ai/",
        "collected_at": collected_at or datetime(2026, 10, 21, tzinfo=timezone.utc),
        "current_rank": current_rank,
        "history_rank": history_rank,
    }


class TestCurrentBaseline(unittest.TestCase):
    def test_groups_same_series_and_keeps_historical_results_provenance(self):
        rows = [
            result_row(
                model_id="new",
                model_name="Newest model",
                score=82.5,
                current_rank=1,
                history_rank=1,
                collected_at=datetime(2026, 10, 21, tzinfo=timezone.utc),
            ),
            result_row(
                model_id="older",
                model_name="Older model",
                score=76.25,
                current_rank=2,
                history_rank=2,
                evaluation_date=date(2026, 10, 20),
                collected_at=datetime(2026, 10, 20, tzinfo=timezone.utc),
            ),
            result_row(
                model_id="other-version",
                model_name="Other version model",
                score=10,
                version="v1",
                current_rank=1,
                history_rank=1,
            ),
        ]
        with patch.object(benchmark_store, "_rows", return_value=rows):
            measurements = benchmark_store.get_current_baseline()

        self.assertEqual(len(measurements), 2)
        latest = next(item for item in measurements if item["benchmark_version"] == "v2")
        self.assertEqual(latest["model_name"], "Newest model")
        self.assertEqual(latest["date_label"], "Record collected")
        self.assertEqual(latest["date_value"], "2026-10-21")
        self.assertEqual(latest["history"][0]["model_name"], "Older model")
        self.assertEqual(latest["history"][0]["date_label"], "Evaluation date")
        self.assertEqual(latest["source_url"], "https://livebench.ai/")
        self.assertEqual(latest["score_direction"], "higher_better")

    def test_trends_route_serves_current_baseline_html(self):
        from futuretwin_dashboard import app

        response = app.test_client().get("/trends")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Current AI Capabilities", response.data)
        # This explanatory paragraph was explicitly removed in the minimal UI.
        # Keep route coverage without requiring the deleted copy to return.
        self.assertNotIn(b"Explore how AI is developing across different fields.", response.data)
        self.assertIn(b"capability-show-more", response.data)
        self.assertIn(b'id="benchmark-evidence"', response.data)
        self.assertRegex(response.get_data(as_text=True),
                         r"<summary[^>]*>Research details for Latest AI Advances</summary>")
        self.assertIn(b"Latest AI Advances", response.data)
        self.assertIn(b"aria-expanded", response.data)
        self.assertIn(b"No new comparable improvements in the latest snapshot.", response.data)
        self.assertNotIn(b"Current AI capability baseline", response.data)

    def test_overview_api_includes_baseline_without_removing_existing_fields(self):
        from futuretwin_dashboard import app

        sample = [{
            "domain": "Coding",
            "benchmark_name": "LiveBench",
            "benchmark_version": "v2",
            "model_name": "Example model",
            "score": 82.5,
            "score_unit": "percent",
            "date_label": "Record collected",
            "date_value": "2026-10-21",
            "history": [],
        }]
        with (
            patch.object(benchmark_store, "get_domain_overview", return_value=[{"domain": "Coding"}]),
            patch.object(benchmark_store, "get_benchmark_list", return_value=[{"benchmark_name": "LiveBench"}]),
            patch.object(benchmark_store, "get_current_baseline", return_value=sample),
            patch.object(benchmark_store, "_rows", return_value=[{"n": 1}]),
        ):
            response = app.test_client().get("/api/benchmarks/overview")

        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["domains"], [{"domain": "Coding"}])
        self.assertEqual(data["benchmarks"], [{"benchmark_name": "LiveBench"}])
        self.assertEqual(data["models_total"], 1)
        self.assertEqual(data["current_measurements"], sample)


if __name__ == "__main__":
    unittest.main()
