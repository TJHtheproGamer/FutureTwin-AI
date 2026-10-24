"""No paid inference, training, profile writes or synthetic production predictions."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from futuretwin_exposure_contract import (
    APPROVED_CHECKPOINT, DOCUMENT_HASHES, checkpoint_contract,
    predicted_share, validate_documents,
)

PACKAGE = Path(__file__).resolve().parents[1] / "models/distilbert_v2"


class ShareTests(unittest.TestCase):
    def share(self, counts, assessed=4, ready=True, verified=True, truncated=0):
        return predicted_share(
            {label: {"count": count} for label, count in zip(("E0", "E1", "E2"), counts)},
            assessed, ready=ready, model={"label_definitions_verified": verified}, truncated=truncated)

    def test_e1_and_e2_are_equally_counted_not_risk_weighted(self):
        for counts in [(1, 1, 2), (1, 2, 1), (1, 0, 3)]:
            s = self.share(counts)
            self.assertEqual(s["percentage"], 75)
            self.assertEqual((s["numerator"], s["denominator"]), (3, 4))
            self.assertEqual(s["weighting"], "unweighted_task_records")

    def test_unknown_incomplete_or_truncated_never_becomes_zero_exposure(self):
        for args in [
            {"ready": False}, {"verified": False}, {"truncated": 1}, {"assessed": 0},
        ]:
            self.assertIsNone(self.share((1, 1, 2), **args)["percentage"])
        for counts in [(1, 1, 1), (-1, 2, 3), (1.0, 1, 2), (True, 1, 2)]:
            self.assertIsNone(self.share(counts)["percentage"])
        self.assertEqual(self.share((4, 0, 0))["percentage"], 0)


@unittest.skipUnless((PACKAGE / "evaluation.json").exists(), "Uploaded v2 metadata required.")
class PackageTests(unittest.TestCase):
    def documents(self):
        return (
            json.loads((PACKAGE / "final_model/label_provenance.json").read_text()),
            json.loads((PACKAGE / "training_manifest.json").read_text()),
            json.loads((PACKAGE / "evaluation.json").read_text()),
        )

    def test_source_column_e3_and_evaluation_are_consistent(self):
        p, m, e = self.documents()
        validate_documents(p, m, e)
        self.assertEqual(p["source_annotation_column"], "gpt4_exposure")
        self.assertEqual(p["e3_policy"], "drop")
        self.assertEqual(p["e3_rows_before_dedup"], 0)
        contract = checkpoint_contract(PACKAGE / "final_model", APPROVED_CHECKPOINT)
        self.assertTrue(contract["training_label_contract_verified"])
        self.assertEqual(contract["historical_evaluation"]["test_samples"], 2746)
        self.assertFalse(contract["historical_evaluation"]["independently_verified"])
        self.assertIn("zero", contract["e3_note"])

    def test_arbitrary_checkpoint_cannot_claim_another_models_provenance(self):
        self.assertFalse(checkpoint_contract(PACKAGE / "final_model", "other-weights")[
            "training_label_contract_verified"])

    def test_bad_annotation_policy_or_metrics_fail_validation(self):
        p, m, e = self.documents()
        for field, value in [
            ("source_annotation_column", "human_exposure_agg"), ("source_sha256", "unknown"),
            ("e3_policy", "merge"), ("e3_rows_before_dedup", 1),
        ]:
            bad = {**p, field: value}
            with self.assertRaises(ValueError):
                validate_documents(bad, m, e)
        bad = copy.deepcopy(e)
        bad["confusion_matrix_e0_e1_e2"][0][0] -= 1
        with self.assertRaises(ValueError):
            validate_documents(p, m, bad)

    def test_missing_or_changed_documents_disable_semantic_contract(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in DOCUMENT_HASHES:
                dest = root / name
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes((PACKAGE / name).read_bytes())
            self.assertTrue(checkpoint_contract(root / "final_model", APPROVED_CHECKPOINT)[
                "training_label_contract_verified"])
            (root / "evaluation.json").write_text("{}")
            self.assertFalse(checkpoint_contract(root / "final_model", APPROVED_CHECKPOINT)[
                "training_label_contract_verified"])
            (root / "evaluation.json").unlink()
            self.assertFalse(checkpoint_contract(root / "final_model", APPROVED_CHECKPOINT)[
                "training_label_contract_verified"])


class RankingAlgorithmTests(unittest.TestCase):
    def recommendations(self, mode, inventory):
        from futuretwin_my_future import build_recommendations
        occupations = {uri: {"label": label, "isco_group": "2"} for uri, label in
                       [("a", "A"), ("b", "B"), ("c", "C")]}
        relations = {uri: {"essential": [{"uri": "skill:x", "label": "X"}], "optional": []}
                     for uri in occupations}
        exposure = {
            "status": "available", "classified_task_count": 10, "task_coverage_percentage": 100,
            "label_definitions_verified": True, "exact_source_inventory_complete": True,
            "predicted_task_exposure": {"status": "available", "percentage": 10},
        }
        with patch("futuretwin_my_future.get_esco_occupation_catalog",
                   return_value=(occupations, [], relations)), \
                patch("futuretwin_my_future._confirmed_skills", return_value={"skill:x": {"label": "X"}}), \
                patch("futuretwin_intelligence.ranking_metadata",
                      return_value={"effective": mode, "options": []}), \
                patch("futuretwin_ranking_evidence.task_inventory", return_value=(inventory, {})), \
                patch("futuretwin_task_exposure.safe_occupation_exposure", return_value=exposure):
            return build_recommendations({}, sort=mode)

    def test_lower_sort_filters_unknowns_and_uses_raw_fraction_before_limit(self):
        inventory = {
            "a": {"lower_exposure_eligible": True, "e1_count": 1, "e2_count": 8, "classified_count": 10},
            "b": {"lower_exposure_eligible": True, "e1_count": 1, "e2_count": 0, "classified_count": 10},
            "c": {"lower_exposure_eligible": False},
        }
        result = self.recommendations("lower_exposure", inventory)
        self.assertEqual([r["uri"] for r in result["recommendations"]], ["b", "a"])
        self.assertEqual(result["ranking"]["excluded_candidate_count"], 1)
        unchanged = self.recommendations("best_match", inventory)
        self.assertEqual([r["uri"] for r in unchanged["recommendations"]], ["a", "b", "c"])

    def test_no_eligible_matches_is_explicit_not_fabricated_or_global_career_list(self):
        result = self.recommendations("lower_exposure", {})
        self.assertEqual(result["recommendations"], [])
        self.assertIn("Choose Best Match", result["message"])


if __name__ == "__main__":
    unittest.main()
