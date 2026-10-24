"""Separate, auditable career measures. No profile writes or inference calls."""
from __future__ import annotations

from collections import defaultdict
from datetime import date
from functools import lru_cache
import math
from time import time
from typing import Any
from urllib.parse import urlsplit


def finite_number(value):
    if isinstance(value, bool):
        return None
    try:
        number = float(value)
        return number if math.isfinite(number) else None
    except (TypeError, ValueError):
        return None


def safe_url(value):
    if not isinstance(value, str):
        return ""
    try:
        parts = urlsplit(value)
        return value if parts.scheme in {"http", "https"} and parts.hostname and not parts.username else ""
    except ValueError:
        return ""


def score_change(previous, current, unit, direction):
    """Signed score change; lower-is-better changes are not misnamed regressions."""
    old, new = finite_number(previous), finite_number(current)
    if old is None or new is None or direction not in {"higher_better", "lower_better"}:
        raise ValueError("Comparable finite scores and a known scoring direction are required.")
    delta = new - old
    improvement = delta if direction == "higher_better" else -delta
    return {
        "absolute_change": delta,
        "relative_change_pct": 100 * delta / abs(old) if old else None,
        "absolute_change_unit": (
            "percentage points" if unit in {"percent", "percent resolved", "%", "percentage accuracy"}
            else unit
        ),
        "improvement_direction": "improved" if improvement > 0 else "worsened" if improvement < 0 else "unchanged",
    }


def posting_growth(previous, current, *, comparable=False):
    """Do not turn an absent/zero baseline or incomparable samples into growth."""
    old, new = finite_number(previous), finite_number(current)
    if not comparable or old is None or new is None or old <= 0 or new < 0:
        return None
    return 100 * (new - old) / old


def hiring_unavailable():
    return {
        "status": "not_enough_data", "growth_pct": None,
        "reason": "DOSM history covers broad groups, not a verified exact-occupation vacancy series.",
        "basis": "Collected ad samples and broad national groups are not occupation-level hiring growth.",
    }


def ranking_metadata(requested="best_match"):
    from futuretwin_ranking_evidence import ranking_evidence
    evidence = ranking_evidence()
    lower_available = bool(evidence["labels"].get("training_label_contract_verified")
                           and evidence["tasks"].get("eligible_occupation_count", 0) > 0)
    lower_reason = None if lower_available else (
        evidence["labels"].get("reason") if not evidence["labels"].get("training_label_contract_verified")
        else "No complete exact-linked inventories with comparable, untruncated predictions.")
    options = [
        {"id": "lower_exposure", "label": "Lower AI Exposure", "available": lower_available,
         "reason": lower_reason},
        {"id": "best_match", "label": "Best Match", "available": True, "reason": None},
        {"id": "purpose_alignment", "label": "Purpose Alignment", "available": True,
         "reason": "Opt-in heuristic using saved SDG priorities and source-reviewed associations, not measured social impact."},
        {"id": "growing_jobs", "label": "Growing Jobs", "available": False,
         "reason": hiring_unavailable()["reason"]},
    ]
    selected = next((row for row in options if row["id"] == requested), None)
    if selected is None:
        raise ValueError("Choose best_match, lower_exposure, purpose_alignment or growing_jobs.")
    return {
        "requested": requested,
        "effective": requested if selected["available"] else "best_match",
        "fallback_reason": None if selected["available"] else selected["reason"],
        "options": options,
        "evidence": evidence,
        "tie_breakers": (["Ascending unweighted predicted E1+E2 task share"] if
                         requested == "lower_exposure" and lower_available else []) + [
            "Essential confirmed ESCO matches", "All distinct confirmed ESCO matches",
            "User-interest text matches", "Distinct listed-skill coverage",
            "Occupation title", "Occupation URI",
        ],
        "exposure_policy": (
            "Lower AI Exposure filters the existing confirmed-skill candidate pool to eligible exact-linked "
            "inventories and sorts by (E1+E2)/assessed task records, then Best Match tie-breakers. "
            "Requires approved label provenance, 100% task coverage, untruncated predictions and the "
            "same O*NET source release/inference method. Unknown is excluded, not treated as zero. "
            "This is not job safety, replacement risk, working-time exposure or current AI capability."
        ),
    }


def comparable_benchmark_series(records, identities):
    """Strictly partition by source, measure, version, unit, direction and protocol.

    Retain only genuine evaluation dates. Collection-date legacy migrations
    cannot establish evaluation history. Named models remain on every point.
    This is benchmark performance, never verified occupational applicability.
    """
    grouped = defaultdict(list)
    for row in records:
        identity = (
            row.get("source"), row.get("benchmark_name"), row.get("benchmark_version"),
            row.get("task") or "",
        )
        if identity not in identities:
            continue
        raw = row.get("raw_metadata")
        raw = raw if isinstance(raw, dict) else {}
        protocol = raw.get("evaluation_protocol") or raw.get("protocol")
        if (raw.get("migrated_from") or raw.get("evaluation_date_source") == "collection"
                or not isinstance(protocol, str) or not protocol.strip()
                or not row.get("benchmark_version") or not row.get("score_unit")
                or row.get("score_direction") not in {"higher_better", "lower_better"}
                or not row.get("model_name") or not safe_url(row.get("source_url"))):
            continue
        score = finite_number(row.get("score"))
        if score is None:
            continue
        try:
            evaluated = date.fromisoformat(str(row["evaluation_date"])[:10])
        except (KeyError, ValueError, TypeError):
            continue
        key = (*identity, row["score_unit"], row["score_direction"], protocol.strip())
        grouped[key].append({
            "evaluation_date": evaluated.isoformat(), "score": score,
            "model": row["model_name"], "source_url": safe_url(row["source_url"]),
        })
    output = []
    for key, points in sorted(grouped.items()):
        direction = key[5]
        # A frontier may compare named systems under the SAME recorded protocol.
        best_by_date = {}
        for point in sorted(points, key=lambda p: (p["evaluation_date"], p["model"])):
            previous = best_by_date.get(point["evaluation_date"])
            if previous is None or (
                point["score"] > previous["score"] if direction == "higher_better"
                else point["score"] < previous["score"]
            ):
                best_by_date[point["evaluation_date"]] = point
        frontier = []
        for _, point in sorted(best_by_date.items()):
            if not frontier or (
                point["score"] > frontier[-1]["score"] if direction == "higher_better"
                else point["score"] < frontier[-1]["score"]
            ):
                frontier.append(point)
        if len(frontier) < 2:
            continue
        output.append({
            "source": key[0], "benchmark": key[1], "version": key[2], "task": key[3],
            "unit": key[4], "direction": direction, "protocol": key[6],
            "model": "Named evaluated systems; best observed compatible measurements",
            "points": frontier,
            **score_change(frontier[0]["score"], frontier[-1]["score"], key[4], direction),
            "occupation_relationship": "semantic_candidate",
        })
    return output


@lru_cache(maxsize=2)
def _stored_measurements(bucket):
    from benchmark_store import _rows
    return tuple(_rows("""
        SELECT source,benchmark_name,benchmark_version,task,model_name,score,
               score_unit,score_direction,evaluation_date,source_url,raw_metadata
        FROM benchmark_results WHERE evaluation_date IS NOT NULL
          AND benchmark_version<>'' AND score_unit<>''
    """))


def advancement_summary(baseline):
    groups = baseline.get("task_groups") or []
    identities = {
        (g.get("source"), g.get("benchmark"), g.get("benchmark_version"),
         g.get("benchmark_task_id") or "") for g in groups
    }
    result: dict[str, Any] = {
        "status": "not_enough_data", "series": [],
        "measured_task_count": len(groups),
        "reason": "No compatible series with actual evaluation dates and recorded evaluation protocols.",
        "relationship": "Measured benchmark results; career links remain semantic candidates.",
    }
    if not identities:
        return result
    try:
        series = comparable_benchmark_series(_stored_measurements(int(time() // 300)), identities)
    except Exception:
        return {**result, "status": "unavailable",
                "reason": "Stored benchmark history could not be read."}
    if series:
        result.update(status="available", series=series, reason=None)
    return result


def career_intelligence(detail):
    exposure = detail.get("task_exposure") or {}
    has_classes = exposure.get("status") == "available"
    share = exposure.get("predicted_task_exposure") or {}
    return {
        "model_measure": {
            "status": "available" if share.get("status") == "available" else
                      "class_distribution_only" if has_classes else "not_enough_data",
            "label": "Predicted task-exposure share",
            "predicted_task_exposure": share,
            "combined_exposure_percentage": None,
            "reason": share.get("reason") or "Unweighted research-rubric predictions, not job-loss probability.",
        },
        "advancement": advancement_summary(detail.get("ai_impact") or {}),
        "hiring": hiring_unavailable(),
        "automation_potential": {
            "status": "not_enough_data", "percentage": None,
            "reason": "No independently validated workplace feasibility measurements or task-time weights.",
        },
        "replacement_probability": {
            "status": "not_enough_data", "percentage": None,
            "reason": "No calibrated, geography- and time-specific employment-outcome model.",
        },
        "methodology": [
            "Skill coverage = distinct confirmed, exact-linked ESCO skills / distinct listed ESCO skills × 100.",
            "Class share = predicted category count / distinct assessed source tasks × 100; unweighted by working hours.",
            "Coverage = assessed valid source tasks / known tasks in the exact-linked source inventory × 100.",
            "Only exact occupation crosswalk links contribute to the main distribution; possible mappings stay separate.",
            "Fine-tuned local DistilBERT uses CPU, evaluation mode and 160-token inference; its original files are unchanged.",
            "The v2 package documents 160-token training, gpt4_exposure annotations and E3 preparation; held-out accuracy was not independently reproduced.",
            "Benchmark similarity is candidate relevance, not automation probability. Model-release/collection dates are not evaluation dates.",
            "Predicted exposure share = 100 × (E1 + E2 task records) / assessed task records. E2 is not more dangerous than E1.",
            "V2 package-reported held-out E1 F1 is 0.7322; real-world reliability and calibrated uncertainty are unknown.",
        ],
    }


def comparison_status(careers):
    exposures = [c.get("task_exposure") or {} for c in careers]
    eligible = all(
        e.get("status") == "available" and e.get("classified_task_count", 0) > 0
        and e.get("task_coverage_percentage") == 100 for e in exposures
    )
    methods = {e.get("model", {}).get("prediction_fingerprint") for e in exposures}
    sources = {
        (e.get("source", {}).get("version"), e.get("source", {}).get("asset_sha256"))
        for e in exposures
    }
    comparable = bool(eligible and len(methods) == 1 and None not in methods and len(sources) == 1
                      and all(e.get("source", {}).get("asset_sha256") for e in exposures))
    return {
        "class_distributions_comparable": comparable,
        "combined_exposure_allowed": False,
        "predicted_task_exposure_shares_comparable": bool(comparable and all(
            e.get("predicted_task_exposure", {}).get("status") == "available" for e in exposures)),
        "reason": (
            "Same source release and inference method, complete exact-linked inventories. "
            "Compare unweighted class mixes; an eligible predicted share is research-rubric exposure, not job safety."
            if comparable else
            "Some task inventories are missing, incomplete, non-exact or method-incompatible. "
            "Unknown is not lower exposure; no safety ordering is calculated."
        ),
    }
