"""Conservative ESCO occupation candidates for collected job advertisements.

Exact preferred/alternate ESCO titles are checked first. The existing local,
fine-tuned FutureTwin MiniLM is used only to retrieve semantic candidates after
exact matching fails. Semantic outputs remain suggestions, never verified
occupation assignments or employment predictions.
"""
from __future__ import annotations

import hashlib
import json
import re
from functools import lru_cache
from pathlib import Path

import numpy as np

BASE = Path(__file__).resolve().parent
CACHE_DIR = BASE / "data" / "cache"
VECTOR_PATH = CACHE_DIR / "futuretwin_occupation_embeddings.npy"
META_PATH = CACHE_DIR / "futuretwin_occupation_embeddings_meta.json"
THRESHOLDS_PATH = BASE / "data" / "jobmarket" / "occupation_match_thresholds.json"
SENIORITY = {
    "senior", "junior", "lead", "staff", "principal", "associate",
    "sr", "jr", "mid", "midlevel", "intermediate",
}
TRAILING_LEVELS = {"i", "ii", "iii", "iv", "1", "2", "3", "4"}
GENERIC_ALIASES = {
    "engineer", "manager", "director", "specialist", "officer",
    "consultant", "assistant", "worker", "technician", "executive",
}


def normalize_title(value: str) -> str:
    """Normalize punctuation and remove only common seniority/level modifiers."""
    text = str(value or "").casefold()
    text = re.sub(r"\([^)]*\)|\[[^]]*\]", " ", text)
    tokens = re.findall(r"[a-z0-9]+", text)
    while tokens and tokens[0] in SENIORITY:
        tokens.pop(0)
    while tokens and tokens[-1] in SENIORITY | TRAILING_LEVELS:
        tokens.pop()
    return " ".join(tokens)


def exact_title_matches(title: str, occupations: dict, title_index=None) -> list[dict]:
    """Match normalized preferred and alternate ESCO titles; preserve method."""
    normalized = normalize_title(title)
    if not normalized:
        return []
    if title_index is not None:
        return title_index.get(normalized, [])
    matches = []
    for uri, occupation in occupations.items():
        if normalized == normalize_title(occupation.get("label", "")):
            matches.append({
                "uri": uri, "label": occupation["label"],
                "method": "normalized_exact_preferred_title",
            })
            continue
        if normalized not in GENERIC_ALIASES and any(normalized == normalize_title(alias)
               for alias in occupation.get("aliases", [])):
            matches.append({
                "uri": uri, "label": occupation["label"],
                "method": "normalized_exact_alternate_title",
            })
    return sorted(matches, key=lambda row: (row["label"].casefold(), row["uri"]))


def build_title_index(occupations):
    index = {}
    for uri, row in occupations.items():
        entries = [(row.get("label", ""), "normalized_exact_preferred_title")]
        entries.extend((alias, "normalized_exact_alternate_title")
                       for alias in row.get("aliases", []))
        for title, method in entries:
            normalized = normalize_title(title)
            if not normalized:
                continue
            if method == "normalized_exact_alternate_title" and normalized in GENERIC_ALIASES:
                continue
            matches = index.setdefault(normalized, [])
            if not any(item["uri"] == uri for item in matches):
                matches.append({"uri": uri, "label": row["label"], "method": method})
    return index


def _signature_json(value):
    if isinstance(value, (set, frozenset)):
        return sorted(value)
    raise TypeError(f"unsupported occupation signature value: {type(value).__name__}")


def _signature(model_signature: str, rows: list[dict]) -> str:
    digest = hashlib.sha256((model_signature + "|job-duties-text-v2").encode("utf-8"))
    for row in rows:
        digest.update(json.dumps(
            row,
            sort_keys=True,
            ensure_ascii=False,
            default=_signature_json,
        ).encode("utf-8"))
    return digest.hexdigest()


@lru_cache(maxsize=1)
def load_occupation_index():
    """Build/reuse normalized occupation vectors using the existing MiniLM."""
    from futuretwin_occupation_api import get_esco_occupation_catalog
    from futuretwin_skill_api import _signature as skill_model_signature
    from futuretwin_skill_api import load_index

    occupations, _, relations = get_esco_occupation_catalog()
    rows = []
    for uri, occupation in sorted(occupations.items()):
        grouped = relations.get(uri, {"essential": [], "optional": []})
        essential = [s.get("label", "").strip() for s in grouped.get("essential", [])]
        optional = [s.get("label", "").strip() for s in grouped.get("optional", [])]
        aliases = occupation.get("aliases", [])
        text = (
            f"Occupation: {occupation.get('label', '')}. "
            f"Also known as: {', '.join(aliases[:12])}. "
            f"{occupation.get('description', '')} "
            f"Essential skills: {', '.join(essential[:16])}. "
            f"Optional skills: {', '.join(optional[:8])}."
        )
        rows.append({
            "uri": uri,
            "label": occupation.get("label", ""),
            "text": text,
            "skill_uris": {
                kind: {item["uri"] for item in grouped.get(kind, []) if item.get("uri")}
                for kind in ("essential", "optional")
            },
        })

    model, _, _ = load_index()
    signature = _signature(skill_model_signature(), rows)
    vectors = None
    if VECTOR_PATH.is_file() and META_PATH.is_file():
        try:
            meta = json.loads(META_PATH.read_text(encoding="utf-8"))
            saved = np.load(VECTOR_PATH, allow_pickle=False)
            if (meta.get("signature") == signature
                    and saved.shape == (
                        len(rows), model.get_sentence_embedding_dimension())):
                vectors = saved
        except (ValueError, OSError, json.JSONDecodeError):
            pass
    if vectors is None:
        vectors = model.encode(
            [row["text"] for row in rows],
            batch_size=64,
            normalize_embeddings=True,
            convert_to_numpy=True,
            show_progress_bar=True,
        )
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        np.save(VECTOR_PATH, vectors)
        META_PATH.write_text(
            json.dumps({"signature": signature, "rows": len(rows)}, indent=2),
            encoding="utf-8",
        )
    for row, vector in zip(rows, vectors):
        row["skill_uris"] = {
            kind: set(values) for kind, values in row["skill_uris"].items()
        }
    return model, rows, vectors, signature


def thresholds() -> dict | None:
    """Only return automatic suggestion cutoffs after human-reviewed calibration."""
    try:
        data = json.loads(THRESHOLDS_PATH.read_text(encoding="utf-8"))
        minimum = float(data["minimum_cosine"])
        margin = float(data["minimum_margin"])
        reviewed = int(data["reviewed_examples"])
        if not data.get("automatic_suggestions_enabled", False):
            return None
        if not (0 <= minimum <= 1 and 0 <= margin <= 1 and reviewed >= 10):
            return None
        return {**data, "minimum_cosine": minimum, "minimum_margin": margin}
    except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError):
        return None


def semantic_candidates_batch(
    postings: list[dict],
    explicit_by_ad: dict[tuple[str, str], dict] | None = None,
    top_k: int = 3,
) -> tuple[list[list[dict]], str]:
    """Batch-encode job title/duties and return local MiniLM candidates."""
    usable = [(index, posting) for index, posting in enumerate(postings)
              if str(posting.get("title") or "").strip()]
    if not usable:
        return [[] for _ in postings], ""
    model, rows, vectors, signature = load_occupation_index()
    from futuretwin_job_text import relevant_responsibilities
    explicit_by_ad = explicit_by_ad or {}
    queries = []
    skill_rows_by_index = {}
    for original_index, posting in usable:
        key = (posting.get("source", ""), posting.get("source_posting_id", ""))
        evidence_skills = list(explicit_by_ad.get(key, {}).values())
        skill_rows_by_index[original_index] = evidence_skills
        skill_labels = [str(row.get("label") or "") for row in evidence_skills
                        if row.get("label")]
        queries.append(
            f"{str(posting.get('title') or '').strip()}. "
            f"{str(posting.get('title') or '').strip()}. "
            f"Explicitly mentioned skills: {', '.join(skill_labels[:12])}. "
            f"{relevant_responsibilities(posting.get('description_text'))}."
        )
    query_vectors = model.encode(
        queries, batch_size=32, normalize_embeddings=True, convert_to_numpy=True
    )
    score_matrix = query_vectors @ vectors.T
    k = min(max(1, int(top_k)), len(rows))
    output = [[] for _ in postings]
    for query_index, (original_index, _posting) in enumerate(usable):
        scores = score_matrix[query_index]
        indices = np.argpartition(-scores, k - 1)[:k]
        indices = indices[np.argsort(-scores[indices])]
        skill_uris = {
            str(row.get("uri")) for row in skill_rows_by_index[original_index]
            if row.get("uri")
        }
        candidates = []
        for rank, index in enumerate(indices, 1):
            row = rows[int(index)]
            supported = skill_uris & row["skill_uris"]["essential"]
            supported |= skill_uris & row["skill_uris"]["optional"]
            candidates.append({
                "uri": row["uri"],
                "label": row["label"],
                "candidate_rank": rank,
                "cosine_similarity": float(scores[index]),
                "supporting_skill_uris": sorted(supported),
                "method": "fine_tuned_minilm_semantic_candidate",
            })
        # Duties and literal skill evidence are included in the encoded query;
        # raw cosine order remains the candidate ranking. Supporting skill
        # URIs are disclosed for human inspection, not used as a hidden score.
        output[original_index] = candidates
    return output, signature


def semantic_candidates(
    title: str,
    description: str,
    explicit_skills: list[dict] | None = None,
    top_k: int = 3,
) -> list[dict]:
    """Single-post convenience wrapper; candidates remain unverified."""
    if not isinstance(title, str) or not title.strip():
        return []
    posting = {
        "source": "", "source_posting_id": "", "title": title,
        "description_text": description or "",
    }
    candidates, _ = semantic_candidates_batch(
        [posting], {( "", ""): {str(i): row for i, row in
                                 enumerate(explicit_skills or [])}}, top_k)
    return candidates[0]


def classify_semantic_candidates(candidates: list[dict]) -> list[dict]:
    """Separate calibrated suggestions from uncertain candidates, fail closed."""
    calibration = thresholds()
    if not calibration:
        return [{**row, "status": "uncertain",
                 "status_reason": "No independently validated matching threshold is enabled."}
                for row in candidates]
    minimum = calibration["minimum_cosine"]
    margin = calibration["minimum_margin"]
    best_score = candidates[0]["cosine_similarity"] if candidates else 0
    second_score = (candidates[1]["cosine_similarity"] if len(candidates) > 1
                    else 0)
    gap = best_score - second_score
    status = ("suggested" if best_score >= minimum and gap >= margin
              else "uncertain")
    return [
        {**row, "status": status if index == 0 else "uncertain",
         "status_reason": (
             "Meets the reviewed retrieval threshold; still a semantic suggestion."
             if index == 0 and status == "suggested"
             else "Below the reviewed threshold or not the top candidate."
         )}
        for index, row in enumerate(candidates)
    ]
