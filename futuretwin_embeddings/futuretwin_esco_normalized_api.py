"""FutureTwin: conservative ESCO ID normalization for explicitly mentioned job skills.

Place next to futuretwin_job_analysis_api.py and futuretwin_skill_api.py.

Commands:
    python futuretwin_embeddings/futuretwin_esco_normalized_api.py --demo
    python futuretwin_embeddings/futuretwin_esco_normalized_api.py --serve

POST /api/analyze-job-v2 with {"text": "...", "top_k": 5}.

This keeps the original /api/analyze-job and /api/match-skills endpoints.
Mapping to an ESCO URI is allowed only when a detected skill term uniquely
matches an official preferred skill label or a provided official alternate label.
No embedding-nearest-neighbor predictions are silently treated as observed
job requirements. Unmatched/ambiguous mentions are kept explicitly unresolved.
"""
from __future__ import annotations

import argparse
import os
import re
import unicodedata
from collections import defaultdict
from functools import lru_cache
from pathlib import Path

import pandas as pd
from flask import jsonify, request

from futuretwin_job_analysis_api import app, analyze_job
from futuretwin_skill_api import BASE, load_index


RAW_ESCO_LOCATIONS = [
    BASE / "skills_en.csv",
    BASE / "data" / "skills_en.csv",
    BASE.parent / "skills_en.csv",
]


def normalize_label(value: str) -> str:
    """Light canonicalization for exact label comparisons, not fuzzy matching."""
    s = unicodedata.normalize("NFKC", str(value)).casefold()
    s = re.sub(r"\s+", " ", s).strip()
    return s


def get_official_aliases(cell: str) -> list[str]:
    """ESCO alternate labels may be newline/pipe separated depending on export."""
    if not cell or not str(cell).strip():
        return []
    # Do not split commas or semicolons: they can be part of a skill's label.
    return [s.strip() for s in re.split(r"\r?\n|\|", str(cell)) if s.strip()]


@lru_cache(maxsize=1)
def load_esco_registry() -> tuple[dict, dict, str | None]:
    _, catalog, _ = load_index()
    allowed = set(catalog["skillUri"].astype(str))
    preferred: dict[str, set[str]] = defaultdict(set)
    aliases: dict[str, set[str]] = defaultdict(set)
    uri_to_name: dict[str, str] = {}

    for row in catalog.itertuples(index=False):
        uri = str(row.skillUri)
        label = str(row.skill)
        uri_to_name[uri] = label
        key = normalize_label(label)
        if key:
            preferred[key].add(uri)

    raw_path = next((p for p in RAW_ESCO_LOCATIONS if p.is_file()), None)
    if raw_path is not None:
        raw = pd.read_csv(raw_path, dtype=str, keep_default_na=False)
        raw.columns = raw.columns.str.strip().str.lstrip("\ufeff")
        if {"conceptUri", "altLabels"}.issubset(raw.columns):
            for row in raw[["conceptUri", "altLabels"]].itertuples(index=False):
                uri = str(row.conceptUri).strip()
                if uri not in allowed:
                    continue
                for alternate in get_official_aliases(row.altLabels):
                    key = normalize_label(alternate)
                    if key:
                        aliases[key].add(uri)
        else:
            print("ESCO skills_en.csv found without expected conceptUri/altLabels; official aliases skipped.", flush=True)

    registry = {"preferred": dict(preferred), "aliases": dict(aliases), "names": uri_to_name}
    return registry, {"skills": len(catalog), "alternate_label_terms": len(aliases)}, str(raw_path) if raw_path else None


def map_mention_to_esco(term: str) -> dict:
    registry, _, _ = load_esco_registry()
    key = normalize_label(term)
    preferred = registry["preferred"].get(key, set())
    official_aliases = registry["aliases"].get(key, set())

    # A unique exact preferred-label match takes precedence over aliases.
    if preferred:
        candidates = preferred
        source = "preferred_label_exact"
    else:
        candidates = official_aliases
        source = "official_alternate_label_exact"

    if not candidates:
        return {"status": "unmatched", "skill_uri": None, "label": None,
                "source": None, "note": "No verified exact ESCO label/alias match; not inferred by similarity."}
    if len(candidates) > 1:
        return {"status": "ambiguous", "skill_uri": None, "label": None,
                "source": source,
                "candidate_count": len(candidates),
                "candidates": [
                    {"skill_uri": u, "label": registry["names"].get(u, "")}
                    for u in sorted(candidates)[:10]
                ]}
    uri = next(iter(candidates))
    return {"status": "matched", "skill_uri": uri,
            "label": registry["names"][uri], "source": source}


def analyze_job_v2(text: str, top_k: int = 5) -> dict:
    # Retain the original safety checks, evidence spans, and semantic separation.
    result = analyze_job(text, top_k=top_k)
    for mention in result["explicit_mentions"]:
        mention["esco_mapping"] = map_mention_to_esco(mention["term"])

    _, stats, raw_path = load_esco_registry()
    result["method"]["esco_uri_mapping"] = (
        "Exact unique ESCO preferred labels; optional exact official alternate labels. "
        "Unmatched and ambiguous terms remain unresolved."
    )
    result["method"]["official_ESCO_alias_file"] = raw_path
    result["method"]["registry"] = stats
    result["warning"] = (
        "An explicit mention is evidence that text contains a term, not proof it is required "
        "(e.g. negation or preferred-only language). ESCO mapping can remain unresolved. "
        "Semantic candidates must not be counted as employer-stated skill requirements."
    )
    return result


@app.post("/api/analyze-job-v2")
def api_analyze_job_v2():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"error": "Send a JSON object"}), 400
    try:
        result = analyze_job_v2(payload.get("text"), payload.get("top_k", 5))
    except (TypeError, ValueError) as e:
        return jsonify({"error": str(e)}), 400
    return jsonify(result)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--demo", action="store_true")
    mode.add_argument("--serve", action="store_true")
    args = parser.parse_args()
    if args.demo:
        example = "Data analyst responsible for SQL queries, data visualization, statistical analysis and dashboard development."
        result = analyze_job_v2(example, top_k=5)
        print("=== Explicit skill → ESCO ID verification ===")
        for mention in result["explicit_mentions"]:
            mapping = mention["esco_mapping"]
            print(f"{mention['term']}: {mapping['status']} -> {mapping['skill_uri']}")
        print("Semantic suggestions remain separate:", len(result["semantic_candidates"]))
    else:
        load_index()
        port = int(os.getenv("PORT", "5000"))
        app.run(host="0.0.0.0", port=port, debug=False)


if __name__ == "__main__":
    main()
