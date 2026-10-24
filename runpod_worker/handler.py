"""RunPod Serverless handler for the private FutureTwin MiniLM checkpoint."""
from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Any

MODEL_DIMENSION = 384
MAX_TEXTS = 64
MAX_TEXT_CHARS = 8_000


def _model_path() -> Path:
    value = os.environ.get("FUTURETWIN_MODEL_PATH", "").strip()
    if not value:
        raise RuntimeError("FUTURETWIN_MODEL_PATH must point to the mounted model directory")
    path = Path(value)
    if not (path / "modules.json").is_file() or not (path / "model.safetensors").is_file():
        raise FileNotFoundError(
            f"FutureTwin MiniLM checkpoint is incomplete at {path}; "
            "expected modules.json and model.safetensors"
        )
    return path


@lru_cache(maxsize=1)
def _load_model():
    from sentence_transformers import SentenceTransformer

    # Local-only loading prevents a silent fallback to the public base model.
    model = SentenceTransformer(
        str(_model_path()),
        device="cuda" if _cuda_available() else "cpu",
        local_files_only=True,
        trust_remote_code=False,
    )
    actual_dim = model.get_embedding_dimension()
    if actual_dim != MODEL_DIMENSION:
        raise ValueError(
            f"Expected a {MODEL_DIMENSION}-dimensional checkpoint, got {actual_dim}"
        )
    return model


def _cuda_available() -> bool:
    try:
        import torch
        return torch.cuda.is_available()
    except ImportError:
        return False


def embed_texts(texts: Any) -> list[list[float]]:
    """Encode stripped input strings with the existing normalized MiniLM model."""
    if not isinstance(texts, list) or not texts:
        raise ValueError("'texts' must be a non-empty list of strings")
    if len(texts) > MAX_TEXTS:
        raise ValueError(f"'texts' may contain at most {MAX_TEXTS} entries")
    if any(not isinstance(text, str) for text in texts):
        raise ValueError("Every item in 'texts' must be a string")
    cleaned = [text.strip() for text in texts]
    if any(not text for text in cleaned):
        raise ValueError("Text entries must not be empty or whitespace-only")
    if any(len(text) > MAX_TEXT_CHARS for text in cleaned):
        raise ValueError(f"Each text may contain at most {MAX_TEXT_CHARS} characters")

    model = _load_model()
    vectors = model.encode(
        cleaned,
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=False,
    )
    if vectors.shape != (len(cleaned), MODEL_DIMENSION):
        raise RuntimeError(f"Unexpected embedding shape: {vectors.shape}")
    return vectors.tolist()


def handler(job: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(job, dict):
        raise ValueError("Job must be an object")
    payload = job.get("input")
    if not isinstance(payload, dict):
        raise ValueError("Job must contain an 'input' object")
    if payload.get("operation") != "embed":
        raise ValueError("Unsupported operation; use operation='embed'")
    vectors = embed_texts(payload.get("texts"))
    return {"embeddings": vectors, "dimension": MODEL_DIMENSION}


if __name__ == "__main__":
    import runpod

    runpod.serverless.start({"handler": handler})
