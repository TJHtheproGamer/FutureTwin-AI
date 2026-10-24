import unittest
from datetime import date, datetime, timezone

import jobmarket_store


class _Cursor:
    def __init__(self):
        self.calls = []

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def executemany(self, query, rows):
        self.calls.append((query, list(rows)))


class _Connection:
    def __init__(self):
        self.cursor_instance = _Cursor()

    def cursor(self):
        return self.cursor_instance


class JobmarketObservationTests(unittest.TestCase):
    def test_schema_keeps_batches_dates_and_mapping_methods_separate(self):
        schema = jobmarket_store.SCHEMA
        self.assertIn("job_posting_observations", schema)
        self.assertIn("original_posted_date DATE", schema)
        self.assertIn("job_posting_skill_observations", schema)
        self.assertIn("job_posting_occupation_matches", schema)
        self.assertIn("mapping_method TEXT NOT NULL", schema)
        self.assertIn("job_posting_observation_lifecycle", schema)
        self.assertIn("COUNT(DISTINCT run_id) AS observation_count", schema)
        self.assertIn("salary_min NUMERIC", schema)
        self.assertIn("source_updated_at TIMESTAMPTZ", schema)
        self.assertIn("job_posting_occupation_suggestions", schema)
        self.assertIn("ALTER TABLE job_postings ALTER COLUMN remote DROP NOT NULL", schema)

    def test_observation_writer_preserves_source_date_and_fetch_window(self):
        conn = _Connection()
        observed_at = datetime(2026, 10, 21, 15, 38, tzinfo=timezone.utc)
        record = {
            "source_posting_id": "p-1",
            "posted_date": date(2026, 10, 6),
            "title": "Project Manager",
            "country": "Worldwide",
            "location": "Remote",
            "remote": True,
            "content_hash": "hash-1",
            "duplicate_of": None,
        }
        count = jobmarket_store.record_posting_observations(
            conn, "batch-1", "remoteok", [record], observed_at
        )

        self.assertEqual(count, 1)
        sql, rows = conn.cursor_instance.calls[0]
        self.assertIn("original_posted_date", sql)
        self.assertEqual(rows[0][0:4], (
            "batch-1", "remoteok", "p-1", observed_at
        ))
        self.assertEqual(rows[0][4:10], (
            date(2026, 10, 6), "Project Manager", "Worldwide", "Remote",
            True, "hash-1"
        ))


if __name__ == "__main__":
    unittest.main()
