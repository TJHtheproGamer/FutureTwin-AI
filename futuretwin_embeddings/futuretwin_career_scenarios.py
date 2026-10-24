"""Configurable, hypothetical practice scopes; not adoption predictions."""
from __future__ import annotations

from copy import deepcopy
from typing import Any

from futuretwin_career_insurance import skill_descriptions


SCENARIO_PROFILES = (
    {
        "id": "slower_adoption", "label": "Slower AI adoption",
        "scope": "limited_assistance", "max_workflow_steps": 1, "max_task_examples": 1,
        "assumption": "Assume limited assistance in a selected workflow, with people retaining the existing method.",
        "assistance": "If a tool proves suitable, explore a small suggestion for “{skill}”; keep your own method.",
        "review": "Check the suggestion against your own work before using it.",
        "actions": ["Practise {skills} without relying on AI.",
                    "Try a small tool-assisted example only if appropriate, then compare it with your own result."],
    },
    {
        "id": "moderate_adoption", "label": "Moderate AI adoption",
        "scope": "reviewed_sequence", "max_workflow_steps": 2, "max_task_examples": 2,
        "assumption": "Assume more frequent assistance across selected work steps, with human review at each handoff.",
        "assistance": "If suitable, explore assistance for “{skill}” within a sequence of reviewed steps.",
        "review": "Record changes, check each result and approve it before the next step.",
        "actions": ["Build a small reviewed practice sequence using {skills}.",
                    "Keep a change log and compare each assisted step with a non-assisted result."],
    },
    {
        "id": "faster_adoption", "label": "Faster AI adoption",
        "scope": "validated_workflow", "max_workflow_steps": 3, "max_task_examples": 3,
        "assumption": "Assume broader assistance, with workflow validation, reliability checks and human oversight.",
        "assistance": "If suitable and permitted, test assistance for “{skill}” as part of a broader practice workflow.",
        "review": "Define acceptance checks, test failures and keep a human approval and fallback route.",
        "actions": ["Create a practice workflow combining {skills}.",
                    "Define acceptance tests, check failure cases and practise a manual fallback before expanding use."],
    },
)


def build_scenarios(detail: dict, insurance: dict, changes: list, valuable: list,
                    profiles: tuple | None = None) -> list[dict[str, Any]]:
    """Select increasing example scope, not increasing measured task exposure.

    Practice order comes from the shared preparation options, followed by other
    official essential/optional associations if needed. No task is invented.
    These assembled exercises are NOT a claim about a complete real job workflow.
    """
    catalog = skill_descriptions()
    practice = []
    seen = set()
    sources = (
        insurance.get("prepare", []),
        [{**s, "relation": "essential"} for key in ("matched_essential", "missing_essential")
         for s in detail.get(key, [])],
        [{**s, "relation": "optional"} for key in ("matched_optional", "missing_optional")
         for s in detail.get(key, [])],
    )
    for source in sources:
        for skill in source:
            if skill["uri"] in seen:
                continue
            seen.add(skill["uri"])
            practice.append(skill)
    result = []
    exposure = detail.get("task_exposure") or {}
    # Exact occupation-task provenance only; class codes do not imply tool suitability.
    source_tasks = exposure.get("tasks", []) if exposure.get("status") == "available" else []
    for profile in profiles if profiles is not None else SCENARIO_PROFILES:
        chosen = practice[:profile["max_workflow_steps"]]
        steps = [{
            "uri": s["uri"], "label": s["label"], "relation": s["relation"],
            "description": catalog.get(s["uri"], {}).get("description", ""),
            "assistance": profile["assistance"].format(skill=s["label"]),
            "review": profile["review"],
            "linked_tasks": [
                deepcopy(c) for c in changes
                if s["uri"] in {linked["uri"] for linked in c.get("skills", [])}
            ][:profile["max_task_examples"]],
        } for s in chosen]
        labels = ", ".join(f"“{s['label']}”" for s in chosen)
        actions = [s.format(skills=labels) for s in profile["actions"]] if chosen else [
            "Choose a career with official occupation-skill evidence before planning a practice workflow."
        ]
        if insurance.get("prepare"):
            actions.append("Review the learning options below; if you already know a skill, use the Passport confirmation process.")
        result.append({
            "id": profile["id"], "label": profile["label"], "assumption": profile["assumption"],
            "profile": {k: profile[k] for k in ("scope", "max_workflow_steps", "max_task_examples")},
            "workflow": {
                "title": f"Practice exploration for {detail['occupation']['label']}",
                "note": "Hypothetical practice sequence assembled from official ESCO skill associations—not an observed or complete job workflow.",
                "steps": steps,
            },
            "assistance_summary": "Tool suitability and real-world capability remain unverified. The number of examples is a scenario setting, not measured adoption or task exposure.",
            "changes": deepcopy(changes[:profile["max_task_examples"]]),
            "valuable": deepcopy(valuable[:5]),
            "prepare": actions,
            "occupational_task_examples": [
                {
                    "task_id": task.get("task_id"),
                    "onet_soc_code": task.get("onet_soc_code"),
                    "text": task.get("text") or task.get("task_text") or "",
                    "predicted_class": task.get("label"),
                    "source": deepcopy(exposure.get("source", {})),
                    "relationship": "Exact-mapped source task; experimental class, not demonstrated automation.",
                }
                for task in source_tasks[:profile["max_task_examples"]]
            ],
            "limitations": [
                "No verified exact-career adoption, employment or human-plus-AI outcome is available.",
                "Benchmark performance and semantic similarity do not establish workplace automation.",
                "ESCO associations do not establish that a skill will become more important.",
            ] + ([] if changes else ["Not enough task evidence for this career."]),
        })
    return result


def workforce_evidence_slots(occupation_uri: str) -> list[dict[str, Any]]:
    """Provenance contract for future evidence adapters; no fabricated values.

    A future provider must populate occupation/location/population/period/source
    and comparable task conditions before changing status to observed. Broad
    occupational-group observations stay in separate workforce_context.
    """
    from futuretwin_career_stress import LABOUR_FIELDS
    return [
        {
            "id": key, "label": label, "status": "unavailable", "value": None,
            "occupation_uri": occupation_uri, "location": None, "population": None,
            "period_start": None, "period_end": None, "source_url": None,
            "observed_at": None, "task_conditions": None, "evidence_type": "not_available",
            "note": "Data not available. Broad-group context and benchmark measurements do not fill this exact-career evidence gap.",
        }
        for key, label in LABOUR_FIELDS
    ]
