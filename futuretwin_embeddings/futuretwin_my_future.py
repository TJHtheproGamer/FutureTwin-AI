"""Evidence-grounded My Future career matching and skill-gap calculations."""
from __future__ import annotations

import math
import re
import sqlite3
from typing import Any

from futuretwin_occupation_api import (
    ISCO_GROUPS, explore_occupation, get_esco_occupation_catalog,
)
from futuretwin_skills_profile import public_profile

MAX_INTERESTS = 8
MAX_INTEREST_LENGTH = 80
MAX_SAVED_OCCUPATIONS = 50
MAX_ROADMAPS = 50
MAX_ROADMAP_STEPS = 300
MAX_RECOMMENDATIONS = 30
_TOKEN_RE = re.compile(r"(?u)[^\W_]+")

CAREER_AREAS = [
    {"code": code, "label": title}
    for code, (_, title) in sorted(ISCO_GROUPS.items())
]


class MyFutureValidationError(ValueError):
    """A preference, saved career, or roadmap item is not valid."""


def empty_state() -> dict[str, Any]:
    from futuretwin_sdg import clean_preferences
    return {
        "purpose": clean_preferences(None),
        "preferences": {
            "career_areas": [],
            "interests": [],
            "target_occupation_uri": None,
        },
        "saved_occupations": [],
        "roadmap_progress": {},
        "roadmap_goals": {},
        "insurance_alternatives": {},
    }


def _valid_occupation_uri(value: Any, occupations: dict[str, Any]) -> bool:
    return isinstance(value, str) and value in occupations


def validate_state(payload: Any) -> dict[str, Any]:
    """Validate state before it is added to the existing encrypted profile."""
    if not isinstance(payload, dict):
        raise MyFutureValidationError("Your My Future settings could not be saved.")
    occupations, _, skills_by_occupation = get_esco_occupation_catalog()
    preferences = payload.get("preferences", {})
    if not isinstance(preferences, dict):
        raise MyFutureValidationError("Review your career preferences and try again.")

    allowed_areas = set(ISCO_GROUPS)
    areas = preferences.get("career_areas", [])
    if not isinstance(areas, list) or len(areas) > len(allowed_areas):
        raise MyFutureValidationError("Choose valid career areas.")
    career_areas: list[str] = []
    for area in areas:
        if not isinstance(area, str) or area not in allowed_areas:
            raise MyFutureValidationError("Choose valid career areas.")
        if area not in career_areas:
            career_areas.append(area)

    interests = preferences.get("interests", [])
    if not isinstance(interests, list) or len(interests) > MAX_INTERESTS:
        raise MyFutureValidationError(f"Add up to {MAX_INTERESTS} interests.")
    clean_interests: list[str] = []
    seen_interests: set[str] = set()
    for interest in interests:
        if not isinstance(interest, str):
            raise MyFutureValidationError("Interests must be plain text.")
        interest = interest.strip()
        if len(interest) > MAX_INTEREST_LENGTH:
            raise MyFutureValidationError(
                f"Each interest must be {MAX_INTEREST_LENGTH} characters or fewer."
            )
        key = interest.casefold()
        if interest and key not in seen_interests:
            seen_interests.add(key)
            clean_interests.append(interest)

    target = preferences.get("target_occupation_uri")
    if target in ("", None):
        target = None
    elif not _valid_occupation_uri(target, occupations):
        raise MyFutureValidationError("Choose a career from ESCO search results.")

    saved = payload.get("saved_occupations", [])
    if not isinstance(saved, list) or len(saved) > MAX_SAVED_OCCUPATIONS:
        raise MyFutureValidationError(
            f"You can save up to {MAX_SAVED_OCCUPATIONS} careers."
        )
    saved_occupations: list[str] = []
    for uri in saved:
        if not _valid_occupation_uri(uri, occupations):
            raise MyFutureValidationError("Choose saved careers from ESCO search results.")
        if uri not in saved_occupations:
            saved_occupations.append(uri)
    # A selected target is also kept in the saved-career list.
    if target and target not in saved_occupations:
        if len(saved_occupations) >= MAX_SAVED_OCCUPATIONS:
            raise MyFutureValidationError(
                f"You can save up to {MAX_SAVED_OCCUPATIONS} careers."
            )
        saved_occupations.append(target)

    progress = payload.get("roadmap_progress", {})
    if not isinstance(progress, dict) or len(progress) > MAX_ROADMAPS:
        raise MyFutureValidationError("Review your learning roadmap progress and try again.")
    roadmap_progress: dict[str, list[str]] = {}
    for occupation_uri, completed in progress.items():
        if not _valid_occupation_uri(occupation_uri, occupations):
            raise MyFutureValidationError("A learning roadmap career is no longer available.")
        if not isinstance(completed, list):
            raise MyFutureValidationError("Learning progress must be a list of skill IDs.")
        if len(completed) > MAX_ROADMAP_STEPS:
            raise MyFutureValidationError("A learning roadmap has too many steps.")
        valid_skill_uris = {
            skill["uri"]
            for relation in ("essential", "optional")
            for skill in skills_by_occupation.get(
                occupation_uri, {"essential": [], "optional": []}
            )[relation]
        }
        checked: list[str] = []
        for skill_uri in completed:
            if not isinstance(skill_uri, str) or skill_uri not in valid_skill_uris:
                raise MyFutureValidationError(
                    "A learning step does not belong to this ESCO career."
                )
            if skill_uri not in checked:
                checked.append(skill_uri)
        roadmap_progress[occupation_uri] = checked

    raw_goals = payload.get("roadmap_goals", {})
    if not isinstance(raw_goals, dict) or len(raw_goals) > MAX_ROADMAPS:
        raise MyFutureValidationError("Review your learning plan goals and try again.")
    roadmap_goals: dict[str, list[str]] = {}
    for occupation_uri, selected in raw_goals.items():
        if not _valid_occupation_uri(occupation_uri, occupations):
            raise MyFutureValidationError("A learning-plan career is no longer available.")
        if not isinstance(selected, list):
            raise MyFutureValidationError("Learning goals must be a list of skill IDs.")
        if len(selected) > MAX_ROADMAP_STEPS:
            raise MyFutureValidationError("A learning plan has too many goals.")
        valid_skill_uris = {
            skill["uri"]
            for relation in ("essential", "optional")
            for skill in skills_by_occupation.get(
                occupation_uri, {"essential": [], "optional": []}
            )[relation]
        }
        goals: list[str] = []
        for skill_uri in selected:
            if not isinstance(skill_uri, str) or skill_uri not in valid_skill_uris:
                raise MyFutureValidationError(
                    "A learning goal does not belong to this ESCO career."
                )
            if skill_uri not in goals:
                goals.append(skill_uri)
        roadmap_goals[occupation_uri] = goals

    from futuretwin_career_insurance import clean_alternatives
    try:
        insurance_alternatives = clean_alternatives(
            payload.get("insurance_alternatives", {}), occupations, strict=True
        )
    except ValueError as exc:
        raise MyFutureValidationError(str(exc)) from exc
    from futuretwin_sdg import clean_preferences
    try:
        purpose = clean_preferences(payload.get("purpose"))
    except ValueError as exc:
        raise MyFutureValidationError(str(exc)) from exc
    return {
        "purpose": purpose,
        "preferences": {
            "career_areas": career_areas,
            "interests": clean_interests,
            "target_occupation_uri": target,
        },
        "saved_occupations": saved_occupations,
        "roadmap_progress": roadmap_progress,
        "roadmap_goals": roadmap_goals,
        "insurance_alternatives": insurance_alternatives,
    }


def read_state(payload: Any) -> dict[str, Any]:
    """Return a safe, backward-compatible projection of stored My Future data."""
    if not isinstance(payload, dict):
        return empty_state()
    try:
        return validate_state(payload)
    except MyFutureValidationError:
        # Keep the page usable if an old or partially written state has stale IDs.
        # The raw encrypted record is left untouched until the user saves changes.
        occupations, _, skills_by_occupation = get_esco_occupation_catalog()
        preferences = payload.get("preferences", {})
        if not isinstance(preferences, dict):
            return empty_state()
        raw_areas = preferences.get("career_areas", [])
        raw_interests = preferences.get("interests", [])
        areas = [
            value for value in (raw_areas if isinstance(raw_areas, list) else [])
            if isinstance(value, str) and value in ISCO_GROUPS
        ][:len(ISCO_GROUPS)]
        interests = [
            value.strip()[:MAX_INTEREST_LENGTH]
            for value in (raw_interests if isinstance(raw_interests, list) else [])
            if isinstance(value, str) and value.strip()
        ][:MAX_INTERESTS]
        target = preferences.get("target_occupation_uri")
        if not _valid_occupation_uri(target, occupations):
            target = None
        saved = payload.get("saved_occupations", [])
        saved = [
            uri for uri in saved
            if _valid_occupation_uri(uri, occupations)
        ][:MAX_SAVED_OCCUPATIONS] if isinstance(saved, list) else []
        if target and target not in saved:
            saved.append(target)
        progress: dict[str, list[str]] = {}
        raw_progress = payload.get("roadmap_progress", {})
        if isinstance(raw_progress, dict):
            for occupation_uri, completed in list(raw_progress.items())[:MAX_ROADMAPS]:
                if not _valid_occupation_uri(occupation_uri, occupations):
                    continue
                if not isinstance(completed, list):
                    continue
                completed = completed[:MAX_ROADMAP_STEPS]
                valid_skills = {
                    skill["uri"]
                    for relation in ("essential", "optional")
                    for skill in skills_by_occupation.get(
                        occupation_uri, {"essential": [], "optional": []}
                    )[relation]
                }
                progress[occupation_uri] = list(dict.fromkeys(
                    uri for uri in completed
                    if isinstance(uri, str) and uri in valid_skills
                ))
        goals: dict[str, list[str]] = {}
        raw_goals = payload.get("roadmap_goals", {})
        if isinstance(raw_goals, dict):
            for occupation_uri, selected in list(raw_goals.items())[:MAX_ROADMAPS]:
                if not _valid_occupation_uri(occupation_uri, occupations):
                    continue
                if not isinstance(selected, list):
                    continue
                valid_skills = {
                    skill["uri"]
                    for relation in ("essential", "optional")
                    for skill in skills_by_occupation.get(
                        occupation_uri, {"essential": [], "optional": []}
                    )[relation]
                }
                goals[occupation_uri] = list(dict.fromkeys(
                    uri for uri in selected[:MAX_ROADMAP_STEPS]
                    if isinstance(uri, str) and uri in valid_skills
                ))
        from futuretwin_career_insurance import clean_alternatives
        from futuretwin_sdg import clean_preferences
        try:
            purpose = clean_preferences(payload.get("purpose"))
        except ValueError:
            purpose = clean_preferences(None)
        return {
            "purpose": purpose,
            "preferences": {
                "career_areas": list(dict.fromkeys(areas)),
                "interests": list(dict.fromkeys(interests)),
                "target_occupation_uri": target,
            },
            "saved_occupations": list(dict.fromkeys(saved)),
            "roadmap_progress": progress,
            "roadmap_goals": goals,
            "insurance_alternatives": clean_alternatives(
                payload.get("insurance_alternatives", {}), occupations
            ),
        }


def _confirmed_skills(stored_profile: Any) -> dict[str, dict[str, str]]:
    """Use persisted, explicitly confirmed ESCO identities only."""
    if not isinstance(stored_profile, dict):
        return {}
    profile = public_profile(stored_profile)
    confirmed: dict[str, dict[str, str]] = {}
    for row in profile.get("skills", []):
        uri = row.get("selected_esco_uri")
        if not row.get("confirmed") or not isinstance(uri, str) or not uri:
            continue
        candidates = row.get("esco_candidates", [])
        candidate = next(
            (item for item in candidates if item.get("uri") == uri), {}
        )
        confirmed[uri] = {
            "uri": uri,
            "label": candidate.get("label") or row.get("value") or uri,
        }
    return confirmed


def _unique_relations(
    related: dict[str, list[dict[str, str]]]
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    essential_by_uri = {item["uri"]: item for item in related.get("essential", [])}
    optional_by_uri = {
        item["uri"]: item for item in related.get("optional", [])
        if item["uri"] not in essential_by_uri
    }
    return (
        sorted(essential_by_uri.values(), key=lambda item: item["label"].casefold()),
        sorted(optional_by_uri.values(), key=lambda item: item["label"].casefold()),
    )


def _coverage(matched_count: int, total_count: int, *, essential=None, optional=None) -> dict[str, Any]:
    breakdown = {}
    for name, pair in (("essential", essential), ("optional", optional)):
        if pair is not None:
            matched, total = pair
            breakdown[name] = {
                "matched_count": matched, "total_count": total,
                "percentage": 100 * matched / total if total else None,
            }
    if total_count <= 0:
        return {
            "status": "not_enough_data",
            "matched_count": 0,
            "total_count": 0,
            "label": "Not enough data",
            "percentage": None,
            **breakdown,
            "basis": "Validated ESCO occupation-skill relations and exact confirmed skill IDs.",
        }
    return {
        "status": "available",
        "matched_count": matched_count,
        "total_count": total_count,
        "label": f"{matched_count} of {total_count}",
        "percentage": 100 * matched_count / total_count,
        **breakdown,
        "basis": "Exact confirmed ESCO skill IDs divided by distinct listed ESCO skills.",
    }


def _add_empty_best_match_methodology(ranking, confirmed_count, specific_count):
    if ranking.get("effective") != "best_match":
        return
    from futuretwin_best_match import rank_best_match
    _, ranking["best_match"] = rank_best_match(
        [], task_inventory={}, task_metadata={},
        confirmed_count=confirmed_count, specific_count=specific_count,
    )


def _interest_matches(occupation: dict[str, Any], interests: list[str]) -> list[str]:
    searchable = " ".join([
        occupation.get("label", ""),
        occupation.get("description", ""),
        *occupation.get("aliases", []),
    ]).casefold()
    tokens = set(_TOKEN_RE.findall(searchable))
    matched: list[str] = []
    for interest in interests:
        phrase = interest.casefold().strip()
        phrase_tokens = _TOKEN_RE.findall(phrase)
        if not phrase_tokens:
            continue
        if phrase in searchable or all(token in tokens for token in phrase_tokens):
            matched.append(interest)
    return matched


def _prevalence_limit(occupation_count: int) -> int:
    """Exclude only very broad ESCO skills from candidate discovery."""
    return max(20, math.ceil(occupation_count * 0.02))


def _recommendation_ranking(sort: str) -> dict[str, Any]:
    """My Future supports only Best Match and Lower AI Exposure."""
    from futuretwin_intelligence import ranking_metadata
    ranking = ranking_metadata(sort if sort in {"best_match", "lower_exposure"} else "best_match")
    ranking["options"] = [
        option for option in ranking.get("options", [])
        if option.get("id") in {"best_match", "lower_exposure"}
    ]
    return ranking


def build_recommendations(
    stored_profile: Any,
    state: dict[str, Any] | None = None,
    limit: int = MAX_RECOMMENDATIONS,
    sort: str = "best_match",
) -> dict[str, Any]:
    """Rank occupations linked by exact confirmed ESCO skill relations."""
    from futuretwin_intelligence import hiring_unavailable
    ranking = _recommendation_ranking(sort)
    occupations, _, skills_by_occupation = get_esco_occupation_catalog()
    clean_state = read_state(state)
    confirmed = _confirmed_skills(stored_profile)
    if not confirmed:
        _add_empty_best_match_methodology(ranking, 0, 0)
        return {
            "status": "no_confirmed_skills",
            "ranking": ranking,
            "message": "Confirm skills in My Career to see careers linked to your profile.",
            "limited": True,
            "confirmed_skill_count": 0,
            "recommendations": [],
        }

    occupation_frequency: dict[str, int] = {}
    for related in skills_by_occupation.values():
        skill_uris = {
            item["uri"]
            for relation in ("essential", "optional")
            for item in related[relation]
        }
        for skill_uri in skill_uris:
            occupation_frequency[skill_uri] = occupation_frequency.get(skill_uri, 0) + 1

    prevalence_limit = _prevalence_limit(len(occupations))
    specific_uris = {
        uri for uri in confirmed
        if 0 < occupation_frequency.get(uri, 0) <= prevalence_limit
    }
    if not specific_uris and not any(
        occupation_frequency.get(uri, 0) for uri in confirmed
    ):
        _add_empty_best_match_methodology(ranking, len(confirmed), 0)
        return {
            "status": "no_occupation_links",
            "ranking": ranking,
            "message": (
                "ESCO does not list occupation links for these confirmed skills yet. "
                "You can still search for and save a career."
            ),
            "limited": True,
            "confirmed_skill_count": len(confirmed),
            "specific_skill_count": 0,
            "recommendations": [],
        }
    if not specific_uris:
        _add_empty_best_match_methodology(ranking, len(confirmed), 0)
        return {
            "status": "skills_too_broad",
            "ranking": ranking,
            "message": (
                "Your confirmed skills are too common in the ESCO data to narrow career links yet. "
                "Add a specific skill or search for a career."
            ),
            "limited": True,
            "confirmed_skill_count": len(confirmed),
            "specific_skill_count": 0,
            "prevalence_limit": prevalence_limit,
            "recommendations": [],
        }

    preferences = clean_state["preferences"]
    areas = set(preferences["career_areas"])
    interests = preferences["interests"]
    candidates: list[dict[str, Any]] = []
    for uri, occupation in occupations.items():
        if areas and occupation.get("isco_group", "")[:1] not in areas:
            continue
        related = skills_by_occupation.get(uri, {"essential": [], "optional": []})
        essential, optional = _unique_relations(related)
        all_relations = essential + optional
        if not all_relations:
            continue
        relation_by_uri = {
            skill["uri"]: ("essential" if skill in essential else "optional")
            for skill in all_relations
        }
        matched_uris = set(confirmed).intersection(relation_by_uri)
        specific_matches = matched_uris.intersection(specific_uris)
        if not specific_matches:
            continue
        matched_essential = [
            skill for skill in essential if skill["uri"] in matched_uris
        ]
        matched_optional = [
            skill for skill in optional if skill["uri"] in matched_uris
        ]
        interest_matches = _interest_matches(occupation, interests)
        total_count = len({skill["uri"] for skill in all_relations})
        matched_count = len(matched_uris)
        candidates.append({
            "uri": uri,
            "title": occupation["label"],
            "description": occupation.get("description", "")[:500],
            "isco_group": occupation.get("isco_group", ""),
            "isco_group_label": ISCO_GROUPS.get(
                occupation.get("isco_group", "")[:1], (None, None)
            )[1],
            "matched_skills": [
                {
                    "uri": skill["uri"],
                    "label": skill["label"],
                    "relation": "essential",
                }
                for skill in matched_essential
            ] + [
                {
                    "uri": skill["uri"],
                    "label": skill["label"],
                    "relation": "optional",
                }
                for skill in matched_optional
            ],
            "matched_skill_count": matched_count,
            "essential_match_count": len(matched_essential),
            "missing_essential_count": len(essential) - len(matched_essential),
            "missing_optional_count": len(optional) - len(matched_optional),
            "skill_coverage": _coverage(
                matched_count, total_count,
                essential=(len(matched_essential), len(essential)),
                optional=(len(matched_optional), len(optional)),
            ),
            "interest_matches": interest_matches,
            "why": (
                f"ESCO lists {matched_count} skill"
                f"{'' if matched_count == 1 else 's'} you confirmed for this occupation, "
                f"including {len(matched_essential)} essential."
            ),
        })

    # Keep the ranking explainable: essential overlap first, then distinct
    # exact skill links, user-interest text, and finally the coverage fraction.
    candidates.sort(
        key=lambda item: (
            -item["essential_match_count"],
            -item["matched_skill_count"],
            -len(item["interest_matches"]),
            -(item["skill_coverage"]["matched_count"] / item["skill_coverage"]["total_count"]),
            item["title"].casefold(),
            item["uri"],
        )
    )
    if ranking["effective"] == "lower_exposure":
        from fractions import Fraction
        from futuretwin_ranking_evidence import task_inventory
        try:
            inventory, _ = task_inventory()
            eligible = [item for item in candidates
                        if inventory.get(item["uri"], {}).get("lower_exposure_eligible")]
            ranking["eligible_candidate_count"] = len(eligible)
            ranking["excluded_candidate_count"] = len(candidates) - len(eligible)
            # Stable sorting preserves the existing Best Match tie-breakers.
            eligible.sort(key=lambda item: Fraction(
                inventory[item["uri"]]["e1_count"] + inventory[item["uri"]]["e2_count"],
                inventory[item["uri"]]["classified_count"],
            ))
            candidates = eligible
        except (OSError, ValueError, KeyError, RuntimeError, sqlite3.Error):
            ranking["effective"] = "best_match"
            ranking["fallback_reason"] = "Comparable task evidence became unavailable; showing Best Match."
    if ranking["effective"] == "best_match":
        from futuretwin_best_match import rank_best_match
        from futuretwin_ranking_evidence import task_inventory
        try:
            inventory, task_metadata = task_inventory()
        except (OSError, ValueError, KeyError, RuntimeError, sqlite3.Error):
            inventory, task_metadata = {}, {
                "reason": "Verified task-exposure data could not be loaded."
            }
        candidates, best_match_metadata = rank_best_match(
            candidates,
            task_inventory=inventory,
            task_metadata=task_metadata,
            confirmed_count=len(confirmed),
            specific_count=len(specific_uris),
        )
        ranking["best_match"] = best_match_metadata
    valid_limit = max(1, min(int(limit), MAX_RECOMMENDATIONS))
    limited = len(confirmed) < 3 or len(specific_uris) < 2
    if not candidates:
        message = (
            "None of your matching careers has a complete, verified task inventory for this sort. "
            "Choose Best Match to see all skill-linked careers."
            if ranking["effective"] == "lower_exposure" else
            "No occupations in the selected career areas link to these confirmed skills. "
            "Clear the area filter or search for a career."
            if areas else
            "No occupations in the current ESCO relations link to these confirmed skills. "
            "You can still search for and save a career."
        )
        return {
            "status": "no_matches",
            "ranking": ranking,
            "message": message,
            "limited": limited,
            "confirmed_skill_count": len(confirmed),
            "specific_skill_count": len(specific_uris),
            "prevalence_limit": prevalence_limit,
            "recommendations": [],
        }
    selected = candidates[:min(valid_limit, 6) if limited else valid_limit]
    from futuretwin_task_exposure import safe_occupation_exposure
    from futuretwin_ranking_evidence import career_ranking_eligibility
    for candidate in selected:
        candidate["task_exposure"] = safe_occupation_exposure(candidate["uri"], include_tasks=False)
        candidate["hiring_trend"] = hiring_unavailable()
        candidate["ranking_eligibility"] = career_ranking_eligibility(candidate["task_exposure"])
    return {
        "status": "ok",
        "ranking": ranking,
        "message": (
            "Early options based on exact ESCO skill links; add more confirmed skills "
            "for a broader comparison."
            if limited else
            "Career links use exact confirmed ESCO skill IDs and occupation-skill relations."
        ),
        "limited": limited,
        "confirmed_skill_count": len(confirmed),
        "specific_skill_count": len(specific_uris),
        "prevalence_limit": prevalence_limit,
        "recommendations": selected,
    }


def build_career_details(
    occupation_uri: str,
    stored_profile: Any,
    state: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    """Return an occupation detail view grounded in ESCO and the current baseline."""
    occupations, _, skills_by_occupation = get_esco_occupation_catalog()
    occupation = occupations.get(occupation_uri)
    if not occupation:
        return None
    clean_state = read_state(state)
    confirmed = _confirmed_skills(stored_profile)
    related = skills_by_occupation.get(
        occupation_uri, {"essential": [], "optional": []}
    )
    essential, optional = _unique_relations(related)
    matched_essential = [skill for skill in essential if skill["uri"] in confirmed]
    matched_optional = [skill for skill in optional if skill["uri"] in confirmed]
    missing_essential = [skill for skill in essential if skill["uri"] not in confirmed]
    missing_optional = [skill for skill in optional if skill["uri"] not in confirmed]
    all_skills = essential + optional
    matched_count = len(matched_essential) + len(matched_optional)
    roadmap_done = set(
        clean_state["roadmap_progress"].get(occupation_uri, [])
    )
    roadmap = [
        {
            "uri": skill["uri"],
            "label": skill["label"],
            "relation": relation,
            "completed": skill["uri"] in roadmap_done,
        }
        for relation, skills in (
            ("essential", missing_essential),
            ("optional", missing_optional),
        )
        for skill in skills
    ]

    # The existing explorer provides the current benchmark baseline and broad
    # workforce context. Missing research data must not block skill-gap details.
    try:
        existing = explore_occupation(occupation_uri) or {}
    except Exception:
        existing = {}
    ai_impact = existing.get("ai_impact") or {
        "status": "not_enough_data",
        "basis": "current_benchmark_baseline",
        "links": [],
        "task_groups": [],
        "note": "Current benchmark evidence is unavailable.",
    }
    job_demand = existing.get("job_demand") or {
        "status": "unavailable",
        "note": "Workforce context is unavailable.",
    }
    occupation_view = {
        "uri": occupation["uri"],
        "label": occupation["label"],
        "isco_group": occupation.get("isco_group", ""),
        "isco_group_label": ISCO_GROUPS.get(
            occupation.get("isco_group", "")[:1], (None, None)
        )[1],
        "description": occupation.get("description", "")[:1000],
    }
    detail = {
        "occupation": occupation_view,
        "matched_essential": matched_essential,
        "matched_optional": matched_optional,
        "missing_essential": missing_essential,
        "missing_optional": missing_optional,
        "skill_coverage": _coverage(
            matched_count, len({s["uri"] for s in all_skills}),
            essential=(len(matched_essential), len(essential)),
            optional=(len(matched_optional), len(optional)),
        ),
        "why": (
            f"{matched_count} confirmed skill"
            f"{'' if matched_count == 1 else 's'} match ESCO's listed skills for this occupation."
            if matched_count else
            "No confirmed skills match this occupation's listed ESCO skills yet."
        ),
        "learning_roadmap": roadmap,
        "roadmap_goals": clean_state["roadmap_goals"].get(occupation_uri, []),
        "saved": occupation_uri in clean_state["saved_occupations"],
        "target": clean_state["preferences"]["target_occupation_uri"] == occupation_uri,
        "interest_matches": _interest_matches(
            occupation, clean_state["preferences"]["interests"]
        ),
        "ai_impact": ai_impact,
        "task_exposure": existing.get("task_exposure", {"status": "unavailable"}),
        "job_demand": job_demand,
        "future_scenarios": future_scenario_framework(),
    }
    from futuretwin_intelligence import career_intelligence
    detail["intelligence"] = career_intelligence(detail)
    from futuretwin_career_stress import build_stress_test
    detail["stress_test"] = build_stress_test(
        detail, confirmed, occupations, skills_by_occupation, clean_state
    )
    from futuretwin_playground import build_career_map, career_experience
    detail["career_map"] = build_career_map(
        detail, confirmed, occupations, skills_by_occupation
    )
    detail["career_experience"] = career_experience(occupation, related)
    return detail


def saved_careers(state: dict[str, Any]) -> list[dict[str, Any]]:
    occupations, _, _ = get_esco_occupation_catalog()
    target = state["preferences"]["target_occupation_uri"]
    results: list[dict[str, Any]] = []
    for uri in state["saved_occupations"]:
        occupation = occupations.get(uri)
        if not occupation:
            continue
        results.append({
            "uri": uri,
            "label": occupation["label"],
            "description": occupation.get("description", "")[:300],
            "target": uri == target,
        })
    return results


def future_scenario_framework() -> dict[str, Any]:
    """Illustrative assumption slots, not personalized career forecasts."""
    return {
        "status": "illustrative_only",
        "note": (
            "These are hypothetical adoption assumptions, not predictions about this career. "
            "No role-impact or job-loss estimate is calculated."
        ),
        "assumption_source_status": "No external scenario source is configured.",
        "scenarios": [
            {
                "id": "slower_adoption",
                "label": "Slower adoption",
                "assumption": "Workplace adoption of AI tools progresses gradually.",
                "sources": [],
            },
            {
                "id": "moderate_adoption",
                "label": "Moderate adoption",
                "assumption": "Workplace adoption of AI tools progresses steadily.",
                "sources": [],
            },
            {
                "id": "faster_adoption",
                "label": "Faster adoption",
                "assumption": "Workplace adoption of AI tools progresses quickly.",
                "sources": [],
            },
        ],
    }
