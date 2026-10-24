"""Occupation search and evidence assembled from FutureTwin's existing data."""
from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path
from typing import Any

import pandas as pd

BASE = Path(__file__).resolve().parent
OCCUPATIONS_FILE = BASE / "occupations_en.csv"
RELATIONS_FILE = BASE / "occupationSkillRelations_en.csv"
TOKEN_RE = re.compile(r"(?u)[^\W_]+(?:[+#][+#]?)?")
ALIAS_SPLIT_RE = re.compile(r"\r?\n|\|")

ISCO_GROUPS = {
    "1": ("managers", "Managers"),
    "2": ("professionals", "Professionals"),
    "3": ("technicians", "Technicians and associate professionals"),
    "4": ("clerical", "Clerical support workers"),
    "5": ("service_sales", "Service and sales workers"),
    "6": ("agriculture", "Agriculture, forestry and fishery workers"),
    "7": ("craft", "Craft and related trades workers"),
    "8": ("operators", "Plant and machine operators"),
    "9": ("elementary", "Elementary occupations"),
}


def _tokens(value: str) -> tuple[str, ...]:
    return tuple(token.casefold() for token in TOKEN_RE.findall(str(value or "")))


def _query_variants(query: str) -> list[tuple[str, ...]]:
    variants = [_tokens(query)]
    expanded = re.sub(r"(?i)\bai\b", "artificial intelligence", query)
    expanded_tokens = _tokens(expanded)
    if expanded_tokens and expanded_tokens not in variants:
        variants.append(expanded_tokens)
    return [variant for variant in variants if variant]


def _aliases(value: str) -> list[str]:
    return [part.strip() for part in ALIAS_SPLIT_RE.split(str(value or "")) if part.strip()]


@lru_cache(maxsize=1)
def _load_esco() -> tuple[dict[str, dict[str, Any]], list[dict[str, Any]], dict[str, dict[str, list[dict[str, str]]]]]:
    if not OCCUPATIONS_FILE.is_file() or not RELATIONS_FILE.is_file():
        raise FileNotFoundError("The ESCO occupation files are not available.")

    occupations_df = pd.read_csv(OCCUPATIONS_FILE, dtype=str, keep_default_na=False)
    occupations: dict[str, dict[str, Any]] = {}
    search_rows: list[dict[str, Any]] = []
    for row in occupations_df.to_dict(orient="records"):
        if row.get("conceptType") != "Occupation" or not row.get("conceptUri"):
            continue
        if row.get("status") and row["status"].casefold() not in {"released", "recommended"}:
            continue
        item = {
            "uri": row["conceptUri"],
            "label": row.get("preferredLabel", "").strip(),
            "isco_group": row.get("iscoGroup", "").strip(),
            "description": (row.get("description") or row.get("scopeNote") or "").strip(),
            "aliases": _aliases(row.get("altLabels", "")),
        }
        if not item["label"]:
            continue
        occupations[item["uri"]] = item
        search_rows.append(item)

    relations_df = pd.read_csv(RELATIONS_FILE, dtype=str, keep_default_na=False)
    skills_by_occupation: dict[str, dict[str, list[dict[str, str]]]] = {}
    for row in relations_df.to_dict(orient="records"):
        uri = row.get("occupationUri", "")
        relation = row.get("relationType", "").casefold()
        skill_uri = row.get("skillUri", "")
        if uri not in occupations or relation not in {"essential", "optional"} or not skill_uri:
            continue
        grouped = skills_by_occupation.setdefault(uri, {"essential": [], "optional": []})
        grouped[relation].append({
            "uri": skill_uri,
            "label": row.get("skillLabel", "").strip(),
        })

    for grouped in skills_by_occupation.values():
        for relation in ("essential", "optional"):
            unique = {skill["uri"]: skill for skill in grouped[relation]}
            grouped[relation] = sorted(unique.values(), key=lambda skill: skill["label"].casefold())
    return occupations, search_rows, skills_by_occupation


def get_esco_occupation_catalog() -> tuple[
    dict[str, dict[str, Any]],
    list[dict[str, Any]],
    dict[str, dict[str, list[dict[str, str]]]],
]:
    """Return the cached, validated ESCO occupation and skill-relation catalog."""
    return _load_esco()


def search_occupations(query: str, limit: int = 10) -> dict[str, Any]:
    """Search official ESCO preferred and alternate occupation titles.

    Matching is token-boundary based; e.g. "AI engineer" never matches
    "animal artificial insemination technician" merely because "ai" is a
    substring. "AI" is also expanded to its common full form.
    """
    if not isinstance(query, str):
        raise TypeError("Search query must be text.")
    query = query.strip()
    if len(query) > 100:
        raise ValueError("Search query must be 100 characters or fewer.")
    if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= 20:
        raise ValueError("limit must be an integer from 1 to 20.")
    if len(query) < 2:
        return {"query": query, "status": "too_short", "suggestions": []}

    variants = _query_variants(query)
    _, rows, _ = _load_esco()
    matches: dict[str, tuple[int, str, str]] = {}
    for item in rows:
        candidates = [("preferred title", item["label"])]
        candidates.extend(("also known as", alias) for alias in item["aliases"])
        best: tuple[int, str, str] | None = None
        for kind, candidate in candidates:
            candidate_tokens = _tokens(candidate)
            for query_tokens in variants:
                score = 0
                if query_tokens == candidate_tokens:
                    score = 100 if kind == "preferred title" else 98
                elif len(query_tokens) <= len(candidate_tokens) and candidate_tokens[:len(query_tokens)] == query_tokens:
                    score = 88 if kind == "preferred title" else 84
                if score and (best is None or score > best[0]):
                    best = (score, kind, candidate)
        if best:
            matches[item["uri"]] = best

    items_by_uri = {item["uri"]: item for item in rows}
    sorted_matches = sorted(
        ((score, items_by_uri[uri], kind, matched_label)
         for uri, (score, kind, matched_label) in matches.items()),
        key=lambda entry: (-entry[0], entry[1]["label"].casefold(), entry[1]["uri"]),
    )[:limit]
    suggestions = []
    for _, item, kind, matched_label in sorted_matches:
        group_code = item["isco_group"]
        group = ISCO_GROUPS.get(group_code[:1], (None, None))[1] if group_code else None
        description = item["description"]
        suggestions.append({
            "uri": item["uri"],
            "label": item["label"],
            "matched_as": kind,
            "matched_label": matched_label,
            "isco_group": group_code,
            "isco_group_label": group,
            "description": description[:500],
        })
    status = "no_match" if not suggestions else "ambiguous" if len(matches) > 1 else "matched"
    return {"query": query, "status": status, "suggestions": suggestions}


def _occupation_ai_evidence(occupation_uri: str) -> dict[str, Any]:
    """Baseline AI task exposure; does not depend on fresh improvements."""
    from futuretwin_baseline_impact import get_occupation_baseline
    return get_occupation_baseline(occupation_uri)


def _occupation_market_context(isco_group: str) -> dict[str, Any]:
    major = (isco_group or "")[:1]
    group = ISCO_GROUPS.get(major)
    if not group:
        return {
            "status": "not_enough_data",
            "note": "No broad employment group is available for this occupation.",
        }
    group_key, group_label = group
    try:
        from jobmarket_trends import compute_malaysia_indicators

        indicators = compute_malaysia_indicators()
        row = next(
            (item for item in indicators.get("occupation_movers", [])
             if item.get("occupation", "").casefold() == group_key),
            None,
        )
        if not row:
            return {
                "status": "not_enough_data",
                "group": group_label,
                "note": "No recent employment figure is available for this broad group.",
            }
        return {
            "status": "broad_context",
            "group": group_label,
            "employment_change_pct": row.get("change_pct"),
            "latest_date": row.get("latest_date"),
            "note": "Broad group employment context only; it is not an exact-role hiring or vacancy trend.",
        }
    except Exception as exc:
        return {
            "status": "unavailable",
            "group": group_label,
            "note": "Employment data could not be loaded.",
            "error": str(exc),
        }


def explore_occupation(uri: str) -> dict[str, Any] | None:
    if not isinstance(uri, str) or not uri.strip():
        raise ValueError("An ESCO occupation identifier is required.")
    occupations, _, skills = _load_esco()
    item = occupations.get(uri.strip())
    if not item:
        return None
    related = skills.get(uri, {"essential": [], "optional": []})
    from futuretwin_task_exposure import safe_occupation_exposure
    return {
        "occupation": {
            "uri": item["uri"],
            "label": item["label"],
            "isco_group": item["isco_group"],
            "isco_group_label": ISCO_GROUPS.get(item["isco_group"][:1], (None, None))[1],
            "description": item["description"],
        },
        "skills": related,
        "ai_impact": _occupation_ai_evidence(uri),
        "task_exposure": safe_occupation_exposure(uri),
        "job_demand": _occupation_market_context(item["isco_group"]),
        "future_skills": {
            "status": "general_guidance",
            "benchmark_links": [],
            "note": "ESCO essential and optional skills are general occupation guidance, not a personal skills gap or a forecast.",
        },
    }
