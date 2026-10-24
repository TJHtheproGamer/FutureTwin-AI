"""Skills-only profile schema, source validation, and legacy-safe projection."""
from __future__ import annotations

import copy
import re
import unicodedata
from typing import Any, Callable

SCHEMA_VERSION = 2
MAX_PROFILE_ITEMS = 40
MAX_ITEM_VALUE = 2000
MAX_ITEM_EVIDENCE = 3000
ORIGINS = {"explicit", "activity_suggestion", "user_added", "legacy"}
_SPACE = re.compile(r"\s+")
# These are not skill labels. Also keep incidental academic/contact data out
# of evidence when a shorter exact skill/activity quote can support the item.
_UNRELATED = re.compile(
    r"\b(?:cgpa|gpa|university|universities|college|bachelor|diploma|"
    r"master(?:'s)?\s+(?:degree|of)|ph\.?d\.?|b\.?sc\.?|m\.?sc\.?|"
    r"b\.?eng\.?|m\.?eng\.?|degree|doctorate|date of birth|passport|"
    r"nationality|marital status)\b|[\w.+-]+@[\w.-]+\.[a-z]{2,}",
    re.IGNORECASE,
)
MatchFunction = Callable[..., list[dict[str, Any]]]


class ProfileValidationError(ValueError):
    pass


def normalise(value: str) -> str:
    return _SPACE.sub(" ", unicodedata.normalize("NFKC", value).casefold()).strip()


def _evidence_without_unrelated_details(value: str, evidence: str) -> str:
    if _UNRELATED.search(evidence):
        return value if normalise(value) in normalise(evidence) else ""
    return evidence


def validated_extraction(raw: dict[str, Any], source_text: str) -> dict[str, Any]:
    """Only source-grounded skill mentions and work activities leave this step.

    Extraction never invents an ESCO label. MiniLM suggests those later from the
    copied activity wording, and all such suggestions start unconfirmed.
    """
    source = normalise(source_text)
    skills: list[dict[str, Any]] = []
    seen: set[str] = set()
    for category, origin in (
        ("explicit_skills", "explicit"), ("work_activities", "activity_suggestion")
    ):
        rows = raw.get(category, [])
        if not isinstance(rows, list):
            raise ValueError("The extraction contains an invalid skills list.")
        for row in rows[:MAX_PROFILE_ITEMS]:
            if not isinstance(row, dict):
                continue
            value, evidence = row.get("value"), row.get("evidence")
            if not isinstance(value, str) or not isinstance(evidence, str):
                continue
            value, evidence = value.strip(), evidence.strip()
            if len(value) > MAX_ITEM_VALUE or len(evidence) > MAX_ITEM_EVIDENCE:
                continue
            v, e = normalise(value), normalise(evidence)
            if (
                not v or not e or v not in source or e not in source
                or v not in e or v in seen or _UNRELATED.search(value)
            ):
                continue
            evidence = _evidence_without_unrelated_details(value, evidence)
            seen.add(v)
            skills.append({
                "value": value, "evidence": evidence, "origin": origin,
                "selected_esco_uri": None, "confirmed": False,
            })
    # Explicit mentions take precedence when the same phrase occurs in both.
    return {"schema_version": SCHEMA_VERSION, "skills": skills[:MAX_PROFILE_ITEMS]}


def candidates_for(value: str, match: MatchFunction) -> list[dict[str, str]]:
    return [
        {"uri": item["skill_uri"], "label": item["skill"]}
        for item in match(value, top_k=3)
        if item.get("skill_uri") and item.get("skill")
    ]


def enrich_skills(skills: list[dict[str, Any]], match: MatchFunction) -> list[dict[str, Any]]:
    return [{**item, "esco_candidates": candidates_for(item["value"], match)} for item in skills]


def clean_user_profile(payload: Any, match: MatchFunction) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ProfileValidationError("Review your skills and try again.")
    rows = payload.get("skills", [])
    if not isinstance(rows, list) or len(rows) > MAX_PROFILE_ITEMS:
        raise ProfileValidationError("Your skills profile can have up to 40 items.")
    skills: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict):
            raise ProfileValidationError("One of the skills is invalid.")
        value, evidence = row.get("value", ""), row.get("evidence", "")
        if not isinstance(value, str) or not isinstance(evidence, str):
            raise ProfileValidationError("Skill text must be plain text.")
        value, evidence = value.strip(), evidence.strip()
        if not value:
            continue
        if len(value) > MAX_ITEM_VALUE or len(evidence) > MAX_ITEM_EVIDENCE:
            raise ProfileValidationError("A skill or supporting quote is too long.")
        if _UNRELATED.search(value):
            raise ProfileValidationError("Use a skill or work activity, not education or personal details.")
        origin = row.get("origin", "user_added")
        if not isinstance(origin, str) or origin not in ORIGINS:
            raise ProfileValidationError("Review the skill source and try again.")
        confirmed = row.get("confirmed", False)
        if not isinstance(confirmed, bool):
            raise ProfileValidationError("Confirm each match explicitly.")
        selected = row.get("selected_esco_uri")
        if selected is not None and not isinstance(selected, str):
            raise ProfileValidationError("Choose a valid ESCO skill match.")
        candidates = candidates_for(value, match)
        if selected and selected not in {item["uri"] for item in candidates}:
            raise ProfileValidationError("Refresh this skill's matches and choose again.")
        if confirmed and not selected:
            raise ProfileValidationError("Choose an ESCO match before confirming it.")
        experience = row.get("source") == "experience"
        if experience and not confirmed:
            raise ProfileValidationError("Confirm experience skills before saving them.")
        quote_consent = experience and row.get("evidence_consent") is True
        skills.append({
            "value": value,
            "evidence": _evidence_without_unrelated_details(value, evidence)
            if not experience or quote_consent else "",
            "origin": origin, "confirmed": confirmed,
            "selected_esco_uri": selected or None, "esco_candidates": candidates,
            **({"source": "experience", "evidence_consent": quote_consent} if experience else {}),
        })
    # Ignore old category fields sent by older clients; never add them to new profiles.
    return {"schema_version": SCHEMA_VERSION, "skills": skills}


def public_profile(stored: dict[str, Any]) -> dict[str, Any]:
    """Expose skills only. Old private categories never leave profile storage."""
    current = stored.get("schema_version") == SCHEMA_VERSION
    skills: list[dict[str, Any]] = []
    rows = stored.get("skills", [])
    for row in rows if isinstance(rows, list) else []:
        if not isinstance(row, dict) or not isinstance(row.get("value"), str):
            continue
        value = row["value"].strip()
        if not value or _UNRELATED.search(value):
            continue
        candidates = [
            {"uri": c["uri"], "label": c["label"]}
            for c in row.get("esco_candidates", [])
            if isinstance(c, dict) and isinstance(c.get("uri"), str)
            and isinstance(c.get("label"), str)
        ] if isinstance(row.get("esco_candidates", []), list) else []
        selected = row.get("selected_esco_uri")
        selected = selected if isinstance(selected, str) and selected in {c["uri"] for c in candidates} else None
        origin = row.get("origin") if current else "legacy"
        evidence = row.get("evidence", "")
        evidence = evidence if isinstance(evidence, str) else ""
        skills.append({
            "value": value,
            "evidence": _evidence_without_unrelated_details(value, evidence),
            "origin": origin if isinstance(origin, str) and origin in ORIGINS else "legacy",
            "esco_candidates": candidates, "selected_esco_uri": selected,
            "confirmed": bool(current and row.get("confirmed") is True and selected),
            **({"source": "experience", "evidence_consent": row.get("evidence_consent") is True}
               if row.get("source") == "experience" else {}),
        })
    legacy = bool(stored.get("_legacy_profile")) or (
        not current and any(key != "skills" for key in stored)
    )
    result = {"schema_version": SCHEMA_VERSION, "skills": skills, "has_legacy_data": legacy}
    for key in ("created_at", "updated_at"):
        if key in stored:
            result[key] = stored[key]
    return result


def merge_stored_profile(previous: dict[str, Any], reviewed: dict[str, Any]) -> dict[str, Any]:
    """Archive legacy data inside the same encrypted payload, never overwrite it."""
    if previous and previous.get("schema_version") != SCHEMA_VERSION:
        result = {"_legacy_profile": copy.deepcopy(previous)}
        if isinstance(previous.get("my_future"), dict):
            # Keep the new dashboard state addressable if a legacy skills
            # profile is upgraded after preferences or roadmap progress exist.
            result["my_future"] = copy.deepcopy(previous["my_future"])
    else:
        result = copy.deepcopy(previous)
    result.update({"schema_version": SCHEMA_VERSION, "skills": copy.deepcopy(reviewed["skills"])})
    return result


def append_confirmed_skills(
    previous: dict[str, Any], reviewed: dict[str, Any], *, confirm_existing: bool = False
) -> tuple[dict[str, Any], int, int]:
    """Append by ESCO identity or wording, without replacing saved/legacy data."""
    existing = (
        previous.get("skills", []) if previous.get("schema_version") == SCHEMA_VERSION
        else public_profile(previous)["skills"]
    )
    combined = copy.deepcopy(existing)
    words = {normalise(item["value"]) for item in existing}
    uris = {item.get("selected_esco_uri") for item in existing if item.get("selected_esco_uri")}
    added = duplicates = 0
    for item in reviewed["skills"]:
        if not item.get("confirmed") or not item.get("selected_esco_uri"):
            raise ProfileValidationError("Confirm each new skill before saving.")
        word, uri = normalise(item["value"]), item["selected_esco_uri"]
        existing_match = next(
            (row for row in combined if row.get("selected_esco_uri") == uri), None
        )
        if confirm_existing and existing_match is not None and not existing_match.get("confirmed"):
            # An explicit Passport action may confirm a pending exact identity.
            # Preserve its original wording, evidence and source information.
            existing_match["confirmed"] = True
            candidates = existing_match.setdefault("esco_candidates", [])
            if not any(candidate.get("uri") == uri for candidate in candidates):
                candidates.extend(copy.deepcopy(item["esco_candidates"]))
            added += 1
            continue
        if (not confirm_existing and word in words) or uri in uris:
            duplicates += 1
            continue
        combined.append(copy.deepcopy(item))
        words.add(word)
        uris.add(uri)
        added += 1
    if len(combined) > MAX_PROFILE_ITEMS:
        raise ProfileValidationError("Your skills profile can have up to 40 items. Remove an item first.")
    return merge_stored_profile(previous, {"skills": combined}), added, duplicates
