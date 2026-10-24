"""FutureTwin: local fine-tuned MiniLM -> ESCO skill candidate matching API.

Place this file at futuretwin_embeddings/futuretwin_skill_api.py in Replit.

Expected paths, relative to this script:
  models/futuretwin_minilm/modules.json
  data/embedding_training/skill_catalog.csv

Commands:
  python futuretwin_embeddings/futuretwin_skill_api.py --demo
  python futuretwin_embeddings/futuretwin_skill_api.py --serve

This is semantic candidate retrieval, not verified skill extraction, employment
forecasting, AI replaceability, or a probability of occupational relevance.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd
from flask import Flask, jsonify, request
from sentence_transformers import SentenceTransformer

BASE = Path(__file__).resolve().parent
MODEL_DIR = BASE / "models" / "futuretwin_minilm"
CATALOG_PATH = BASE / "data" / "embedding_training" / "skill_catalog.csv"
CACHE_DIR = BASE / "data" / "cache"
EMBED_PATH = CACHE_DIR / "futuretwin_skill_embeddings.npy"
META_PATH = CACHE_DIR / "futuretwin_skill_embeddings_meta.json"

app = Flask(__name__)


def _signature() -> str:
    """Invalidate cached vectors when skill catalogue or model files change."""
    digest = hashlib.sha256()
    digest.update(CATALOG_PATH.read_bytes())
    for file in sorted(MODEL_DIR.rglob("*")):
        if file.is_file():
            st = file.stat()
            digest.update(str(file.relative_to(MODEL_DIR)).encode())
            digest.update(f"{st.st_size}:{st.st_mtime_ns}".encode())
    return digest.hexdigest()


@lru_cache(maxsize=1)
def load_index():
    if not (MODEL_DIR / "modules.json").exists():
        raise FileNotFoundError(
            f"Model not found at {MODEL_DIR}. Extract futuretwin_minilm.zip first."
        )
    if not CATALOG_PATH.exists():
        raise FileNotFoundError(
            f"ESCO catalogue missing: {CATALOG_PATH}"
        )

    # Identical candidate construction to our RunPod evaluation scripts.
    catalog = pd.read_csv(CATALOG_PATH, dtype=str)
    required = {"skillUri", "skill", "skill_description"}
    missing = required - set(catalog.columns)
    if missing:
        raise ValueError(f"Skill catalogue is missing columns: {sorted(missing)}")
    catalog = catalog.dropna(subset=["skillUri", "skill"]).copy()
    catalog["skillUri"] = catalog["skillUri"].str.strip()
    catalog["skill"] = catalog["skill"].str.strip()
    catalog = catalog[(catalog.skillUri != "") & (catalog.skill != "")]
    catalog = catalog.drop_duplicates(subset=["skillUri"]).reset_index(drop=True)
    catalog["skill_description"] = catalog["skill_description"].fillna("")
    skill_texts = (
        "Skill: " + catalog["skill"] + ". " + catalog["skill_description"]
    ).str.strip().tolist()

    print("Loading fine-tuned FutureTwin MiniLM on CPU...", flush=True)
    model = SentenceTransformer(str(MODEL_DIR), device="cpu")

    signature = _signature()
    embeddings = None
    if EMBED_PATH.exists() and META_PATH.exists():
        try:
            meta = json.loads(META_PATH.read_text(encoding="utf-8"))
            saved = np.load(EMBED_PATH, allow_pickle=False)
            if (meta.get("signature") == signature
                    and saved.shape == (len(catalog), model.get_sentence_embedding_dimension())):
                embeddings = saved
                print("Loaded cached ESCO skill vectors.", flush=True)
        except (ValueError, OSError, json.JSONDecodeError):
            pass

    if embeddings is None:
        print(f"Encoding {len(catalog):,} ESCO skills (first run may take a while)...", flush=True)
        embeddings = model.encode(
            skill_texts,
            batch_size=64,
            normalize_embeddings=True,
            convert_to_numpy=True,
            show_progress_bar=True,
        )
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        np.save(EMBED_PATH, embeddings)
        META_PATH.write_text(
            json.dumps({"signature": signature, "rows": len(catalog)}, indent=2),
            encoding="utf-8",
        )
        print("Saved vectors for faster future starts.", flush=True)

    print(f"FutureTwin ready: {len(catalog):,} skill candidates.", flush=True)
    return model, catalog, embeddings


def match_skills(text: str, top_k: int = 10) -> list[dict]:
    if not isinstance(text, str) or not text.strip():
        raise ValueError("'text' must be a non-empty string")
    if not isinstance(top_k, int) or isinstance(top_k, bool) or not 1 <= top_k <= 50:
        raise ValueError("'top_k' must be an integer from 1 to 50")

    model, catalog, embeddings = load_index()
    query = model.encode(
        text.strip(), normalize_embeddings=True, convert_to_numpy=True
    )
    scores = embeddings @ query
    k = min(top_k, len(scores))
    idx = np.argpartition(-scores, k - 1)[:k]
    idx = idx[np.argsort(-scores[idx])]
    return [
        {
            "rank": rank,
            "skill": str(catalog.iloc[i]["skill"]),
            "skill_uri": str(catalog.iloc[i]["skillUri"]),
            "description": str(catalog.iloc[i]["skill_description"]),
            "cosine_similarity": round(float(scores[i]), 4),
        }
        for rank, i in enumerate(idx, 1)
    ]


@app.get("/health")
def health():
    return jsonify({
        "status": "ok",
        "model_files_found": (MODEL_DIR / "modules.json").exists(),
        "skill_catalog_found": CATALOG_PATH.exists(),
    })


@app.post("/api/match-skills")
def api_match_skills():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"error": "Send a JSON object"}), 400
    text = payload.get("text", "")
    top_k = payload.get("top_k", 10)
    try:
        matches = match_skills(text, top_k)
    except (ValueError, TypeError) as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify({
        "model": "futuretwin-minilm-esco",
        "input": text,
        "top_k": len(matches),
        "candidates": matches,
        "note": "Similarity is not a confidence probability; validate skills before treating them as job posting evidence.",
    })


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--demo", action="store_true", help="Test matching in this terminal")
    mode.add_argument("--serve", action="store_true", help="Start the Flask API")
    args = parser.parse_args()

    if args.demo:
        occupation = (
            "Occupation: Software developer. "
            "Develops, tests, debugs and maintains software applications."
        )
        print(f"\nInput: {occupation}\n")
        for candidate in match_skills(occupation, top_k=10):
            print(f"{candidate['rank']:>2}. {candidate['skill']} "
                  f"(similarity {candidate['cosine_similarity']:.4f})")
    else:
        # Development API only. Add authentication/rate-limits before publishing.
        load_index()
        port = int(os.getenv("PORT", "5000"))
        app.run(host="0.0.0.0", port=port, debug=False)


if __name__ == "__main__":
    main()
