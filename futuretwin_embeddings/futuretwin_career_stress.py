"""Deterministic, evidence-aware scenario lenses; never career forecasts.

This module consumes the existing baseline, not advancement events. It makes no
model calls and does not promote semantic candidates into verified task links.
"""
from __future__ import annotations

from typing import Any


LABOUR_FIELDS = (
    ("employment_trends", "Exact-career employment trends"),
    ("hiring_growth", "Job vacancies and hiring growth"),
    ("university_intake", "University intake"),
    ("seniority_hiring", "Entry-level versus senior hiring"),
    ("ai_adoption", "Observed workplace AI adoption"),
    ("task_exposure", "Validated AI task exposure"),
    ("human_ai_comparison", "Human versus AI task outcomes"),
    ("human_plus_ai", "Human-plus-AI task outcomes"),
)


def build_stress_test(
    detail: dict[str, Any],
    confirmed: dict[str, Any],
    occupations: dict[str, Any],
    relations: dict[str, Any],
    state: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build explainable suggestions from exact ESCO identities.

    Comparison choices are explicit or provisional saved/interest/ESCO options.
    Shared counts refer only to those choices, never to market demand.
    """
    target_skills = {}
    for key in ("matched_essential", "matched_optional",
                "missing_essential", "missing_optional"):
        for skill in detail.get(key, []):
            target_skills[skill["uri"]] = skill
    from futuretwin_career_insurance import build_insurance
    insurance = build_insurance(detail, confirmed, occupations, relations, state)
    options = insurance["comparison"]["alternatives"]
    option_ids = {
        row["uri"]: {s["uri"] for kind in ("essential", "optional")
                     for s in relations.get(row["uri"], {}).get(kind, [])}
        for row in options
    }

    def shared(skill: dict[str, Any]) -> dict[str, Any]:
        other = [career for career in options
                 if skill["uri"] in option_ids[career["uri"]]]
        return {**skill, "shared_career_count": len(other), "other_careers": other}

    # Only occupation-associated confirmed skills are described as transferable
    # here. Other confirmed skills remain in the Passport, not discarded.
    valuable = [shared(skill) for uri, skill in target_skills.items()
                if uri in confirmed]
    valuable.sort(key=lambda s: (-s["shared_career_count"], s["label"].casefold()))
    baseline = detail.get("ai_impact") or {}
    changes = []
    seen = set()
    for group in baseline.get("task_groups", []):
        task = str(group.get("task") or "").strip()
        linked = []
        for skill in group.get("skills", []):
            uri = skill.get("skill_uri")
            if uri in target_skills and uri not in {s["uri"] for s in linked}:
                linked.append({"uri": uri, "label": target_skills[uri]["label"]})
        if not task or not linked or task.casefold() in seen:
            continue
        seen.add(task.casefold())
        # Group flags are insufficient for verified workplace outcomes. Current
        # engine has semantic candidates only; keep that conservative contract.
        changes.append({
            "task": task, "skills": linked,
            "relationship": "Possible task relationship · semantic candidate, not verified workplace impact",
        })
    from futuretwin_career_scenarios import build_scenarios, workforce_evidence_slots
    scenarios = build_scenarios(detail, insurance, changes, valuable)
    return {
        "status": "hypothetical",
        "notice": "Hypothetical adoption assumptions, not forecasts. No adoption rates, replacement percentages or job-loss estimates are calculated.",
        "scenarios": scenarios,
        "insurance": insurance,
        "evidence": {
            "methodology": [
                "Only explicitly confirmed ESCO skill identifiers count as recorded skills.",
                *insurance["methodology"],
                "The same transferable learning priorities are used across scenarios because validated scenario-specific skill-demand evidence is unavailable.",
                "Observed benchmark measurements remain separate from semantic candidate links and hypothetical workplace adoption.",
                "Profiles select up to one, two or three official skill practice steps and candidate task examples. These are hypothetical display scopes, not measured adoption rates.",
                "Practice steps come from shared preparation options, then other official essential/optional associations. Tool assistance and review safeguards are hypothetical actions, not verified capability claims.",
                "Candidate examples are deduplicated by wording; full returned baseline records remain separately available.",
                "No independent workforce outcomes or verified automation/augmentation classifications are inferred.",
            ],
            "benchmark_baseline": baseline,
            "experimental_task_exposure": detail.get("task_exposure") or {},
            "career_intelligence": detail.get("intelligence") or {},
            "workforce_context": detail.get("job_demand", {}),
            "related_careers": options,
            "occupation_context": detail["occupation"],
            "scenario_assumptions_source": "Product-defined qualitative assumptions; no external forecast or calibrated adoption model.",
            # Stable slots for future evidence adapters. Population, source,
            # period and role scope must be validated before these are populated.
            "labour_market": workforce_evidence_slots(detail["occupation"]["uri"]),
        },
    }
