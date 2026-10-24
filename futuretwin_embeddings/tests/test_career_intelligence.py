"""Synthetic boundary fixtures; actual CPU predictions are verified separately."""
import unittest
from unittest.mock import patch

from flask import Flask
from futuretwin_intelligence import (
    comparable_benchmark_series, comparison_status, posting_growth,
    ranking_metadata, score_change, safe_url,
)
from futuretwin_intelligence_api import register_intelligence_routes
from futuretwin_opportunities import build_opportunities, explicit_quote
from futuretwin_my_future import _coverage


class MeasureTests(unittest.TestCase):
    def test_equal_duration_cohorts_and_missing_prior_sample(self):
        from datetime import date
        import jobmarket_trends as trends
        bounds = trends._window_bounds([date(2026, 1, 31)])
        recent = date.fromisoformat(bounds["recent_end"]) - date.fromisoformat(bounds["recent_start"])
        prior = date.fromisoformat(bounds["prior_end"]) - date.fromisoformat(bounds["prior_start"])
        self.assertEqual(recent.days + 1, 28)
        self.assertEqual(prior.days + 1, 28)
        with patch.object(trends, "get_posting_dates", return_value=[{"posted_date": date(2026, 1, 31)}] * 6), \
                patch.object(trends, "get_skill_mentions", return_value=[
                    {"posted_date": date(2026, 1, 31), "skill": "test-skill", "cosine_similarity": .9}
                ] * 6):
            report = trends.compute_skill_trends()
        self.assertIsNone(report["observed_sample_skills"][0]["share_prior_pct"])
        self.assertIsNone(report["observed_sample_skills"][0]["share_delta_pp"])
        self.assertEqual(report["rising"], [])
        self.assertEqual(report["declining"], [])

    def test_distinct_skill_coverage_and_breakdowns(self):
        cov = _coverage(3, 10, essential=(2, 4), optional=(1, 6))
        self.assertEqual(cov["percentage"], 30)
        self.assertEqual(cov["essential"]["percentage"], 50)
        self.assertAlmostEqual(cov["optional"]["percentage"], 100 / 6)
        self.assertIsNone(_coverage(0, 0)["percentage"])

    def test_percentage_points_are_not_relative_percent(self):
        result = score_change(40, 60, "percent", "higher_better")
        self.assertEqual(result["absolute_change"], 20)
        self.assertEqual(result["absolute_change_unit"], "percentage points")
        self.assertEqual(result["relative_change_pct"], 50)

    def test_lower_is_better_and_zero_baseline(self):
        result = score_change(50, 30, "milliseconds", "lower_better")
        self.assertEqual(result["absolute_change"], -20)
        self.assertEqual(result["improvement_direction"], "improved")
        self.assertIsNone(score_change(0, 3, "points", "higher_better")["relative_change_pct"])
        with self.assertRaises(ValueError):
            score_change(float("nan"), 1, "points", "higher_better")

    def test_hiring_requires_comparability_and_nonzero_baseline(self):
        self.assertIsNone(posting_growth(0, 10, comparable=True))
        self.assertIsNone(posting_growth(10, 20))
        self.assertEqual(posting_growth(10, 15, comparable=True), 50)
        self.assertIsNone(posting_growth(-1, 15, comparable=True))

    def test_unknown_sort_falls_back_and_is_never_zero_exposure(self):
        with patch("futuretwin_ranking_evidence.ranking_evidence", return_value={
            "labels": {"training_label_contract_verified": False, "reason": "Unverified"},
            "tasks": {"eligible_occupation_count": 0}, "vacancies": {},
        }):
            result = ranking_metadata("lower_exposure")
        self.assertEqual(result["effective"], "best_match")
        self.assertTrue(result["fallback_reason"])
        self.assertFalse(result["options"][0]["available"])
        self.assertEqual(ranking_metadata("growing_jobs")["effective"], "best_match")
        with self.assertRaises(ValueError):
            ranking_metadata("future_safety")

    def test_source_links_reject_non_http_and_embedded_credentials(self):
        self.assertEqual(safe_url("javascript:alert(1)"), "")
        self.assertEqual(safe_url("https://username@example.com"), "")
        self.assertEqual(safe_url("https://example.com/data"), "https://example.com/data")


class BenchmarkTests(unittest.TestCase):
    identity = ("test-source", "test-benchmark", "v1", "task-a")

    def rows(self):
        return [
            {
                "source": "test-source", "benchmark_name": "test-benchmark",
                "benchmark_version": "v1", "task": "task-a", "score_unit": "percent",
                "score_direction": "higher_better", "model_name": model,
                "source_url": "https://example.com/results", "score": value,
                "evaluation_date": when, "raw_metadata": {"protocol": "fixed-test-set-v1"},
            }
            for model, value, when in [
                ("test-model-old", 40, "2025-01-01"), ("test-model-new", 60, "2025-03-01")
            ]
        ]

    def test_comparable_protocol_frontier_with_actual_dates(self):
        series = comparable_benchmark_series(self.rows(), {self.identity})
        self.assertEqual(len(series), 1)
        self.assertEqual(series[0]["absolute_change"], 20)
        self.assertEqual(series[0]["points"][1]["model"], "test-model-new")
        self.assertEqual(series[0]["occupation_relationship"], "semantic_candidate")

    def test_missing_protocol_or_actual_dates_cannot_form_trend(self):
        for field, value in [("evaluation_date", None), ("raw_metadata", {})]:
            rows = self.rows()
            rows[1][field] = value
            self.assertEqual(comparable_benchmark_series(rows, {self.identity}), [])

    def test_versions_units_protocols_and_directions_never_mix(self):
        for field, value in [
            ("benchmark_version", "v2"), ("score_unit", "points"),
            ("raw_metadata", {"protocol": "different-protocol"}),
            ("score_direction", "lower_better"),
        ]:
            rows = self.rows()
            rows[1][field] = value
            self.assertEqual(comparable_benchmark_series(rows, {self.identity}), [])

    def test_collection_date_migration_is_not_evaluation_history(self):
        rows = self.rows()
        rows[1]["raw_metadata"]["migrated_from"] = "ai_benchmark_measurements"
        self.assertEqual(comparable_benchmark_series(rows, {self.identity}), [])


class OpportunityTests(unittest.TestCase):
    def setUp(self):
        self.occupations = {
            "career:a": {"label": "AI specialist", "aliases": []},
            "career:b": {"label": "Data analyst", "aliases": []},
        }
        self.relations = {
            uri: {"essential": [{"uri": "skill:python", "label": "Python (computer programming)"},
                                {"uri": "skill:sql", "label": "SQL"}], "optional": []}
            for uri in self.occupations
        }
        self.ads = [
            {"source": "sample", "source_posting_id": "1", "title": "AI specialist",
             "description_text": "Use Python and SQL to test reports.", "url": "https://example.com/job",
             "posted_date": "2026-01-01", "collected_at": "2026-01-02"},
            {"source": "sample", "source_posting_id": "2", "title": "Unrelated role",
             "description_text": "No named programming terms.", "url": "javascript:alert(1)",
             "posted_date": "2026-01-01", "collected_at": "2026-01-02"},
        ]
        self.mentions = [
            {"source": "sample", "source_posting_id": ad, "skill_uri": uri,
             "skill": label, "cosine_similarity": .99}
            for ad in ("1", "2")
            for uri, label in [("skill:python", "Python"), ("skill:sql", "SQL")]
        ]

    def test_similarity_alone_does_not_establish_named_skill(self):
        self.assertIsNone(explicit_quote("SQL", "SQLAlchemy is installed."))
        self.assertTrue(explicit_quote("Python (computer programming)", "We use Python."))
        radar = build_opportunities(self.ads, self.mentions, self.occupations, self.relations)
        self.assertTrue(radar["skills"])
        self.assertTrue(all(s["sample_mentions"] == 1 for s in radar["skills"]))
        self.assertTrue(all(s["sample_share_pct"] == 50 for s in radar["skills"]))

    def test_candidate_is_not_new_or_growing_because_title_contains_ai(self):
        radar = build_opportunities(self.ads, self.mentions, self.occupations, self.relations)
        self.assertEqual(radar["jobs"][0]["category"], "direct_title_match")
        self.assertIsNone(radar["jobs"][0]["hiring_trend"]["growth_pct"])
        self.assertFalse(radar["coverage"]["longitudinal_comparison_supported"])
        self.assertTrue(all(s["demand_change_pp"] is None for s in radar["skills"]))

    def test_skill_related_careers_are_separate_from_title_matched_postings(self):
        radar = build_opportunities(
            self.ads, self.mentions, self.occupations, self.relations
        )
        self.assertEqual([item["uri"] for item in radar["job_postings"]], ["career:a"])
        self.assertEqual(
            [item["uri"] for item in radar["skill_related_careers"]], ["career:b"]
        )
        self.assertTrue(radar["skill_related_careers"][0]["not_a_job_opening"])
        self.assertEqual(radar["counts"]["title_matched_ad_count"], 1)
        self.assertEqual(radar["counts"]["skill_related_career_candidate_count"], 1)
        self.assertEqual(radar["counts"]["supported_esco_occupation_count"], 2)

    def test_evidence_keeps_source_date_location_and_matching_method(self):
        self.ads[0].update(location="Remote", country="Worldwide", remote=True)
        radar = build_opportunities(
            self.ads, self.mentions, self.occupations, self.relations
        )
        evidence = radar["job_postings"][0]["evidence"][0]
        self.assertEqual(evidence["source"], "sample")
        self.assertEqual(evidence["posted_date"], "2026-01-01")
        self.assertEqual(evidence["location"], "Remote")
        self.assertEqual(
            evidence["matching_method"],
            "Normalized exact match to ESCO preferred occupation title",
        )
        skill_evidence = radar["skills"][0]["evidence"][0]
        self.assertIn("literal term found", skill_evidence["matching_method"])

    def test_repeated_mentions_do_not_exceed_distinct_ad_denominator(self):
        radar = build_opportunities(self.ads, self.mentions * 3, self.occupations, self.relations)
        self.assertTrue(all(s["sample_mentions"] == 1 for s in radar["skills"]))
        self.assertTrue(all(s["related_careers"] for s in radar["skills"]))

    def test_empty_source_does_not_create_fake_cards(self):
        radar = build_opportunities([], [], self.occupations, self.relations)
        self.assertEqual(radar["status"], "not_enough_data")
        self.assertEqual(radar["jobs"], [])
        self.assertEqual(radar["skills"], [])

    def test_generic_alias_without_domain_skills_cannot_identify_career(self):
        self.occupations["career:a"]["aliases"] = ["Principal Engineer"]
        self.ads[0].update(title="Principal Engineer", description_text="A generic engineering vacancy.")
        radar = build_opportunities(self.ads, [], self.occupations, self.relations)
        self.assertEqual(radar["jobs"], [])


class ComparisonTests(unittest.TestCase):
    def exposure(self, status="available", fingerprint="test-method"):
        return {"task_exposure": {
            "status": status, "classified_task_count": 10,
            "task_coverage_percentage": 100,
            "model": {"prediction_fingerprint": fingerprint},
            "source": {"version": "test-version", "asset_sha256": "test-source-hash"},
        }}

    def test_only_exact_complete_same_method_inventories_are_comparable(self):
        self.assertTrue(comparison_status([self.exposure(), self.exposure()])["class_distributions_comparable"])
        self.assertFalse(comparison_status([self.exposure(), self.exposure("uncertain_mapping")])["class_distributions_comparable"])
        self.assertFalse(comparison_status([self.exposure(), self.exposure(fingerprint="other-method")])["class_distributions_comparable"])
        self.assertFalse(comparison_status([self.exposure(), self.exposure()])["combined_exposure_allowed"])

    def test_compare_api_rejects_duplicate_unknown_or_excessive_identifiers(self):
        app = Flask(__name__)
        register_intelligence_routes(app)
        client = app.test_client()
        for query in ["uri=a", "uri=a&uri=a", "uri=a&uri=b&uri=c&uri=d&uri=e"]:
            self.assertEqual(client.get("/api/my-future/compare?" + query).status_code, 400)
        with patch("futuretwin_occupation_api.get_esco_occupation_catalog", return_value=({}, [], {})):
            self.assertEqual(client.get("/api/my-future/compare?uri=a&uri=b").status_code, 404)

    def test_opportunity_api_limits(self):
        app = Flask(__name__)
        register_intelligence_routes(app)
        client = app.test_client()
        for value in ["0", "31", "not-a-number"]:
            self.assertEqual(client.get("/api/my-future/opportunities?limit=" + value).status_code, 400)


if __name__ == "__main__":
    unittest.main()
