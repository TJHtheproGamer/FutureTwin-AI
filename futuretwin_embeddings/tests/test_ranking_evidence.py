"""Evidence boundaries and offline public-source import; never calls model inference."""
import csv
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from futuretwin_ranking_evidence import (
    DATA, career_ranking_eligibility, label_audit, load_vacancy_rows,
    ranking_evidence, export_eligibility,
)
from import_dosm_vacancies import GROUPS, extract_quarters, import_history


class LabelLineageTests(unittest.TestCase):
    def test_missing_or_corrupt_audit_is_fail_closed_not_a_recommendation_crash(self):
        with patch.object(Path, "read_text", return_value="{}"):
            result = label_audit()
        self.assertEqual(result["status"], "audit_unavailable")
        self.assertFalse(result["training_label_contract_verified"])

    def test_verified_paper_is_not_verified_model_lineage(self):
        with patch("futuretwin_distilbert.CLASSIFIER.metadata", return_value={}):
            audit = label_audit()
        self.assertFalse(audit["training_label_contract_verified"])
        self.assertIn("2303.10130", audit["paper"])
        self.assertTrue(audit["missing_evidence"])
        self.assertIn("E3", audit["e3_note"])

    def test_full_inventory_does_not_unlock_unverified_meanings(self):
        eligibility = career_ranking_eligibility({
            "status": "available", "classified_task_count": 30,
            "task_coverage_percentage": 100,
        })
        self.assertTrue(eligibility["lower_exposure"]["task_inventory_ready"])
        self.assertFalse(eligibility["lower_exposure"]["eligible"])
        self.assertFalse(eligibility["growing_jobs"]["eligible"])

    def test_missing_and_possible_inventory_are_not_lower_exposure(self):
        for status in ["uncertain_mapping", "unavailable", "not_precomputed"]:
            result = career_ranking_eligibility({
                "status": status, "classified_task_count": 30, "task_coverage_percentage": 100,
            })
            self.assertFalse(result["lower_exposure"]["task_inventory_ready"])
            self.assertFalse(result["lower_exposure"]["eligible"])


class HistoricalVacancyTests(unittest.TestCase):
    def test_actual_dosm_observations_have_periods_and_source_not_guessed_codes(self):
        rows, meta = load_vacancy_rows()
        self.assertEqual(len(rows), 168)
        self.assertEqual(len({r["period"] for r in rows}), 21)
        self.assertEqual(len({r["source_group_id"] for r in rows}), 8)
        self.assertEqual(meta["verified_overlap_observations"], 160)
        self.assertTrue(all(r["occupation_code"] == "" for r in rows))
        self.assertTrue(all(r["classification_version"] == "" for r in rows))
        self.assertTrue(all(r["scope"] == "major_group" for r in rows))
        self.assertTrue(all(r["source_sha256"] == meta["source_sha256"] for r in rows))
        professionals = {r["period"]: r for r in rows if r["source_group_id"] == "dosm-jmi:professionals"}
        self.assertEqual(professionals["2024-Q2"]["vacancies"], 159133)
        self.assertEqual(professionals["2024-Q3"]["vacancies"], 145049)
        self.assertNotIn("2024-Q4", professionals)
        self.assertFalse(meta["eligible_for_career_ranking"])

    def test_changed_data_does_not_silently_keep_verified_status(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            for name in ["dosm_jmi_group_vacancies.csv", "dosm_jmi_group_vacancies.meta.json"]:
                (path / name).write_bytes((DATA / name).read_bytes())
            with (path / "dosm_jmi_group_vacancies.csv").open("a") as file:
                file.write("\nchanged")
            with self.assertRaises(ValueError):
                load_vacancy_rows(path)

    def cells(self):
        cells = {"B30": "Table 2: Number of Job Offering Advertised Online by Occupation",
                 "H33": "Q3", "I33": "Q4"}
        for row, (_, label) in enumerate(GROUPS, 35):
            cells[f"B{row}"] = label
            cells[f"H{row}"] = "6"
            cells[f"I{row}"] = "0"  # Unobserved next-quarter template, not imported.
            for col, value in zip(["AE", "AF", "AG"], ["1", "2", "3"]):
                cells[f"{col}{row}"] = value
        return cells

    def test_import_ignores_unobserved_zero_templates(self):
        with patch("import_dosm_vacancies.workbook_cells", return_value=self.cells()):
            rows = extract_quarters("unused", through=(2019, 3))
        self.assertEqual(len(rows), 8)
        self.assertEqual(rows[0]["period_start"], "2019-07-01")
        self.assertEqual(rows[0]["period_end_exclusive"], "2019-10-01")
        self.assertTrue(all(r["vacancies"] == 6 for r in rows))

    def test_missing_suppressed_or_inconsistent_counts_fail_import(self):
        for bad in ["", "-", "7", "-1"]:
            cells = self.cells()
            cells["H35"] = bad
            with patch("import_dosm_vacancies.workbook_cells", return_value=cells):
                with self.assertRaises(ValueError):
                    extract_quarters("unused", through=(2019, 3))

    def test_unknown_workbook_cannot_inherit_official_source_claim(self):
        with tempfile.NamedTemporaryFile() as file:
            file.write(b"unknown workbook")
            file.flush()
            with self.assertRaises(ValueError):
                import_history(file.name, file.name)


class LiveStoredEvidenceTests(unittest.TestCase):
    def test_catalog_report_checks_stored_predictions_without_inference(self):
        from futuretwin_distilbert import CLASSIFIER
        model = CLASSIFIER._model
        with patch.object(CLASSIFIER, "classify", side_effect=AssertionError("No inference allowed")):
            evidence = ranking_evidence()
        self.assertIs(CLASSIFIER._model, model)
        tasks = evidence["tasks"]
        self.assertEqual(tasks["task_records"], 18838)
        self.assertEqual(tasks["catalog_occupations"], 3039)
        self.assertEqual(tasks["exact_complete_occupations"], 498)
        self.assertEqual(tasks["possible_only_occupations"], 1973)
        self.assertEqual(tasks["mapped_without_tasks_occupations"], 136)
        self.assertEqual(tasks["unmapped_occupations"], 432)
        self.assertEqual(tasks["eligible_occupation_count"], 498)
        self.assertEqual(evidence["vacancies"]["eligible_occupation_count"], 0)

    def test_all_catalog_occupations_have_explicit_report_rows(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "eligibility.csv"
            export_eligibility(path)
            rows = list(csv.DictReader(io.StringIO(path.read_text())))
        self.assertEqual(len(rows), 3039)
        self.assertEqual(len({r["occupation_uri"] for r in rows}), 3039)
        self.assertEqual(sum(r["lower_exposure_eligible"] == "True" for r in rows), 498)
        self.assertTrue(all(r["growing_jobs_eligible"] == "False" for r in rows))
        self.assertEqual(sum(r["task_inventory_ready"] == "True" for r in rows), 498)

    def test_only_supported_mode_is_enabled_and_best_match_is_default(self):
        from futuretwin_intelligence import ranking_metadata
        for mode in ["lower_exposure", "growing_jobs", "best_match"]:
            rank = ranking_metadata(mode)
            self.assertEqual(rank["effective"], "lower_exposure" if mode == "lower_exposure" else "best_match")
            self.assertEqual([r["id"] for r in rank["options"]],
                              ["lower_exposure", "best_match", "purpose_alignment", "growing_jobs"])
            self.assertNotIn("broad_exposure_percentage", rank["evidence"])
        self.assertEqual(ranking_metadata()["effective"], "best_match")


if __name__ == "__main__":
    unittest.main()
