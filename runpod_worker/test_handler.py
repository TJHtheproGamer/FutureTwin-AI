import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import handler as worker


class StubModel:
    def encode(self, texts, **kwargs):
        assert texts == ["first", "second"]
        assert kwargs["normalize_embeddings"] is True
        vectors = np.zeros((len(texts), worker.MODEL_DIMENSION), dtype=np.float32)
        vectors[:, 0] = 1
        return vectors

    def get_embedding_dimension(self):
        return worker.MODEL_DIMENSION


class WorkerTests(unittest.TestCase):
    def test_embed_returns_normalized_384d_vectors(self):
        with patch.object(worker, "_load_model", return_value=StubModel()):
            result = worker.handler({"input": {
                "operation": "embed", "texts": [" first ", "second"],
            }})
        self.assertEqual(result["dimension"], 384)
        self.assertEqual(len(result["embeddings"]), 2)
        self.assertTrue(all(len(vector) == 384 for vector in result["embeddings"]))
        self.assertTrue(all(np.isclose(np.linalg.norm(vector), 1) for vector in result["embeddings"]))

    def test_rejects_invalid_texts(self):
        for texts in (None, [], ["  "], ["ok", 3], ["x" * 8001]):
            with self.subTest(texts=repr(texts)[:40]), self.assertRaises(ValueError):
                worker.embed_texts(texts)

    def test_rejects_unknown_operation(self):
        with self.assertRaisesRegex(ValueError, "Unsupported operation"):
            worker.handler({"input": {"operation": "classify", "texts": ["text"]}})

    def test_model_path_must_be_configured(self):
        with patch.dict(os.environ, {}, clear=True), self.assertRaisesRegex(
            RuntimeError, "FUTURETWIN_MODEL_PATH"
        ):
            worker._model_path()

    @unittest.skipUnless(os.environ.get("FUTURETWIN_MODEL_PATH"), "private checkpoint path not set")
    def test_real_checkpoint_loads(self):
        worker._load_model.cache_clear()
        vector = worker.embed_texts(["A fictional person analyzes survey data."])[0]
        self.assertEqual(len(vector), 384)
        self.assertTrue(np.isclose(np.linalg.norm(vector), 1, atol=1e-5))


if __name__ == "__main__":
    unittest.main()
