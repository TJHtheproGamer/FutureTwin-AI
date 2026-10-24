"""Evidence-backed job listings filtered against a browser's confirmed Passport."""
from __future__ import annotations

import json
import re
from datetime import date, datetime
from decimal import Decimal

from futuretwin_job_matching import (
    classify_semantic_candidates,
    build_title_index,
    exact_title_matches,
)
from futuretwin_intelligence import safe_url
from futuretwin_occupation_api import get_esco_occupation_catalog
from jobmarket_store import _rows
from futuretwin_job_text import plain_job_text, relevant_responsibilities


SOURCE_LABELS = {
    "himalayas": "Himalayas",
    "remoteok": "Remote OK",
    "remotive": "Remotive",
    "greenhouse": "Greenhouse",
    "lever": "Lever",
}


def _json_list(value):
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
            return parsed if isinstance(parsed, list) else []
        except json.JSONDecodeError:
            return []
    return []


def _date(value):
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return str(value) if value else None


def _number(value):
    if isinstance(value, Decimal):
        return float(value)
    return float(value) if isinstance(value, (int, float)) else None


def _posting_rows():
    return _rows("""
        SELECT p.source, p.source_posting_id, p.title, p.employer,
               p.country, p.location, p.remote, p.workplace_type, p.category,
               p.posted_date, p.source_updated_at, p.url,
               p.description_text AS description,
               p.seniority, p.employment_type, p.salary_min, p.salary_max,
               p.salary_currency, p.salary_period, p.salary_text,
               p.collected_at,
               COALESCE((
                 SELECT jsonb_agg(jsonb_build_object(
                   'uri', latest.skill_uri, 'label', latest.skill_label,
                   'evidence_quote', latest.evidence_quote,
                   'cosine_similarity', latest.cosine_similarity
                 ))
                 FROM (
                   SELECT DISTINCT ON (s.skill_uri)
                          s.skill_uri, s.skill_label, s.evidence_quote,
                          s.cosine_similarity
                   FROM job_posting_skill_observations s
                   JOIN job_posting_observations o
                     ON o.run_id = s.run_id
                    AND o.source = s.source
                    AND o.source_posting_id = s.source_posting_id
                   WHERE s.source = p.source
                     AND s.source_posting_id = p.source_posting_id
                   ORDER BY s.skill_uri, o.observed_at DESC
                 ) latest
               ), '[]'::jsonb) AS explicit_skills,
               COALESCE((
                 SELECT jsonb_agg(jsonb_build_object(
                   'uri', latest.occupation_uri,
                   'method', latest.mapping_method,
                   'evidence_quote', latest.evidence_quote
                 ))
                 FROM (
                   SELECT DISTINCT ON (m.occupation_uri, m.mapping_method)
                          m.occupation_uri, m.mapping_method, m.evidence_quote
                   FROM job_posting_occupation_matches m
                   JOIN job_posting_observations o
                     ON o.run_id = m.run_id
                    AND o.source = m.source
                    AND o.source_posting_id = m.source_posting_id
                   WHERE m.source = p.source
                     AND m.source_posting_id = p.source_posting_id
                     AND m.mapping_method IN (
                       'normalized_exact_preferred_title',
                       'normalized_exact_alternate_title'
                     )
                   ORDER BY m.occupation_uri, m.mapping_method,
                            o.observed_at DESC
                 ) latest
               ), '[]'::jsonb) AS exact_matches,
               COALESCE((
                 SELECT jsonb_agg(jsonb_build_object(
                   'uri', latest.occupation_uri,
                   'cosine_similarity', latest.cosine_similarity,
                   'candidate_rank', latest.candidate_rank,
                   'supporting_skill_uris', latest.supporting_skill_uris,
                   'evidence_quote', latest.evidence_quote
                 ) ORDER BY latest.candidate_rank)
                 FROM (
                   SELECT DISTINCT ON (s.occupation_uri)
                          s.occupation_uri, s.cosine_similarity,
                          s.candidate_rank, s.supporting_skill_uris,
                          s.evidence_quote
                   FROM job_posting_occupation_suggestions s
                   WHERE s.source = p.source
                     AND s.source_posting_id = p.source_posting_id
                     AND s.model_signature = (
                       SELECT newest.model_signature
                       FROM job_posting_occupation_suggestions newest
                       WHERE newest.source = p.source
                         AND newest.source_posting_id = p.source_posting_id
                       ORDER BY newest.predicted_at DESC LIMIT 1
                     )
                   ORDER BY s.occupation_uri, s.predicted_at DESC
                 ) latest
               ), '[]'::jsonb) AS semantic_matches
        FROM job_postings p
        WHERE p.duplicate_of IS NULL
          AND (p.expires_at IS NULL OR p.expires_at > NOW())
        ORDER BY p.posted_date DESC NULLS LAST,
                 p.source_updated_at DESC NULLS LAST,
                 p.collected_at DESC
        LIMIT 3000
    """)


def search_job_postings(
    *,
    q: str = "",
    occupation: str = "",
    location: str = "",
    workplace: str = "",
    skill: str = "",
    skill_uri: str = "",
    confirmed_skills: dict | None = None,
    limit: int = 30,
) -> dict:
    """Return real postings; only exact title matches are described as exact."""
    occupations, _, _ = get_esco_occupation_catalog()
    title_index = build_title_index(occupations)
    confirmed_skills = confirmed_skills or {}
    confirmed = {
        uri: {"uri": uri, "label": row.get("label") or uri}
        for uri, row in confirmed_skills.items()
    }
    q = q.strip().casefold()
    occupation = occupation.strip().casefold()
    location = location.strip().casefold()
    skill = skill.strip().casefold()
    workplace = workplace.strip().casefold()
    results = []
    rows = _posting_rows()

    for raw in rows:
        title = str(raw.get("title") or "")
        employer = str(raw.get("employer") or "")
        description = plain_job_text(raw.get("description"))
        # Keep questionable source rows in storage/history, but do not
        # recommend obvious placeholder titles as genuine opportunities.
        if (not title.strip() or not employer.strip()
                or re.fullmatch(r"[b-df-hj-np-tv-xz]{8,}", title.casefold())
                or not safe_url(raw.get("url"))):
            continue
        place = " ".join(str(raw.get(key) or "")
                         for key in ("location", "country")).strip()
        # Free-text job discovery is title/company search, not arbitrary
        # boilerplate or application-instruction matching deep in an ad.
        haystack = f"{title} {employer}".casefold()
        if q and q not in haystack:
            continue
        if location and location not in place.casefold():
            continue
        if workplace == "remote" and raw.get("remote") is not True:
            continue
        if workplace == "non_remote" and raw.get("remote") is not False:
            continue

        exact_matches = _json_list(raw.get("exact_matches"))
        sem_matches = _json_list(raw.get("semantic_matches"))
        # Recheck against today's catalog and conservative alias rules rather
        # than trusting stale assignments from earlier matching versions.
        exact_candidates = [
            {**item, "status": "exact_title"}
            for item in exact_title_matches(title, occupations, title_index)
        ]
        if len(exact_candidates) > 1:
            exact_candidates = []

        semantic_candidates = []
        if sem_matches:
            enriched = []
            for item in sem_matches:
                uri = item.get("uri")
                if uri not in occupations:
                    continue
                enriched.append({
                    **item,
                    "label": occupations[uri]["label"],
                    "method": "fine_tuned_minilm_semantic_candidate",
                    "cosine_similarity": _number(item.get("cosine_similarity")) or 0.0,
                    "supporting_skill_uris": _json_list(
                        item.get("supporting_skill_uris")),
                })
            semantic_candidates = classify_semantic_candidates(enriched)

        if exact_candidates:
            occupation_match = exact_candidates[0]
        elif semantic_candidates:
            top = semantic_candidates[0]
            occupation_match = {
                **top,
                "status": "semantic_suggested" if top["status"] == "suggested"
                          else "uncertain_suggestion",
            }
        else:
            occupation_match = None

        if occupation:
            labels = [title]
            if occupation_match:
                labels.append(occupation_match.get("label", ""))
            if not any(occupation in label.casefold() for label in labels):
                continue

        explicit = _json_list(raw.get("explicit_skills"))
        ad_skill_uris = {
            str(item.get("uri")) for item in explicit if item.get("uri")
        }
        if skill and not any(
            skill in str(item.get("label") or "").casefold()
            for item in explicit
        ):
            continue
        if skill_uri and skill_uri not in ad_skill_uris:
            continue
        matched_skills = [
            item for uri, item in confirmed.items() if uri in ad_skill_uris
        ]
        unmentioned_confirmed = [
            item for uri, item in confirmed.items() if uri not in ad_skill_uris
        ]
        ad_skills_not_in_passport = [
            {
                "uri": item.get("uri"),
                "label": item.get("label"),
                "evidence_quote": item.get("evidence_quote"),
            }
            for item in explicit
            if item.get("uri") not in confirmed
        ]

        results.append({
            "source": raw.get("source"),
            "source_label": SOURCE_LABELS.get(raw.get("source"), raw.get("source")),
            "source_posting_id": raw.get("source_posting_id"),
            "title": title,
            "employer": employer,
            "country": raw.get("country") or "",
            "location": raw.get("location") or "",
            "remote": raw.get("remote"),
            "workplace_type": raw.get("workplace_type") or "unspecified",
            "category": raw.get("category") or "",
            "posted_date": _date(raw.get("posted_date")),
            "source_updated_at": _date(raw.get("source_updated_at")),
            "collected_at": _date(raw.get("collected_at")),
            "url": safe_url(raw.get("url")),
            "description": description[:700],
            "matching_text": relevant_responsibilities(description)[:900],
            "seniority": raw.get("seniority") or "",
            "employment_type": raw.get("employment_type") or "",
            "salary_min": _number(raw.get("salary_min")),
            "salary_max": _number(raw.get("salary_max")),
            "salary_currency": raw.get("salary_currency") or "",
            "salary_period": raw.get("salary_period") or "",
            "salary_text": raw.get("salary_text") or "",
            "occupation_match": occupation_match,
            "semantic_candidates": semantic_candidates[:3],
            "explicit_skills": explicit,
            "matched_passport_skills": matched_skills,
            "passport_skills_not_mentioned": unmentioned_confirmed,
            "ad_skills_not_in_passport": ad_skills_not_in_passport,
            "confirmed_skill_match_count": len(matched_skills),
        })

    # This orders evidence-based exact Passport skill mentions first, then
    # recent source dates. It is not a qualification or suitability score.
    results.sort(key=lambda row: (
        row["posted_date"] or row["source_updated_at"] or "",
        row["source_label"].casefold(),
    ), reverse=True)
    results.sort(key=lambda row: row["confirmed_skill_match_count"], reverse=True)
    return {
        "status": "available" if results else "no_matches",
        "count": len(results),
        "returned": min(limit, len(results)),
        "confirmed_skill_count": len(confirmed),
        "personalization_status": (
            "passport_skill_evidence" if confirmed else "no_confirmed_skills"
        ),
        "note": (
            "Passport matches require an exact ESCO URI and literal wording in "
            "the ad. Skills not mentioned in an ad are unknown, not absent."
        ),
        "postings": results[:limit],
    }
