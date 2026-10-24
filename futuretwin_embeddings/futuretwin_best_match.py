"""Explainable Best Match scoring from available, separately identified evidence."""
from __future__ import annotations

import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

BASE = Path(__file__).resolve().parent
CONFIG_PATH = BASE / "data" / "best_match_config.json"

COMPONENTS = (
    ("skill_compatibility", "Skill compatibility"),
    ("ai_task_exposure", "AI task exposure"),
    ("ai_benchmark_evidence", "AI benchmark evidence"),
)

BENCHMARK_UNAVAILABLE_REASON = (
    "Measured model benchmarks are not independently linked to this occupation's tasks "
    "with relevant human-versus-AI evidence. Benchmark results remain separate."
)


def load_config(path: Path | None = None) -> dict[str, Any]:
    """Read editable weights and reject invalid configurations rather than guessing."""
    config = json.loads((path or CONFIG_PATH).read_text(encoding="utf-8"))
    weights = config.get("weights")
    relations = config.get("skill_relation_weights")
    if not isinstance(weights, dict) or set(weights) != {key for key, _ in COMPONENTS}:
        raise ValueError("Best Match weights must specify exactly the three evidence components.")
    values = {}
    for key, value in weights.items():
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
            raise ValueError("Best Match weights must be finite, nonnegative numbers.")
        values[key] = float(value)
    if abs(sum(values.values()) - 100) > 0.0001:
        raise ValueError("Best Match weights must total 100.")
    if (not isinstance(relations, dict) or set(relations) != {"essential", "optional"}
            or any(isinstance(value, bool) or not isinstance(value, (int, float))
                   or not math.isfinite(value) or value < 0 for value in relations.values())
            or abs(sum(relations.values()) - 1) > 0.0001):
        raise ValueError("Essential and optional skill weights must total 1.")
    minimum = config.get("minimum_confirmed_skills_for_broader_profile")
    if isinstance(minimum, bool) or not isinstance(minimum, int) or minimum < 1:
        raise ValueError("The broader-profile skill minimum must be a positive integer.")
    config["weights"] = values
    config["skill_relation_weights"] = {
        key: float(value) for key, value in relations.items()
    }
    return config


def effective_weights(purpose_preferences: dict, config: dict) -> tuple[dict[str, float], float]:
    """Three fixed factors; legacy purpose preferences have no effect."""
    return dict(config["weights"]), 0.0


def _ratio(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if math.isfinite(result) and 0 <= result <= 1 else None


def _skill_component(candidate: dict, relation_weights: dict) -> dict:
    coverage = candidate.get("skill_coverage") or {}
    relation_data = []
    for relation in ("essential", "optional"):
        row = coverage.get(relation) or {}
        try:
            total = int(row.get("total_count", 0))
            matched = int(row.get("matched_count", 0))
        except (TypeError, ValueError):
            continue
        if total <= 0 or matched < 0 or matched > total:
            continue
        relation_data.append({
            "relation": relation,
            "matched_count": matched,
            "total_count": total,
            "coverage": matched / total,
            "weight": relation_weights[relation],
        })
    denominator = sum(row["weight"] for row in relation_data)
    if denominator <= 0:
        return {
            "status": "unavailable", "score": None, "reason":
                "No validated essential or optional ESCO skill relations are available.",
            "basis": "Exact confirmed ESCO skill IDs only.",
            "relation_coverage": [],
        }
    score = sum(row["coverage"] * row["weight"] for row in relation_data) / denominator
    return {
        "status": "available", "score": score,
        "reason": None,
        "basis": "Weighted mean of per-list essential and optional coverage; list size does not dominate.",
        "relation_weights": {row["relation"]: row["weight"] / denominator
                             for row in relation_data},
        "relation_coverage": relation_data,
        "matched_count": candidate.get("matched_skill_count", 0),
        "total_count": (candidate.get("skill_coverage") or {}).get("total_count", 0),
    }


def _task_component(row: dict | None, task_metadata: dict) -> dict:
    if not row:
        return {
            "status": "unavailable", "score": None, "exposure_share": None,
            "reason": task_metadata.get("reason") or
                      "No verified exact-linked task inventory is available.",
        }
    if row.get("mapping_status") != "exact":
        reason = "No exact ESCO–O*NET occupation mapping is available."
    elif not row.get("task_inventory_ready"):
        reason = "The exact-linked source task inventory is incomplete."
    elif row.get("truncated_count", 0):
        reason = "Some task descriptions were truncated before prediction."
    elif not row.get("lower_exposure_eligible"):
        reason = "The task label contract or prediction coverage is not eligible for ranking."
    else:
        reason = None

    denominator = row.get("classified_count")
    numerator = (row.get("e1_count") or 0) + (row.get("e2_count") or 0)
    share = row.get("predicted_task_exposure_share")
    if (reason is None and isinstance(denominator, int) and denominator > 0
            and isinstance(numerator, int) and 0 <= numerator <= denominator
            and isinstance(share, (int, float)) and math.isfinite(share)
            and 0 <= share <= 100):
        return {
            "status": "available", "score": 1 - share / 100,
            "exposure_share": float(share), "numerator": numerator,
            "denominator": denominator, "reason": None,
            "source": task_metadata.get("source", "Verified exact-linked task inventory"),
            "model_fingerprint": task_metadata.get("prediction_fingerprint"),
            "note": "Predicted E1+E2 task share, not job-replacement probability.",
        }
    return {
        "status": "unavailable", "score": None, "exposure_share": None,
        "numerator": numerator if isinstance(numerator, int) else None,
        "denominator": denominator if isinstance(denominator, int) else None,
        "reason": reason or "The verified task-exposure share is incomplete.",
    }


def rank_best_match(
    candidates: list[dict],
    *,
    purpose_preferences: dict | None = None,
    task_inventory: dict | None,
    task_metadata: dict | None,
    confirmed_count: int,
    specific_count: int,
    config: dict | None = None,
    purpose_links: dict | None = None,
    purpose_review_scope: str | None = None,
) -> tuple[list[dict], dict]:
    """Attach evidence components and rank only within matching evidence groups."""
    config = config or load_config()
    weights, _ = effective_weights({}, config)
    task_inventory = task_inventory or {}
    task_metadata = task_metadata or {}
    scored = []
    availability = Counter()
    for candidate in candidates:
        uri = candidate["uri"]
        components = {
            "skill_compatibility": _skill_component(
                candidate, config["skill_relation_weights"]
            ),
            "ai_task_exposure": _task_component(
                task_inventory.get(uri), task_metadata
            ),
            "ai_benchmark_evidence": {
                "status": "unavailable", "score": None,
                "reason": BENCHMARK_UNAVAILABLE_REASON,
            },
        }
        for key, _ in COMPONENTS:
            components[key]["configured_weight"] = config["weights"][key]
            components[key]["effective_weight"] = weights[key]
            components[key]["applied_weight"] = 0.0

        weighted = [
            key for key, _ in COMPONENTS
            if components[key]["status"] == "available" and weights[key] > 0
        ]
        total_weight = sum(weights[key] for key in weighted)
        score = (
            100 * sum(weights[key] * components[key]["score"] for key in weighted) / total_weight
            if total_weight > 0 else None
        )
        for key in weighted:
            components[key]["applied_weight"] = 100 * weights[key] / total_weight

        labels = dict(COMPONENTS)
        group_parts = []
        group_labels = []
        for key in weighted:
            if key == "skill_compatibility":
                relations = [
                    row["relation"]
                    for row in components[key].get("relation_coverage", [])
                ]
                group_parts.append(f"{key}[{'+'.join(relations)}]")
                group_labels.append(
                    labels[key] + " (" + " + ".join(relations) + " lists)"
                )
            else:
                group_parts.append(key)
                group_labels.append(labels[key])
        group_id = "+".join(group_parts) if weighted else "no_scored_factors"
        group_label = " + ".join(group_labels) or "No comparable evidence"
        supported = [key for key, _ in COMPONENTS if components[key]["status"] == "available"]
        profile_min = config["minimum_confirmed_skills_for_broader_profile"]
        early = confirmed_count < profile_min or specific_count < 2
        candidate["best_match"] = {
            "score": round(score, 1) if score is not None else None,
            "score_label": "Evidence-weighted points",
            "components": components,
            "component_coverage": {"available": len(supported), "total": len(COMPONENTS)},
            "supported_components": supported,
            "weighted_components": weighted,
            "evidence_group": {
                "id": group_id, "label": group_label,
                "score_comparable_within_group_only": True,
            },
            "profile_status": "early" if early else "broader",
            "profile_note": (
                "Early options use a small confirmed-skill profile; this is not a confidence estimate."
                if early else "Uses confirmed exact ESCO skill links."
            ),
        }
        for key, _ in COMPONENTS:
            if components[key]["status"] == "available":
                availability[key] += 1
        scored.append(candidate)

    groups = defaultdict(list)
    for candidate in scored:
        groups[candidate["best_match"]["evidence_group"]["id"]].append(candidate)
    group_order = sorted(
        groups,
        key=lambda group_id: (
            -len(groups[group_id][0]["best_match"]["weighted_components"]),
            group_id,
        ),
    )
    output, group_summaries = [], []
    for group_id in group_order:
        rows = groups[group_id]
        rows.sort(key=lambda row: (
            -(row["best_match"]["score"] if row["best_match"]["score"] is not None else -1),
            -row["essential_match_count"], -row["matched_skill_count"],
            -len(row["interest_matches"]),
            -(row["skill_coverage"]["percentage"] or 0),
            row["title"].casefold(), row["uri"],
        ))
        group = rows[0]["best_match"]["evidence_group"]
        group_summaries.append({**group, "candidate_count": len(rows)})
        for index, row in enumerate(rows, 1):
            row["best_match"]["rank_in_group"] = index
            row["best_match"]["evidence_group"]["candidate_count"] = len(rows)
            output.append(row)

    profile_min = config["minimum_confirmed_skills_for_broader_profile"]
    early = confirmed_count < profile_min or specific_count < 2
    relation_weights = config["skill_relation_weights"]
    metadata = {
        "version": config["version"],
        "status": config.get("weight_status", "Initial configurable weights; not empirically validated."),
        "configured_weights": config["weights"],
        "effective_weights": weights,
        "relation_weights": relation_weights,
        "score_label": "Evidence-weighted points, not probability, proficiency or qualification.",
        "score_policy": (
            "Unavailable components are omitted and supported weights renormalized within each career. "
            "Scores are comparable only inside the same evidence group; groups with more weighted factors appear first."
        ),
        "profile": {
            "status": "early" if early else "broader",
            "confirmed_skill_count": confirmed_count,
            "specific_skill_count": specific_count,
            "broader_profile_minimum": profile_min,
            "note": (
                "Early options: fewer than three confirmed skills or fewer than two specific linked skills. "
                "This is a small evidence profile, not a confidence estimate."
                if early else "Recommendations use currently confirmed exact ESCO skill links."
            ),
        },
        "component_availability": {
            key: {"available": availability[key], "candidate_count": len(candidates)}
            for key, _ in COMPONENTS
        },
        "groups": group_summaries,
        "methodology": [
            (
                "Essential and optional skill coverage are normalized by their own list sizes, then weighted "
                f"{relation_weights['essential'] * 100:g}% and {relation_weights['optional'] * 100:g}% "
                "when both are available."
            ),
            "AI task factor rewards a lower predicted E1+E2 task share only for complete, untruncated, exact-linked verified inventories.",
            BENCHMARK_UNAVAILABLE_REASON,
        ],
    }
    return output, metadata


