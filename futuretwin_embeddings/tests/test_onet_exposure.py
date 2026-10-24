"""Real source/crosswalk contracts; test-only class outputs never enter the application DB."""
import json
import hashlib
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from futuretwin_onet_exposure_db import import_source_data, connect
from futuretwin_task_exposure import occupation_exposure, _classification


class OnetSourceAndMappingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.directory = tempfile.TemporaryDirectory()
        cls.path = Path(cls.directory.name) / "test_onet.sqlite3"
        cls.imported = import_source_data(path=cls.path)
        from futuretwin_occupation_api import get_esco_occupation_catalog
        cls.occupations = get_esco_occupation_catalog()[0]
        with connect(cls.path) as connection:
            with connection:
                connection.create_function(
                    "sha256", 1, lambda text: hashlib.sha256(text.encode("utf-8")).hexdigest()
                )
                connection.execute(
                    "INSERT OR REPLACE INTO source_metadata VALUES (?,?)",
                    ("active_model_fingerprint", "test-only-fingerprint"),
                )
                connection.execute(
                    """INSERT INTO task_predictions
                       SELECT 'test-only-fingerprint',onet_soc_code,task_id,
                              sha256(task_text),'E1',0.1,0.8,0.1,8,8,0
                       FROM onet_tasks"""
                )

    @classmethod
    def tearDownClass(cls):
        cls.directory.cleanup()

    def setUp(self):
        self.database_patch = patch(
            "futuretwin_task_exposure.DATABASE", self.path
        )
        self.metadata_patch = patch(
            "futuretwin_task_exposure.CLASSIFIER.metadata",
            return_value={"checkpoint_fingerprint": "test-only-fingerprint"},
        )
        self.database_patch.start()
        self.metadata_patch.start()
        self.addCleanup(self.database_patch.stop)
        self.addCleanup(self.metadata_patch.stop)

    def uri(self, label):
        return next(uri for uri, occupation in self.occupations.items()
                    if occupation["label"] == label)

    def test_full_official_task_inventory_and_metadata_are_imported(self):
        self.assertEqual(self.imported["task_rows"], 18838)
        self.assertEqual(self.imported["mapping_edges"], 4253)
        with connect(self.path) as connection:
            self.assertEqual(connection.execute(
                "SELECT count(DISTINCT onet_soc_code) FROM onet_tasks"
            ).fetchone()[0], 923)
            first = connection.execute(
                "SELECT * FROM onet_tasks WHERE onet_soc_code='11-1011.00' AND task_id='8823'"
            ).fetchone()
            self.assertEqual(first["occupation_title"], "Chief Executives")
            self.assertEqual(first["domain_source"], "Incumbent")
            self.assertEqual(first["task_date"], "08/2023")
            self.assertEqual(first["task_type"], "Core")
            self.assertTrue(first["incumbents_responding"])

    def test_published_relations_and_release_provenance_are_preserved(self):
        with connect(self.path) as connection:
            self.assertEqual(set(row[0] for row in connection.execute(
                "SELECT DISTINCT relationship FROM occupation_mappings"
            )), {"exactMatch", "broadMatch", "narrowMatch", "closeMatch", "exactISCO"})
            metadata = dict(connection.execute("SELECT key,value FROM source_metadata"))
            published = json.loads(metadata["mapping_source"])["published_metadata"]
            self.assertEqual(published["Classification 1 Version"], "O*NET-SOC 2019")
            self.assertEqual(published["Classification 2 Version"], "v1.1.0")
            self.assertEqual(published["Mapping project version date"], "Sep-22")

    def test_identical_source_import_does_not_delete_predictions(self):
        result = import_source_data(path=self.path)
        self.assertFalse(result["imported"])
        with connect(self.path) as connection:
            self.assertEqual(connection.execute(
                "SELECT count(*) FROM task_predictions"
            ).fetchone()[0], 18838)

    def test_accountant_primary_counts_exclude_broad_and_narrow_candidates(self):
        result = occupation_exposure(self.uri("accountant"))
        self.assertEqual(result["status"], "available")
        self.assertTrue(result["source"]["official"])
        self.assertEqual({task["onet_soc_code"] for task in result["tasks"]},
                         {"13-2011.00"})
        self.assertEqual(result["task_coverage_percentage"], 100)
        self.assertEqual(result["distribution"]["E1"]["percentage"], 100)
        self.assertIsNone(result["combined_exposure_percentage"])
        self.assertEqual({mapping["relationship"]
                          for mapping in result["candidate_mappings"]},
                         {"broadMatch", "narrowMatch"})

    def test_software_and_cv_remain_possible_mappings_not_title_guesses(self):
        software = occupation_exposure(self.uri("software developer"))
        self.assertEqual(software["status"], "uncertain_mapping")
        self.assertEqual(software["tasks"], [])
        self.assertEqual(software["distribution"], {})
        cv = occupation_exposure(self.uri("computer vision engineer"))
        self.assertEqual(cv["status"], "uncertain_mapping")
        self.assertIsNone(cv["occupation_total_task_count"])
        self.assertEqual(cv["candidate_mappings"][0]["relationship"], "closeMatch")
        self.assertEqual(cv["candidate_mappings"][0]["onet_soc_code"], "15-2051.00")
        self.assertTrue(cv["candidate_mappings"][0]["tasks"])

    def test_unmapped_uri_is_not_filled_using_a_similar_title(self):
        result = occupation_exposure("software developer")
        self.assertEqual(result["status"], "not_enough_task_data")
        self.assertEqual(result["tasks"], [])

    def test_recommendation_context_omits_all_task_details(self):
        result = occupation_exposure(self.uri("accountant"), include_tasks=False)
        self.assertEqual(result["tasks"], [])
        self.assertTrue(all(mapping["tasks"] == [] for mapping in result["candidate_mappings"]))

    def test_changed_model_fingerprint_never_reuses_old_predictions(self):
        with patch("futuretwin_task_exposure.CLASSIFIER.metadata",
                   return_value={"checkpoint_fingerprint": "changed-model"}):
            result = occupation_exposure(self.uri("accountant"))
        self.assertEqual(result["status"], "not_precomputed")
        self.assertEqual(result["distribution"], {})

    def test_close_e1_e2_flag_is_only_a_transparent_score_gap_heuristic(self):
        row = {
            "label": "E2", "p_e0": 0.02, "p_e1": 0.48, "p_e2": 0.50,
            "input_tokens": 8, "processed_tokens": 8, "truncated": 0,
        }
        result = _classification(row)
        self.assertTrue(result["near_tie_e1_e2"])
        self.assertAlmostEqual(result["top_two_score_gap"], 0.02)
        row.update(p_e1=0.20, p_e2=0.78)
        self.assertFalse(_classification(row)["near_tie_e1_e2"])


if __name__ == "__main__":
    unittest.main()
