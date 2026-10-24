"""Strictly local trained-checkpoint inference; no network or base-model fallback."""
from __future__ import annotations

from collections import OrderedDict
from contextlib import contextmanager
from functools import lru_cache
import hashlib
from importlib.metadata import PackageNotFoundError, version as package_version
import json
from pathlib import Path
import sqlite3
import threading
import time

BASE = Path(__file__).resolve().parent
# Promoted only after offline package, CPU regression, corpus and staged app checks.
# The original models/distilbert/final_model and original ZIP remain untouched.
MODEL_DIR = BASE / "models/distilbert_v2/final_model"
CACHE_FILE = BASE.parent / "generated-artifacts/distilbert_predictions.sqlite3"
LABELS = ("E0", "E1", "E2")
MODEL_FILES = ("config.json", "model.safetensors", "tokenizer_config.json",
               "tokenizer.json", "special_tokens_map.json", "vocab.txt")
MAX_TASKS = 64  # Internal precomputation; the HTTP boundary is stricter.
MAX_CHARACTERS = 8000
MAX_TOKEN_LENGTH = 160  # User-specified training-time length; do not alter saved assets.
INFERENCE_METHOD = {
    "revision": "cpu-eval-160-v1",
    "max_length": MAX_TOKEN_LENGTH,
    "batch_size": 4,
    "padding": "longest",
    "dtype": "float32",
    "device": "cpu",
}


def prediction_version(metadata: dict) -> str:
    """Version predictions by tokenization/method as well as unchanged weights."""
    return metadata.get("prediction_fingerprint", metadata["checkpoint_fingerprint"])


class ModelUnavailable(RuntimeError):
    pass


class ModelBusy(RuntimeError):
    pass


@lru_cache(maxsize=4)
def _fingerprint(directory: str, signature: tuple) -> str:
    digest = hashlib.sha256()
    for name in MODEL_FILES:
        digest.update(name.encode())
        with (Path(directory) / name).open("rb") as handle:
            for block in iter(lambda: handle.read(4 * 1024 * 1024), b""):
                digest.update(block)
    return digest.hexdigest()


class LocalTaskClassifier:
    def __init__(self, model_dir=MODEL_DIR, cache_file=CACHE_FILE):
        self.model_dir = Path(model_dir)
        self.cache_file = Path(cache_file)
        self._memory = OrderedDict()
        self._memory_lock = threading.Lock()
        self._inference_slot = threading.Lock()
        self._model = None
        self._tokenizer = None
        self._loaded_fingerprint = None

    def metadata(self) -> dict:
        missing = [name for name in MODEL_FILES if not (self.model_dir / name).is_file()]
        if missing:
            raise ModelUnavailable(
                "Missing local trained model assets: " + ", ".join(missing)
                + ". Restore the active uploaded checkpoint package; no fallback inference is enabled."
            )
        try:
            signature = tuple(
                (name, (self.model_dir / name).stat().st_size,
                 (self.model_dir / name).stat().st_mtime_ns)
                for name in MODEL_FILES
            )
            config = json.loads((self.model_dir / "config.json").read_text())
            labels = {int(k): v for k, v in config["id2label"].items()}
            if (config.get("model_type") != "distilbert"
                    or config.get("architectures") != ["DistilBertForSequenceClassification"]
                    or set(labels) != {0, 1, 2} or set(labels.values()) != set(LABELS)
                    or config.get("label2id") != {v: k for k, v in labels.items()}):
                raise ValueError("Unexpected architecture or classifier label mapping.")
            version = _fingerprint(str(self.model_dir), signature)
            method = {
                **INFERENCE_METHOD,
                "transformers": package_version("transformers"),
                "torch": package_version("torch"),
            }
            prediction_fingerprint = hashlib.sha256(json.dumps(
                {"checkpoint": version, "method": method}, sort_keys=True
            ).encode()).hexdigest()
        except (OSError, ValueError, KeyError, TypeError, PackageNotFoundError) as exc:
            raise ModelUnavailable("The local trained DistilBERT checkpoint is unavailable or invalid.") from exc
        from futuretwin_exposure_contract import checkpoint_contract
        contract = checkpoint_contract(self.model_dir, version)
        verified = contract["training_label_contract_verified"]
        return {
            "name": "FutureTwin fine-tuned DistilBERT v2" if verified else "FutureTwin fine-tuned DistilBERT",
            "checkpoint_fingerprint": version,
            "prediction_fingerprint": prediction_fingerprint,
            "inference_method": method,
            "max_token_length": MAX_TOKEN_LENGTH,
            "model_lifetime": "Lazy-loaded once per worker; reused for subsequent uncached batches.",
            "id2label": {str(k): v for k, v in labels.items()},
            "device": "cpu", "local_files_only": True,
            "label_definitions_verified": verified,
            "label_definition_note": contract["reason"],
            "label_contract": contract,
            "probability_note": "Softmax class outputs are not calibrated confidence or replacement probabilities.",
            "historical_evaluation": contract.get("historical_evaluation") or ({
                "accuracy": 0.7260325881,
                "macro_f1": 0.6400293348,
                "E1_f1": 0.4347826087,
                "independently_verified": False,
                "source": "User-reported held-out RunPod evaluation; not revalidated here.",
                "limitation": "Historical E1 performance is weak; real-world accuracy is unknown.",
            } if version == "de9461c5844645a5098aee0510122afbbd40684e8b44186baa93099dcde5e798" else None),
        }

    @contextmanager
    def _connection(self):
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(self.cache_file, timeout=5)
        try:
            connection.execute("""CREATE TABLE IF NOT EXISTS predictions (
                model_version TEXT NOT NULL, text_hash TEXT NOT NULL,
                result TEXT NOT NULL, created_at REAL NOT NULL,
                PRIMARY KEY(model_version, text_hash))""")
            with connection:
                yield connection
        finally:
            connection.close()

    def _get(self, key):
        with self._memory_lock:
            if key in self._memory:
                self._memory.move_to_end(key)
                return dict(self._memory[key])
        try:
            with self._connection() as connection:
                row = connection.execute(
                    "SELECT result FROM predictions WHERE model_version=? AND text_hash=?", key
                ).fetchone()
            if row:
                result = json.loads(row[0])
                if (result.get("label") in LABELS
                        and set(result.get("probabilities", {})) == set(LABELS)):
                    self._remember(key, result)
                    return result
        except (OSError, sqlite3.Error, ValueError):
            pass  # Cache faults never substitute predictions; actual inference is required.
        return None

    def _remember(self, key, result):
        with self._memory_lock:
            self._memory[key] = dict(result)
            self._memory.move_to_end(key)
            while len(self._memory) > 512:
                self._memory.popitem(last=False)

    def _put(self, key, result):
        self._remember(key, result)
        try:
            with self._connection() as connection:
                connection.execute("INSERT OR REPLACE INTO predictions VALUES (?,?,?,?)",
                                   (*key, json.dumps(result), time.time()))
                connection.execute("""DELETE FROM predictions WHERE rowid IN
                    (SELECT rowid FROM predictions ORDER BY created_at DESC LIMIT -1 OFFSET 5000)""")
            return True
        except (OSError, sqlite3.Error):
            return False

    def _load_model(self, metadata):
        """Called under the inference lock; retain one validated model per worker."""
        if self._loaded_fingerprint == metadata["checkpoint_fingerprint"]:
            return self._model, self._tokenizer
        import torch
        from transformers import AutoModelForSequenceClassification, AutoTokenizer

        torch.set_num_threads(2)
        tokenizer = AutoTokenizer.from_pretrained(
            self.model_dir, local_files_only=True, trust_remote_code=False
        )
        model, loading = AutoModelForSequenceClassification.from_pretrained(
            self.model_dir, local_files_only=True, trust_remote_code=False,
            use_safetensors=True, output_loading_info=True,
        )
        if any(loading.get(k) for k in (
                "missing_keys", "unexpected_keys", "mismatched_keys", "error_msgs")):
            raise ModelUnavailable("The trained checkpoint has incomplete or mismatched weights.")
        if self.metadata()["checkpoint_fingerprint"] != metadata["checkpoint_fingerprint"]:
            raise ModelUnavailable("The checkpoint changed during loading. Retry after it is stable.")
        model.to("cpu").eval()
        self._model, self._tokenizer = model, tokenizer
        self._loaded_fingerprint = metadata["checkpoint_fingerprint"]
        return model, tokenizer

    def _infer(self, texts, expected_version, progress=None):
        """Strict local inference, with method-versioned results and resident weights."""
        try:
            import torch
            metadata = self.metadata()
            if prediction_version(metadata) != expected_version:
                raise ModelUnavailable("The checkpoint or inference method changed. Retry after it is stable.")
            model, tokenizer = self._load_model(metadata)
            results = []
            for start in range(0, len(texts), 4):
                batch = texts[start:start + 4]
                lengths = [len(tokenizer.encode(t, add_special_tokens=True, truncation=False))
                           for t in batch]
                encoded = tokenizer(batch, padding=True, truncation=True, max_length=MAX_TOKEN_LENGTH,
                                    return_tensors="pt")
                with torch.inference_mode():
                    logits = model(**encoded).logits
                    if logits.shape != (len(batch), 3) or not torch.isfinite(logits).all():
                        raise ModelUnavailable("The local classifier produced invalid logits.")
                    probabilities = torch.softmax(logits, dim=-1).cpu().tolist()
                for values, length in zip(probabilities, lengths):
                    label = model.config.id2label[max(range(3), key=lambda i: values[i])]
                    results.append({
                        "label": label,
                        "probabilities": {model.config.id2label[i]: p for i, p in enumerate(values)},
                        "input_tokens": length, "processed_tokens": min(length, MAX_TOKEN_LENGTH),
                        "truncated": length > MAX_TOKEN_LENGTH,
                    })
                if progress is not None:
                    progress(min(start + len(batch), len(texts)), len(texts))
            return results
        except ModelUnavailable:
            raise
        except Exception as exc:
            raise ModelUnavailable("Local trained-checkpoint inference failed. No fallback was used.") from exc

    def classify_corpus(self, texts: list[str], progress=None) -> dict:
        """Classify a local corpus in one model load, without the bounded ad-hoc cache."""
        if not isinstance(texts, list) or not 1 <= len(texts) <= 25000:
            raise ValueError("A precomputation batch must contain 1–25,000 tasks.")
        if any(not isinstance(text, str) or not text.strip() or len(text) > MAX_CHARACTERS
               for text in texts):
            raise ValueError(f"Each task must contain 1–{MAX_CHARACTERS} characters.")
        metadata = self.metadata()
        if not self._inference_slot.acquire(blocking=False):
            raise ModelBusy("Local classification is busy. Please retry shortly.")
        try:
            predictions = self._infer(
                texts, prediction_version(metadata), progress=progress
            )
        finally:
            self._inference_slot.release()
        return {"model": metadata, "predictions": predictions, "cache_hits": 0}

    def classify(self, texts: list[str]) -> dict:
        if not isinstance(texts, list) or not 1 <= len(texts) <= MAX_TASKS:
            raise ValueError(f"Provide between 1 and {MAX_TASKS} task descriptions.")
        if any(not isinstance(t, str) or not t.strip() or len(t) > MAX_CHARACTERS for t in texts):
            raise ValueError(f"Each task must contain 1–{MAX_CHARACTERS} characters.")
        metadata = self.metadata()
        version = prediction_version(metadata)
        # Exact text hashes preserve inference inputs, and raw submitted text is not cached.
        keys = [(version, hashlib.sha256(t.encode()).hexdigest()) for t in texts]
        results = [self._get(key) for key in keys]
        cached_count = sum(r is not None for r in results)
        cache_persisted = True
        if cached_count < len(texts):
            if not self._inference_slot.acquire(blocking=False):
                raise ModelBusy("Local classification is busy. Please retry shortly.")
            try:
                missing = list(dict.fromkeys(key for key, r in zip(keys, results) if r is None))
                lookup = {key: text for key, text in zip(keys, texts)}
                predictions = self._infer([lookup[key] for key in missing], version)
                inferred = dict(zip(missing, predictions))
                for key, result in inferred.items():
                    cache_persisted = self._put(key, result) and cache_persisted
                results = [r if r is not None else dict(inferred[key])
                           for key, r in zip(keys, results)]
            finally:
                self._inference_slot.release()
        return {"model": metadata, "predictions": results, "cache_hits": cached_count,
                "cache_storage": "disk_and_bounded_memory" if cache_persisted else "bounded_memory_only"}


CLASSIFIER = LocalTaskClassifier()
