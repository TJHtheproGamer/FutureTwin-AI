"""Explainable ESCO learning options. No employability or demand scoring."""
from __future__ import annotations

import csv
import re
from functools import lru_cache
from pathlib import Path
from typing import Any

MAX_ALTERNATIVES = 5
_WORDS = re.compile(r"[a-z][a-z0-9]+")
_STOP = set("""a an the and or of to in for on by with as from that this these
those their its it is are be being been they them at into such can using use
used include including different various other based related specific work
skills skill knowledge ability activities information understand understanding
ensure provide develop development apply applications process processes""".split())
# These are intentionally transparent editorial themes, NOT official ESCO
# hierarchy nodes, learned categories or evidence of relative importance.
THEMES = (
    ("AI and perception", {"artificial intelligence", "machine learning", "computer vision",
                           "neural", "image", "images", "cognitive", "deep learning"}),
    ("Communication and collaboration", {"communicate", "communication", "report",
                                         "reports", "presentation", "collaborate",
                                         "team", "liaise", "advise"}),
    ("Data practice", {"data", "database", "query", "queries", "sql", "statistics"}),
    ("Software and tools", {"software", "programming", "program", "python",
                            "javascript", "languages", "language", "code", "coding"}),
    ("Research and mathematics", {"research", "scientific", "mathematical",
                                  "mathematics", "simulation", "algorithm"}),
    ("Planning and quality", {"plan", "planning", "manage", "management", "quality",
                              "validate", "validation", "reliability", "project"}),
)


def tokens(text: str) -> set[str]:
    return {word for word in _WORDS.findall(text.casefold())
            if len(word) > 2 and word not in _STOP}


@lru_cache(maxsize=1)
def skill_descriptions() -> dict[str, dict[str, str]]:
    """Read official ESCO text directly, without an LLM or rewritten claims."""
    path = Path(__file__).with_name("skills_en.csv")
    if not path.is_file():
        return {}
    with path.open(encoding="utf-8-sig", newline="") as file:
        return {
            row["conceptUri"]: {
                "description": (row.get("description") or row.get("definition") or "").strip(),
                "skill_type": row.get("skillType", ""),
            }
            for row in csv.DictReader(file) if row.get("conceptUri")
        }


def theme_for(label: str) -> str:
    text = label.casefold()
    words = tokens(label)
    for theme, terms in THEMES:
        if any((term in text if " " in term else term in words) for term in terms):
            return theme
    return "Other occupation skills"


def clean_alternatives(value: Any, occupations: dict, *, strict=False) -> dict:
    """Validate per-target selections; preserve [] as an explicit empty set."""
    if not isinstance(value, dict) or len(value) > 50:
        if strict:
            raise ValueError("Review your career comparison choices.")
        return {}
    result = {}
    for target, choices in value.items():
        valid = (isinstance(target, str) and target in occupations
                 and isinstance(choices, list) and len(choices) <= MAX_ALTERNATIVES)
        if not valid:
            if strict:
                raise ValueError("Choose up to five real ESCO alternatives per career.")
            continue
        checked = []
        for uri in choices:
            if not isinstance(uri, str) or uri not in occupations or uri == target:
                if strict:
                    raise ValueError("Choose a different real ESCO career as an alternative.")
                continue
            if uri not in checked:
                checked.append(uri)
        result[target] = checked
    return result


def _diverse(rows: list[dict], limit=3) -> list[dict]:
    """First pass: one per label-derived theme; second pass: fill in base order."""
    selected, seen = [], set()
    for row in rows:
        if row["theme"] not in seen:
            selected.append(row)
            seen.add(row["theme"])
        if len(selected) >= limit:
            return selected
    return (selected + [r for r in rows if r not in selected])[:limit]


def build_insurance(detail: dict, confirmed: dict, occupations: dict,
                    relations: dict, state: dict | None = None) -> dict:
    state = state or {}
    target = detail["occupation"]["uri"]
    target_skills = {
        s["uri"]: s
        for key in ("matched_essential", "matched_optional", "missing_essential", "missing_optional")
        for s in detail.get(key, [])
    }
    target_ids = set(target_skills)
    confirmed_ids = set(confirmed)
    preferences = state.get("preferences", {})
    interests = preferences.get("interests", [])
    areas = preferences.get("career_areas", [])
    saved = state.get("saved_occupations", [])
    alternatives = clean_alternatives(state.get("insurance_alternatives", {}), occupations)
    career_rows, career_skills = {}, {}
    for uri, occupation in occupations.items():
        if uri == target:
            continue
        ids = {s["uri"] for kind in ("essential", "optional")
               for s in relations.get(uri, {}).get(kind, [])}
        shared = target_ids & ids
        union = target_ids | ids
        searchable = " ".join([occupation.get("label", ""),
                               occupation.get("description", ""),
                               *occupation.get("aliases", [])]).casefold()
        # Exact phrase/whole-token matches, not inferred interests.
        matched_interests = [
            i for i in interests if isinstance(i, str) and tokens(i)
            and (i.casefold() in searchable or tokens(i) <= tokens(searchable))
        ]
        area_match = occupation.get("isco_group", "")[:1] in areas
        career_rows[uri] = {
            "uri": uri, "label": occupation["label"],
            "shared_skill_count": len(shared), "target_skill_count": len(target_ids),
            "alternative_skill_count": len(ids),
            "jaccard": len(shared) / len(union) if union else 0,
            "confirmed_overlap": len(ids & confirmed_ids),
            "source": "saved_career" if uri in saved else (
                "interest_match" if matched_interests or area_match else "esco_overlap"),
            "interest_matches": matched_interests, "area_match": area_match,
        }
        career_skills[uri] = ids
    relevant = [r for r in career_rows.values()
                if r["shared_skill_count"] or r["uri"] in saved]
    relevant.sort(key=lambda r: (
        r["uri"] not in saved,
        not (r["interest_matches"] or r["area_match"]),
        -r["jaccard"], -r["confirmed_overlap"], r["label"].casefold(), r["uri"],
    ))
    manual = target in alternatives
    selected_ids = alternatives[target] if manual else [r["uri"] for r in relevant[:3]]
    selected = [{**career_rows[uri], **({"source": "user_selected"} if manual else {})}
                for uri in selected_ids]
    denominator = len(selected)
    description_data = skill_descriptions()
    context = tokens(detail["occupation"].get("label", "") + " "
                     + detail["occupation"].get("description", ""))

    def enrich(skill: dict, relation: str) -> dict:
        description = description_data.get(skill["uri"], {}).get("description", "")
        label_overlap = sorted(tokens(skill["label"]) & context)
        description_overlap = sorted(tokens(description) & context)
        other = [{"uri": row["uri"], "label": row["label"]} for row in selected
                 if skill["uri"] in career_skills[row["uri"]]]
        return {
            **skill, "relation": relation, "confirmed": False,
            "status": "Not yet confirmed", "description": description,
            "theme": theme_for(skill["label"]),
            "shared_career_count": len(other), "comparison_denominator": denominator,
            "other_careers": other,
            "why": {
                "label_overlap": label_overlap, "description_overlap": description_overlap,
                "diversity_note": "One option per label-derived heuristic theme before repeats; these themes are not official ESCO categories.",
            },
        }

    candidates = [
        enrich(s, relation)
        for key, relation in (("missing_essential", "essential"), ("missing_optional", "optional"))
        for s in detail.get(key, []) if s["uri"] not in confirmed_ids
    ]
    # Text overlap is a transparent contextual tie-break, NOT an importance,
    # competence, employability, labour demand or AI-resilience score.
    contextual_key = lambda s: (
        -len(s["why"]["label_overlap"]), -len(s["why"]["description_overlap"]),
        s["label"].casefold(), s["uri"],
    )
    essential = sorted([r for r in candidates if r["relation"] == "essential"], key=contextual_key)
    optional = sorted([r for r in candidates if r["relation"] == "optional"], key=contextual_key)
    prepare = _diverse(essential)
    if len(prepare) < 3:
        prepare += _diverse(optional, 3 - len(prepare))
    transferable = sorted([r for r in candidates if r["shared_career_count"] > 0],
                          key=lambda r: (
                              -r["shared_career_count"], r["relation"] != "essential",
                              *contextual_key(r),
                          ))
    options = _diverse(transferable)
    # Separate copies: a skill can serve both purposes without one reason
    # overwriting the other or duplicate learning goals being stored.
    prepare = [{**r, "reason":
                f"ESCO lists this as {r['relation']} for {detail['occupation']['label']}. "
                "Suggested learning option, not a compulsory employer requirement."} for r in prepare]
    options = [{**r, "reason":
                f"Listed for your target and {r['shared_career_count']} of {denominator} comparison careers. "
                "Occupational overlap, not evidence of demand."} for r in options]
    return {
        "notice": "Suggested learning options, not an objective best-skills ranking. Not yet confirmed does not mean you lack a skill.",
        "prepare": prepare, "options": options,
        "priorities": list({r["uri"]: r for r in prepare + options}.values()),
        "comparison": {
            "mode": "user_selected" if manual else "suggested", "denominator": denominator,
            "alternatives": selected,
            "suggestions": [r for r in relevant if r["uri"] not in selected_ids][:10],
            "note": "Comparison careers are editable examples, not the best alternative paths. Shared counts refer only to this set, not global demand.",
        },
        "methodology": [
            "Prepare: unconfirmed essential ESCO associations first; optional only if fewer than three essential options are available.",
            "Within each preparation tier: occupation-text token overlap with skill label, then official description, then label and URI.",
            "Options: positive exact URI overlap with the comparison set; shared count descending, essential before optional, then the same textual tie-breaks.",
            "Diversity: first choose one per disclosed label-derived theme, then fill from base order. Preparation never promotes optional above essential.",
            "Without a manual selection: saved careers first, then exact text or saved broad-area interest matches, then Jaccard, confirmed overlap, label and URI; suggest three.",
            "Manual comparison sets, including an empty set, replace defaults. No automatic confidence, competence, market or automation score is computed.",
            "Text matching and theme diversity are editorial heuristics, not validated estimates of relative learning importance.",
        ],
    }
