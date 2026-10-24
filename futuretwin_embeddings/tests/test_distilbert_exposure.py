"""Offline contracts; synthetic mocks here never become production predictions."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from flask import Flask

from futuretwin_distilbert import LocalTaskClassifier, ModelUnavailable, ModelBusy
from futuretwin_exposure_api import register_exposure_routes
from futuretwin_task_exposure import occupation_exposure, safe_occupation_exposure, DATABASE
from futuretwin_distilbert import MODEL_DIR


FIXTURE = {"label": "E1", "probabilities": {"E0": 0.1, "E1": 0.8, "E2": 0.1},
           "input_tokens": 8, "processed_tokens": 8, "truncated": False}


class ClassifierCacheTests(unittest.TestCase):
    def test_cache_survives_instance_restart_and_does_not_store_input_text(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "cache.sqlite3"
            one = LocalTaskClassifier(cache_file=path)
            with patch.object(one, "metadata", return_value={"checkpoint_fingerprint": "test-v1"}), \
                    patch.object(one, "_infer", return_value=[FIXTURE]) as infer:
                one.classify(["A synthetic private task description."])
                result = one.classify(["A synthetic private task description."])
                self.assertEqual(result["cache_hits"], 1)
                infer.assert_called_once()
            self.assertNotIn(b"A synthetic private task description.", path.read_bytes())
            two = LocalTaskClassifier(cache_file=path)
            with patch.object(two, "metadata", return_value={"checkpoint_fingerprint": "test-v1"}), \
                    patch.object(two, "_infer") as infer:
                result = two.classify(["A synthetic private task description."])
                self.assertEqual(result["predictions"][0]["label"], "E1")
                infer.assert_not_called()
            with patch.object(two, "metadata", return_value={"checkpoint_fingerprint": "test-v2"}), \
                    patch.object(two, "_infer", return_value=[FIXTURE]) as infer:
                two.classify(["A synthetic private task description."])
                infer.assert_called_once()  # Changed trained artifacts invalidate the cache.

    def test_missing_checkpoint_fails_without_an_inference_fallback(self):
        with tempfile.TemporaryDirectory() as directory:
            classifier = LocalTaskClassifier(model_dir=Path(directory) / "missing")
            with patch.object(classifier, "_infer") as infer:
                with self.assertRaises(ModelUnavailable):
                    classifier.classify(["Design a software system."])
                infer.assert_not_called()

    def test_changed_inference_method_does_not_reuse_same_weight_cache(self):
        with tempfile.TemporaryDirectory() as directory:
            classifier = LocalTaskClassifier(cache_file=Path(directory) / "cache.sqlite3")
            with patch.object(classifier, "metadata") as metadata, \
                    patch.object(classifier, "_infer", return_value=[FIXTURE]) as infer:
                metadata.return_value = {
                    "checkpoint_fingerprint": "unchanged-weights", "prediction_fingerprint": "method-a"
                }
                classifier.classify(["Synthetic cache fixture."])
                metadata.return_value = {
                    "checkpoint_fingerprint": "unchanged-weights", "prediction_fingerprint": "method-b"
                }
                result = classifier.classify(["Synthetic cache fixture."])
                self.assertEqual(result["cache_hits"], 0)
                self.assertEqual(infer.call_count, 2)

    def test_invalid_input_is_rejected_before_model_loading(self):
        classifier = LocalTaskClassifier()
        with patch.object(classifier, "_infer") as infer:
            for value in ([], [""], ["x" * 8001], [4], ["task"] * 65):
                with self.assertRaises(ValueError):
                    classifier.classify(value)
            infer.assert_not_called()

    def test_incomplete_classifier_head_is_never_used(self):
        classifier = LocalTaskClassifier()
        with patch.object(classifier, "metadata",
                          return_value={"checkpoint_fingerprint": "test",
                                        "prediction_fingerprint": "test"}), \
                patch("transformers.AutoTokenizer.from_pretrained"), \
                patch("transformers.AutoModelForSequenceClassification.from_pretrained",
                      return_value=(None, {"missing_keys": ["classifier.weight"]})) as load:
            with self.assertRaises(ModelUnavailable):
                classifier._infer(["Synthetic task."], "test")
            self.assertTrue(load.call_args.kwargs["local_files_only"])
            self.assertTrue(load.call_args.kwargs["use_safetensors"])
            self.assertFalse(load.call_args.kwargs["trust_remote_code"])

    def test_corpus_uses_one_inference_call_without_changing_ad_hoc_limits(self):
        classifier = LocalTaskClassifier()
        texts = ["Synthetic local corpus task."] * 128
        with patch.object(classifier, "metadata",
                          return_value={"checkpoint_fingerprint": "test-v1"}), \
                patch.object(classifier, "_infer",
                             return_value=[FIXTURE] * len(texts)) as infer:
            result = classifier.classify_corpus(texts)
            infer.assert_called_once_with(texts, "test-v1", progress=None)
            self.assertEqual(len(result["predictions"]), 128)
            with self.assertRaises(ValueError):
                classifier.classify(texts)

    def test_corpus_validation_and_busy_state_do_not_use_a_fallback(self):
        classifier = LocalTaskClassifier()
        with patch.object(classifier, "_infer") as infer:
            with self.assertRaises(ValueError):
                classifier.classify_corpus(["task"] * 25001)
            with self.assertRaises(ValueError):
                classifier.classify_corpus([""])
            infer.assert_not_called()
        with patch.object(classifier, "metadata",
                          return_value={"checkpoint_fingerprint": "test-v1"}):
            classifier._inference_slot.acquire()
            try:
                with self.assertRaises(ModelBusy):
                    classifier.classify_corpus(["Task"])
            finally:
                classifier._inference_slot.release()


@unittest.skipUnless(
    DATABASE.exists() and (MODEL_DIR / "model.safetensors").exists(),
    "Integration checks require the uploaded trained checkpoint and precomputed O*NET database.",
)
class OccupationDistributionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from futuretwin_occupation_api import get_esco_occupation_catalog
        cls.occupations = get_esco_occupation_catalog()[0]

    def uri(self, label):
        return next(k for k, v in self.occupations.items() if v["label"] == label)

    def test_actual_software_mapping_is_not_promoted_to_exact_equivalence(self):
        result = occupation_exposure(self.uri("software developer"), cached_only=True)
        self.assertEqual(result["status"], "uncertain_mapping")
        self.assertEqual(result["sample_task_count"], 0)
        self.assertEqual(result["distribution"], {})
        self.assertTrue(result["label_definitions_verified"])
        self.assertIsNone(result["predicted_task_exposure"]["percentage"])
        self.assertTrue(result["source"]["official"])
        self.assertIsNone(result["combined_exposure_percentage"])
        self.assertEqual(result["tasks"], [])
        self.assertTrue(result["candidate_mappings"])
        self.assertTrue(all(
            task["label"] in ("E0", "E1", "E2")
            for mapping in result["candidate_mappings"] for task in mapping["tasks"]
        ))

    def test_cv_retains_its_official_close_match_without_invented_inventory(self):
        result = occupation_exposure(self.uri("computer vision engineer"), cached_only=True)
        self.assertEqual(result["status"], "uncertain_mapping")
        self.assertEqual(result["tasks"], [])
        self.assertEqual(result["distribution"], {})
        self.assertEqual(len(result["candidate_mappings"]), 1)
        mapping = result["candidate_mappings"][0]
        self.assertEqual(mapping["relationship"], "closeMatch")
        self.assertEqual(mapping["onet_soc_code"], "15-2051.00")
        self.assertEqual(mapping["onet_occupation"], "Data Scientists")

    def test_career_browsing_never_loads_model_or_breaks_existing_fit(self):
        with patch("futuretwin_task_exposure.CLASSIFIER.classify") as classify:
            result = safe_occupation_exposure(self.uri("software developer"))
            self.assertEqual(result["status"], "uncertain_mapping")
            classify.assert_not_called()
        with patch("futuretwin_task_exposure.CLASSIFIER.metadata",
                   side_effect=ModelUnavailable("Model unavailable")):
            self.assertEqual(safe_occupation_exposure("example")["status"], "unavailable")


class ExposureAPITests(unittest.TestCase):
    def setUp(self):
        app = Flask(__name__)
        app.secret_key = "synthetic-test-session-only"
        register_exposure_routes(app)
        self.client = app.test_client()

    def test_post_requires_existing_csrf_and_does_not_run_on_failure(self):
        with patch("futuretwin_resume_api._csrf_valid", return_value=False), \
                patch("futuretwin_exposure_api.CLASSIFIER.classify") as classify:
            response = self.client.post("/api/occupations/classify-tasks", json={"tasks": ["Task"]})
            self.assertEqual(response.status_code, 403)
            classify.assert_not_called()

    def test_validation_and_body_limits(self):
        with patch("futuretwin_resume_api._csrf_valid", return_value=True), \
                patch("futuretwin_exposure_api.CLASSIFIER.classify") as classify:
            for payload in ({}, {"tasks": []}, {"tasks": [None]}, {"tasks": ["x"] * 17}):
                self.assertEqual(self.client.post(
                    "/api/occupations/classify-tasks", json=payload).status_code, 400)
            self.assertEqual(self.client.post(
                "/api/occupations/classify-tasks", data="x" * 65537,
                content_type="application/json").status_code, 413)
            classify.assert_not_called()

    def test_model_failure_and_busy_are_explicit_not_fallback_predictions(self):
        with patch("futuretwin_resume_api._csrf_valid", return_value=True):
            for exc, code in ((ModelUnavailable("Unavailable"), 503), (ModelBusy("Busy"), 429)):
                with patch("futuretwin_exposure_api.CLASSIFIER.classify", side_effect=exc):
                    response = self.client.post(
                        "/api/occupations/classify-tasks", json={"tasks": ["Synthetic task"]})
                    self.assertEqual(response.status_code, code)
                    self.assertNotIn("tasks", response.get_json())

    def test_success_output_envelope_and_rate_limit(self):
        result = {"predictions": [FIXTURE], "model": {"name": "synthetic fixture"}, "cache_hits": 0}
        with patch("futuretwin_resume_api._csrf_valid", return_value=True), \
                patch("futuretwin_exposure_api.CLASSIFIER.classify",
                      side_effect=lambda texts: json.loads(json.dumps(result))):
            for _ in range(10):
                response = self.client.post(
                    "/api/occupations/classify-tasks", json={"tasks": ["Synthetic task"]})
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.get_json()["tasks"][0]["label"], "E1")
                self.assertNotIn("predictions", response.get_json())
            self.assertEqual(self.client.post(
                "/api/occupations/classify-tasks", json={"tasks": ["Synthetic task"]}).status_code, 429)


if __name__ == "__main__":
    unittest.main()
