"""Source-attributed SDG associations and opt-in purpose heuristics.

No model training, DistilBERT access, profile writes or paid inference here.
"""
from __future__ import annotations

import json
import math
from functools import lru_cache
from pathlib import Path

DATA = Path(__file__).resolve().parent / "data"
REVIEW_SCOPE = (
    "Assistant desk review of source text and exact ESCO relationships; "
    "not independent human validation, UN endorsement or measured social impact."
)
REVIEW_STATUSES = {
    "assistant_desk_reviewed",
    "independently_human_approved",
}
DEFAULT_PURPOSE = {"goals": [], "skill_weight": 70, "purpose_weight": 30, "demand_weight": 0}


@lru_cache(maxsize=1)
def catalog():
    document = json.loads((DATA / "sdg_targets_un_v5.json").read_text())
    return document, {t["target_code"]: t for t in document["targets"]}


def clean_preferences(value):
    if value is None:
        return {**DEFAULT_PURPOSE, "goals": []}
    if not isinstance(value, dict):
        raise ValueError("Review your purpose priorities.")
    goals = value.get("goals", [])
    if not isinstance(goals, list) or len(goals) > 17:
        raise ValueError("Choose up to 17 SDGs.")
    allowed = {str(i) for i in range(1, 18)}
    if any(not isinstance(g, str) or g not in allowed for g in goals):
        raise ValueError("Choose goals from the official SDG list.")
    weights = []
    for key, default in (("skill_weight", 70), ("purpose_weight", 30), ("demand_weight", 0)):
        w = value.get(key, default)
        if isinstance(w, bool) or not isinstance(w, (int, float)) or not math.isfinite(w) or not 0 <= w <= 100:
            raise ValueError("Priority weights must be finite numbers from 0 to 100.")
        weights.append(w)
    if weights[2] != 0:
        raise ValueError("Verified role-specific demand is unavailable; demand weight must stay zero.")
    if abs(sum(weights[:2]) - 100) > 0.0001:
        raise ValueError("Skill and purpose weights must total 100.")
    return dict(zip(("skill_weight", "purpose_weight", "demand_weight"), weights),
                goals=list(dict.fromkeys(goals)))


@lru_cache(maxsize=1)
def reviewed_links():
    from futuretwin_occupation_api import get_esco_occupation_catalog
    occupations, _, relations = get_esco_occupation_catalog()
    _, targets = catalog()
    source = json.loads((DATA / "sdg_curated_links.json").read_text())
    result = []
    for raw in source["links"]:
        occupation = occupations.get(raw["occupation_uri"])
        target = targets.get(raw["target_code"])
        linked = relations.get(raw["occupation_uri"], {})
        skill = next((dict(s, relation=r) for r in ("essential", "optional")
                      for s in linked.get(r, []) if s["uri"] == raw["skill_uri"]), None)
        # A changed catalogue cannot silently turn a dangling reference into evidence.
        if not occupation or not target or not skill:
            raise ValueError("An SDG curation reference no longer matches the ESCO catalogue.")
        if raw["strength"] not in {"direct", "indirect", "weak"} or raw["direction"] not in {"positive", "negative", "mixed"}:
            raise ValueError("Invalid reviewed SDG relationship.")
        review_status = raw.get("review_status", "assistant_desk_reviewed")
        if review_status == "source_reviewed":
            review_status = "assistant_desk_reviewed"
        if review_status not in REVIEW_STATUSES:
            raise ValueError("Invalid SDG review status.")
        result.append({
            **raw, "occupation": occupation, "target": target, "skills": [skill],
            "review_status": review_status, "reviewed_at": source["reviewed_at"],
            "review_scope": source["review_scope"], "semantic_score": None,
            "evidence": [
                {"label": "ESCO occupation description", "url": occupation["uri"],
                 "quote": occupation["description"]},
                {"label": "ESCO occupation–skill relation", "url": skill["uri"],
                 "quote": f'{skill["label"]} — {skill["relation"]} for {occupation["label"]}'},
                {"label": f'UN target {target["target_code"]}',
                 "url": f'https://sdgs.un.org/goals/goal{target["goal_code"]}#targets_and_indicators',
                 "quote": target["target_title"]},
            ] + raw.get("context_sources", []),
        })
    return result


@lru_cache(maxsize=1)
def candidate_document():
    """Load the generated local review queue without promoting its suggestions."""
    source = json.loads((DATA / "sdg_candidate_links.json").read_text(encoding="utf-8"))
    if source.get("schema_version") != 1 or not isinstance(source.get("links"), list):
        raise ValueError("The local SDG candidate catalogue has an unsupported format.")
    links = source["links"]
    summary = source.get("summary", {})
    counts = {
        "candidate_link_count": len(links),
        "candidate_occupation_count": len({r.get("occupation_uri") for r in links}),
        "candidate_skill_count": len({r.get("skill_uri") for r in links}),
        "candidate_goal_count": len({str(r.get("goal_code")) for r in links}),
        "candidate_nace_division_count": len({
            r.get("nace_division_anchor") for r in links
            if r.get("nace_division_anchor")
        }),
    }
    for key, actual in counts.items():
        if summary.get(key) != actual:
            raise ValueError(f"The local SDG candidate catalogue has an invalid {key}.")
    for row in links:
        if (row.get("review_status") != "unreviewed_candidate"
                or row.get("relationship_status") != "not_assessed"
                or row.get("strength") is not None
                or row.get("direction") is not None):
            raise ValueError("An unreviewed SDG suggestion cannot carry an assessed relationship.")
        score = row.get("semantic_score")
        if isinstance(score, bool) or not isinstance(score, (int, float)) or not math.isfinite(score):
            raise ValueError("An SDG candidate has an invalid retrieval score.")
    return source


@lru_cache(maxsize=1)
def candidate_records():
    """Resolve review-queue references against the current exact ESCO catalogue."""
    from futuretwin_occupation_api import get_esco_occupation_catalog
    occupations, _, relations = get_esco_occupation_catalog()
    _, targets = catalog()
    source = candidate_document()
    result = []
    for raw in source["links"]:
        occupation = occupations.get(raw["occupation_uri"])
        target = targets.get(raw["target_code"])
        linked = relations.get(raw["occupation_uri"], {})
        skill = next((dict(s, relation=r, description=raw.get("skill_description", ""))
                      for r in ("essential", "optional")
                      for s in linked.get(r, []) if s["uri"] == raw["skill_uri"]), None)
        if not occupation or not target or not skill:
            raise ValueError("An SDG candidate reference no longer matches the ESCO catalogue.")
        result.append({
            **raw,
            "occupation": occupation,
            "target": target,
            "skills": [skill],
            "direction_status": "not_assessed",
        })
    return result


@lru_cache(maxsize=1)
def semantic_index():
    """Reuse the existing local fine-tuned MiniLM and ESCO vectors, read-only."""
    from futuretwin_skill_api import load_index
    model, skills, vectors = load_index()
    targets = catalog()[0]["targets"]
    target_vectors = model.encode([t["target_title"] for t in targets],
                                  normalize_embeddings=True, convert_to_numpy=True,
                                  batch_size=32, show_progress_bar=False)
    return targets, target_vectors, vectors, {str(r.skillUri): i for i, r in skills.iterrows()}


@lru_cache(maxsize=256)
def candidate_links(uri):
    from futuretwin_occupation_api import get_esco_occupation_catalog
    occupations, _, relations = get_esco_occupation_catalog()
    if uri not in occupations:
        return []
    reviewed_targets = {
        row["target_code"] for row in reviewed_links()
        if row["occupation_uri"] == uri
    }
    prepared = [
        row for row in candidate_records()
        if row["occupation_uri"] == uri and row["target_code"] not in reviewed_targets
    ]
    if prepared:
        return sorted(prepared, key=lambda row: -row["semantic_score"])[:3]

    import numpy as np
    targets, target_vectors, skill_vectors, indices = semantic_index()
    skills = {s["uri"]: dict(s, relation=r) for r in ("essential", "optional")
              for s in relations.get(uri, {}).get(r, []) if s["uri"] in indices}
    if not skills:
        return []
    ordered = list(skills)
    scores = target_vectors @ skill_vectors[[indices[s] for s in ordered]].T
    best = np.argmax(scores, axis=1)
    ranked = np.argsort(-np.max(scores, axis=1))
    reviewed = {r["target_code"] for r in reviewed_links() if r["occupation_uri"] == uri}
    out = []
    for i in ranked:
        target = targets[int(i)]
        if target["target_code"] in reviewed:
            continue
        s = skills[ordered[int(best[i])]]
        out.append({
            "id": f'candidate:{uri}:{target["target_code"]}', "occupation_uri": uri,
            "target_code": target["target_code"], "target": target, "skills": [s],
            "strength": None, "direction": None, "direction_status": "not_assessed",
            "relationship_status": "not_assessed",
            "review_status": "unreviewed_candidate",
            "semantic_score": float(scores[i, best[i]]),
            "reason": (
                "Local MiniLM ranked this exact ESCO occupation–skill link near the UN target wording; "
                "it is a review lead, not evidence of contribution or direction."
            ),
            "evidence": [
                {"label": "ESCO occupation description", "url": uri,
                 "quote": occupations[uri].get("description") or occupations[uri]["label"]},
                {"label": "ESCO skill", "url": s["uri"], "quote": s["label"]},
                {"label": f'UN target {target["target_code"]}',
                 "url": target.get("target_uri") or
                        f'https://sdgs.un.org/goals/goal{target["goal_code"]}#targets_and_indicators',
                 "quote": target["target_title"]},
            ],
        })
        if len(out) == 3:
            break
    return out


def occupation_purpose(uri, *, candidates=True):
    from futuretwin_occupation_api import get_esco_occupation_catalog
    occupation = get_esco_occupation_catalog()[0].get(uri)
    if not occupation:
        raise LookupError("Choose an occupation from ESCO search.")
    reviewed = [r for r in reviewed_links() if r["occupation_uri"] == uri]
    strength_rank = {"direct": 0, "indirect": 1, "weak": 2}
    direction_rank = {"positive": 0, "mixed": 1, "negative": 2}
    ordered = sorted(
        reviewed,
        key=lambda r: (strength_rank[r["strength"]], direction_rank[r["direction"]],
                       r["target_code"]),
    )
    primary = ordered[:3]
    tradeoff = next((row for row in ordered if row["direction"] in {"mixed", "negative"}), None)
    if tradeoff and primary and tradeoff not in primary:
        primary[-1] = tradeoff
    candidate_status = "not_requested"
    if candidates and len(primary) < 3:
        try:
            primary += candidate_links(uri)[:3-len(primary)]
            candidate_status = "available"
        except (OSError, ValueError, RuntimeError, ImportError):
            candidate_status = "unavailable"
    return {
        "occupation": occupation, "connections": primary,
        "reviewed_count": len(reviewed), "candidate_status": candidate_status,
        "review_scope": REVIEW_SCOPE,
        "tradeoff_status": (
            "A source-reviewed technology-level trade-off is included; individual outcomes are not measured."
            if any(r["direction"] in {"mixed", "negative"} for r in reviewed) else
            "No source-reviewed negative trade-off for this occupation in the MVP. This does not mean none exists."
        ),
        "notice": "Potential purpose associations, not measured contributions. Unreviewed matches never affect purpose ranking.",
    }


def goal_connections(goal_code):
    """Return desk-reviewed connections and unreviewed suggestions separately."""
    code = str(goal_code).strip()
    doc, _ = catalog()
    goal = next((item for item in doc["goals"] if str(item["code"]) == code), None)
    if not goal:
        raise ValueError("Choose an SDG from 1 to 17.")
    reviewed = [
        row for row in reviewed_links()
        if str(row["target"]["goal_code"]) == code
    ]
    candidates = [
        row for row in candidate_records()
        if str(row["goal_code"]) == code
    ]
    candidates.sort(key=lambda row: -row["semantic_score"])
    return {
        "goal": goal,
        "reviewed_connections": reviewed,
        "reviewed_connection_count": len(reviewed),
        "candidate_suggestions": candidates,
        "candidate_suggestion_count": len(candidates),
        "notice": (
            "Reviewed links are source-based desk reviews. Candidate suggestions are "
            "local similarity retrieval only and do not establish contribution or direction."
        ),
    }


def rank_by_purpose(candidates, preferences):
    """Same exact-skill candidate pool; explicitly heuristic, opt-in scoring."""
    prefs = clean_preferences(preferences)
    metadata = {
        "preferences": prefs, "review_scope": REVIEW_SCOPE, "demand_applied": False,
        "demand_reason": "No comparable verified exact-role vacancy series. Employee counts and wages are not hiring demand.",
        "formula": "Heuristic points = skill_weight × listed-skill coverage fraction + purpose_weight × signed reviewed alignment. Weights total 100; these points are not a percentage of social impact.",
        "purpose_formula": "For each selected SDG with reviewed evidence: strongest direct=1, indirect=0.5, weak=0.25; positive +, negative −, mixed 0; mean over those evidenced SDGs.",
        "unknown_policy": "When purpose has weight, careers without reviewed evidence for any selected goal are excluded, not assigned zero. Coverage is displayed.",
        "score_label": "Heuristic ranking points, not proficiency or social-impact percentage",
    }
    if prefs["purpose_weight"] and not prefs["goals"]:
        return candidates, dict(metadata, fallback_reason="Choose SDGs before applying purpose weighting.")
    grouped = {}
    for r in reviewed_links():
        if r["target"]["goal_code"] in prefs["goals"]:
            grouped.setdefault(r["occupation_uri"], []).append(r)
    ranked = []
    for item in candidates:
        links = grouped.get(item["uri"], [])
        if prefs["purpose_weight"] and not links:
            continue
        by_goal = {}
        for r in links:
            magnitude = {"direct": 1, "indirect": .5, "weak": .25}[r["strength"]]
            value = magnitude * {"positive": 1, "negative": -1, "mixed": 0}[r["direction"]]
            g = r["target"]["goal_code"]
            if g not in by_goal or abs(value) > abs(by_goal[g]):
                by_goal[g] = value
        alignment = sum(by_goal.values()) / len(by_goal) if by_goal else None
        coverage = item["skill_coverage"]["percentage"]
        skill_fit = coverage / 100 if coverage is not None else 0
        score = (prefs["skill_weight"] * skill_fit +
                 prefs["purpose_weight"] * (alignment if alignment is not None else 0)) / 100
        ranked.append(dict(item, purpose={
            "score": alignment, "heuristic_points": score * 100,
            "evidenced_selected_goals": len(by_goal), "selected_goal_count": len(prefs["goals"]),
            "connections": links[:3], "skill_fit": skill_fit,
        }))
    if not ranked and candidates:
        return candidates, dict(metadata, fallback_reason="No skill-linked careers have reviewed evidence for your selected SDGs yet. Showing Best Match.")
    ranked.sort(key=lambda x: -x["purpose"]["heuristic_points"])
    return ranked, dict(metadata, eligible_candidate_count=len(ranked),
                        excluded_candidate_count=len(candidates)-len(ranked))


def public_catalog():
    doc, _ = catalog()
    links = reviewed_links()
    candidates = candidate_document()["summary"]
    careers = {r["occupation_uri"]: r["occupation"] for r in links}
    reviewed_status_counts = {
        status: sum(row["review_status"] == status for row in links)
        for status in REVIEW_STATUSES
    }
    reviewed_goal_codes = sorted(
        {str(row["target"]["goal_code"]) for row in links}, key=int
    )
    from futuretwin_occupation_api import get_esco_occupation_catalog
    total_occupations = len(get_esco_occupation_catalog()[0])
    return {
        **doc, "reviewed_mapping_count": len(links), "reviewed_career_count": len(careers),
        "assistant_desk_reviewed_count": reviewed_status_counts["assistant_desk_reviewed"],
        "independent_human_reviewed_count": reviewed_status_counts["independently_human_approved"],
        "reviewed_goal_count": len(reviewed_goal_codes),
        "reviewed_goal_codes": reviewed_goal_codes,
        "candidate_summary": candidates,
        "total_occupation_count": total_occupations,
        "occupations_without_reviewed_evidence": total_occupations - len(careers),
        "review_scope": REVIEW_SCOPE,
        "reviewed_careers": list(careers.values()), "default_preferences": DEFAULT_PURPOSE,
        "demand_available": False,
    }


def country_context(target_code="6.1"):
    """Keep different indicators and occupational levels separate; no invented gap score."""
    specs = {
        "3.8": ("SH_ACS_UNHC_25", "UHC service coverage index (2025 methodology)", "index, 0–100", {}),
        "4.1": ("SE_TOT_PRFL", "Primary-level minimum reading proficiency, both sexes", "%", {
            "Sex": "BOTHSEX", "Education level": "PRIMAR", "Type of skill": "SKILL_READ"}),
        "6.1": ("SH_H2O_SAFE", "Safely managed drinking water services, all areas", "%", {"Location": "ALLAREA"}),
        "7.2": ("EG_FEC_RNEW", "Renewable energy share of total final consumption", "%", {}),
    }
    if target_code not in specs:
        raise ValueError("Choose target 3.8, 4.1, 6.1 or 7.2.")
    code, title, unit, filters = specs[target_code]
    snapshot = json.loads((DATA / "sdg_malaysia_un_v5.json").read_text())
    series = next(s for s in snapshot["series"] if s["code"] == code)
    observations = []
    for row in series["response"].get("dimensions", []):
        if any(row.get(k) != v for k, v in filters.items()):
            continue
        try:
            value, year = float(row["value"]), int(row["timePeriodStart"])
        except (ValueError, KeyError, TypeError):
            continue
        if math.isfinite(value):
            observations.append({"year": year, "value": value, "dimensions": row})
    observations.sort(key=lambda r: r["year"])
    # Ambiguous multi-dimensional observations must not be silently averaged.
    if len({r["year"] for r in observations}) != len(observations):
        observations = []
    salary_rows = []
    salary_error = None
    try:
        from jobmarket_store import get_stats_series
        rows = get_stats_series("wages_occupation")
        latest = max((str(r["date"]) for r in rows), default=None)
        for r in rows:
            if str(r["date"]) != latest or r["dims"].get("occupation") == "overall":
                continue
            value = r["metrics"].get("wages_median")
            if value is not None and math.isfinite(float(value)):
                salary_rows.append({"group": r["dims"].get("occupation"), "value": float(value),
                                    "date": str(r["date"]), "unit": "MYR/month"})
    except Exception:
        salary_error = "Malaysia wage data could not be loaded; no salary values have been invented."
    associations = [r for r in reviewed_links() if r["target_code"] == target_code]
    from futuretwin_occupation_api import ISCO_GROUPS
    related_groups = {ISCO_GROUPS.get(r["occupation"]["isco_group"][:1], (None,))[0] for r in associations}
    return {
        "country": "Malaysia", "target": catalog()[1][target_code],
        "available_targets": list(specs), "indicator": {
            "code": code, "title": title, "unit": unit, "observations": observations,
            "latest": observations[-1] if observations else None,
            "source_url": series["source_url"], "retrieved_at": snapshot["retrieved_at"],
            "release": snapshot["release"], "filters": filters,
        },
        "wages": sorted([dict(r, related_broad_group=r["group"] in related_groups)
                         for r in salary_rows], key=lambda r: -r["value"]),
        "wage_source_url": "https://open.dosm.gov.my/data-catalogue/wages_occupation",
        "wage_scope": "DOSM broad occupation groups; median monthly salaries of Malaysian-citizen employees. Not an ESCO role salary or vacancies.",
        "wage_error": salary_error, "associations": associations,
        "comparison_status": "context_only", "impact_gap_score": None,
        "notice": "Explore national SDG observations alongside broad-group pay. Different dates and classification levels are retained. No validated need-to-occupation crosswalk or causal impact/pay gap is established; indicators are not combined into a common need score.",
    }
