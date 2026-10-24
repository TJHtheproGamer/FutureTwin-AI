"""Observed ad-sample candidates, not forecasts or inferred hiring growth."""
from __future__ import annotations

from collections import defaultdict
from functools import lru_cache
import re
from time import time

from futuretwin_intelligence import hiring_unavailable, safe_url


def _normal_title(value):
    from futuretwin_job_matching import normalize_title
    return normalize_title(value)


def explicit_quote(label, text):
    """Require an actual named term; semantic similarity alone is insufficient."""
    term = re.sub(r"\([^)]*\)", "", label).strip()
    tokens = re.findall(r"[\w]+", term)
    if not tokens or (len(tokens) == 1 and len(tokens[0]) < 2):
        return None
    found = re.search(r"(?<!\w)" + r"\W+".join(map(re.escape, tokens)) + r"(?!\w)",
                      text, re.IGNORECASE)
    if not found:
        return None
    return " ".join(text[max(0, found.start() - 70):found.end() + 100].split())


@lru_cache(maxsize=2)
def _sample(bucket):
    from jobmarket_store import _rows
    postings = _rows("""
        SELECT source,source_posting_id,title,country,location,remote,
               posted_date,url,
               LEFT(description_text,20000) AS description_text,collected_at
        FROM job_postings WHERE duplicate_of IS NULL
        ORDER BY collected_at DESC,source,source_posting_id LIMIT 5000
    """)
    mentions = _rows("""
        SELECT source,source_posting_id,skill_uri,skill,cosine_similarity
        FROM job_posting_skills
    """)
    return postings, mentions


def _collection_windows():
    """Latest successful collection window by ad source, not posting-date range."""
    from jobmarket_store import _rows
    try:
        rows = _rows("""
            SELECT DISTINCT ON (source) source, started_at, finished_at
            FROM jobmarket_collection_log
            WHERE source IN (
                'remoteok','remotive','himalayas','greenhouse','lever'
            ) AND status='ok'
            ORDER BY source, finished_at DESC
        """)
    except Exception:
        return []
    return [{
        "source": row["source"],
        "started_at": str(row["started_at"]),
        "finished_at": str(row["finished_at"]),
    } for row in rows]


def _iso(value):
    return value.isoformat() if hasattr(value, "isoformat") else str(value or "")


def _posting_evidence(ad, matching_method, **extra):
    return {
        "source": ad.get("source") or "",
        "title": ad.get("title") or "",
        "url": safe_url(ad.get("url")),
        "posted_date": _iso(ad.get("posted_date")),
        "country": ad.get("country") or "",
        "location": ad.get("location") or "",
        "remote": ad.get("remote"),
        "matching_method": matching_method,
        **extra,
    }


def _derive_candidates(postings, mentions, occupations, relations):
    """Share deterministic title/skill evidence logic between API and snapshots."""
    ads = {(p["source"], p["source_posting_id"]): p for p in postings}
    skills = {}
    careers_by_skill = defaultdict(dict)
    exact_titles = defaultdict(dict)
    from futuretwin_job_matching import GENERIC_ALIASES
    for uri, occupation in occupations.items():
        preferred = _normal_title(occupation["label"])
        if preferred:
            exact_titles[preferred][uri] = "normalized_exact_preferred_title"
        for alias in occupation.get("aliases", []):
            normalized = _normal_title(alias)
            if (normalized and normalized not in GENERIC_ALIASES
                    and uri not in exact_titles[normalized]):
                exact_titles[normalized][uri] = "normalized_exact_alternate_title"
        for kind in ("essential", "optional"):
            for skill in relations.get(uri, {}).get(kind, []):
                skill_uri = skill.get("uri") or skill.get("skill_uri")
                if not skill_uri:
                    continue
                skills[skill_uri] = {
                    "uri": skill_uri,
                    "label": skill.get("label") or skill.get("skill") or skill_uri,
                }
                previous = careers_by_skill[skill_uri].get(uri)
                if previous is None or kind == "essential":
                    careers_by_skill[skill_uri][uri] = kind

    explicit_by_ad = defaultdict(dict)
    evidence_by_skill = defaultdict(dict)
    for row in mentions:
        key = (row["source"], row["source_posting_id"])
        ad = ads.get(key)
        skill = skills.get(row.get("skill_uri"))
        if not ad or not skill:
            continue
        quote = explicit_quote(
            skill["label"],
            f'{ad.get("title", "")}\n{ad.get("description_text", "")}',
        )
        if quote is None:
            continue
        match = {
            **skill,
            "quote": quote,
            "cosine_similarity": float(row.get("cosine_similarity") or 0),
        }
        explicit_by_ad[key][skill["uri"]] = match
        evidence_by_skill[skill["uri"]][key] = _posting_evidence(
            ad,
            "ESCO skill candidate plus literal term found in the original ad",
            skill_uri=skill["uri"],
            skill_label=skill["label"],
            evidence_quote=quote,
            cosine_similarity=match["cosine_similarity"],
        )

    title_by_career = defaultdict(dict)
    title_skills_by_career = defaultdict(dict)
    skill_by_career = defaultdict(dict)
    skill_candidates_by_career = defaultdict(dict)
    specificity_limit = max(20, round(len(occupations) * 0.02))
    for key, ad in ads.items():
        exact_title_matches = exact_titles.get(_normal_title(ad.get("title", "")), {})
        exact_uri = next(iter(exact_title_matches)) if len(exact_title_matches) == 1 else None
        if exact_uri:
            code = exact_title_matches[exact_uri]
            title_by_career[exact_uri][key] = _posting_evidence(
                ad,
                ("Normalized exact match to ESCO preferred occupation title"
                 if code == "normalized_exact_preferred_title"
                 else "Normalized exact match to ESCO alternate occupation title"),
                mapping_method=code,
            )
            for skill_uri, skill in explicit_by_ad[key].items():
                title_skills_by_career[exact_uri][skill_uri] = {
                    "uri": skill_uri,
                    "label": skill["label"],
                }

        counts = defaultdict(dict)
        for skill_uri in explicit_by_ad[key]:
            if len(careers_by_skill[skill_uri]) <= specificity_limit:
                for uri, relation in careers_by_skill[skill_uri].items():
                    counts[uri][skill_uri] = relation
        eligible = {
            uri: associated for uri, associated in counts.items()
            if len(associated) >= 2
        }
        for uri, associated in eligible.items():
            matched = [
                {
                    "uri": skill_uri,
                    "label": explicit_by_ad[key][skill_uri]["label"],
                    "relation": relation,
                    "evidence_quote": explicit_by_ad[key][skill_uri]["quote"],
                }
                for skill_uri, relation in sorted(
                    associated.items(),
                    key=lambda item: (
                        explicit_by_ad[key][item[0]]["label"].casefold(),
                        item[0],
                    ),
                )
            ]
            quote = " · ".join(skill["evidence_quote"] for skill in matched)
            skill_by_career[uri][key] = _posting_evidence(
                ad,
                "ESCO skill links plus 2 or more explicitly named ESCO skill terms",
                supporting_skills=matched,
                supporting_skill_count=len(matched),
                evidence_quote=quote,
            )
            for item in matched:
                skill_candidates_by_career[uri][item["uri"]] = {
                    "uri": item["uri"],
                    "label": item["label"],
                    "relation": item["relation"],
                }

    return {
        "ads": ads,
        "skills": skills,
        "careers_by_skill": careers_by_skill,
        "explicit_by_ad": explicit_by_ad,
        "evidence_by_skill": evidence_by_skill,
        "title_by_career": title_by_career,
        "title_skills_by_career": title_skills_by_career,
        "skill_by_career": skill_by_career,
        "skill_candidates_by_career": skill_candidates_by_career,
    }


def build_opportunities(postings, mentions, occupations, relations, limit=12,
                        collection_windows=None):
    """Return direct title evidence and separate ESCO skill-related suggestions."""
    valid_limit = max(1, min(int(limit), 30))
    derived = _derive_candidates(postings, mentions, occupations, relations)
    ads = derived["ads"]
    skills = derived["skills"]
    title_by_career = derived["title_by_career"]
    title_skills_by_career = derived["title_skills_by_career"]
    skill_by_career = derived["skill_by_career"]
    skill_candidates_by_career = derived["skill_candidates_by_career"]
    evidence_by_skill = derived["evidence_by_skill"]

    job_order = sorted(
        title_by_career,
        key=lambda uri: (occupations[uri]["label"].casefold(), uri),
    )
    job_postings = [{
        "uri": uri,
        "title": occupations[uri]["label"],
        "category": "direct_title_match",
        "matching_method": "Normalized exact match to ESCO preferred occupation title",
        "hiring_trend": hiring_unavailable(),
        "matched_skills": sorted(
            title_skills_by_career[uri].values(),
            key=lambda skill: (skill["label"].casefold(), skill["uri"]),
        ),
        "sample_supporting_ads": len(title_by_career[uri]),
        "title_candidate_count": len(title_by_career[uri]),
        "evidence": list(title_by_career[uri].values())[:4],
    } for uri in job_order[:valid_limit]]

    title_uris = set(title_by_career)
    candidate_uris = set(skill_by_career) - title_uris
    skill_career_order = sorted(
        candidate_uris,
        key=lambda uri: (occupations[uri]["label"].casefold(), uri),
    )
    skill_related_careers = [{
        "uri": uri,
        "title": occupations[uri]["label"],
        "category": "skill_related_career_candidate",
        "matching_method": (
            "ESCO skill links plus 2 or more explicitly named ESCO skill terms"
        ),
        "not_a_job_opening": True,
        "sample_supporting_ads": len(skill_by_career[uri]),
        "supporting_skills": sorted(
            skill_candidates_by_career[uri].values(),
            key=lambda skill: (skill["label"].casefold(), skill["uri"]),
        ),
        "evidence": list(skill_by_career[uri].values())[:4],
    } for uri in skill_career_order[:valid_limit]]

    skill_order = sorted(
        evidence_by_skill,
        key=lambda uri: (skills[uri]["label"].casefold(), uri),
    )
    skill_results = []
    for skill_uri in skill_order[:valid_limit]:
        related = []
        for uri in skill_career_order:
            candidate = skill_candidates_by_career[uri].get(skill_uri)
            if candidate:
                matching_ads = [
                    evidence for evidence in skill_by_career[uri].values()
                    if any(item["uri"] == skill_uri
                           for item in evidence["supporting_skills"])
                ]
                related.append({
                    "uri": uri,
                    "title": occupations[uri]["label"],
                    "relation": candidate["relation"],
                    "category": "skill_related_career_candidate",
                    "not_a_job_opening": True,
                    "matching_method": (
                        "ESCO occupation-skill link; multi-skill ad evidence"
                    ),
                    "sample_supporting_ads": len(matching_ads),
                })
        n = len(evidence_by_skill[skill_uri])
        skill_results.append({
            "uri": skill_uri, "label": skills[skill_uri]["label"],
            "category": "explicit_skill_mention", "demand_change_pp": None,
            "sample_mentions": n, "sample_postings": len(ads),
            "sample_share_pct": 100 * n / len(ads) if ads else None,
            "matching_method": (
                "ESCO skill candidate plus literal term found in original ad text"
            ),
            "related_careers": related[:6],
            "evidence": list(evidence_by_skill[skill_uri].values())[:4],
        })

    source_counts = defaultdict(int)
    for ad in ads.values():
        source_counts[ad["source"]] += 1
    dates = sorted(str(p["posted_date"]) for p in ads.values() if p.get("posted_date"))
    collected = sorted({str(p.get("collected_at") or "")[:10] for p in ads.values()})
    title_matched_ad_keys = {
        key for rows in title_by_career.values() for key in rows
    }
    skill_related_ad_keys = {
        key for uri in candidate_uris for key in skill_by_career[uri]
    }
    collection_days = [day for day in collected if day]
    windows = collection_windows or []
    supported_uris = title_uris | set(skill_by_career)
    counts = {
        "title_matched_ad_count": len(title_matched_ad_keys),
        "skill_related_career_candidate_count": len(candidate_uris),
        "skill_related_ad_count": len(skill_related_ad_keys),
        "explicit_skill_count": len(evidence_by_skill),
        "supported_esco_occupation_count": len(supported_uris),
    }
    return {
        "status": (
            "available" if job_postings or skill_results or skill_related_careers
            else "not_enough_data"
        ),
        "counts": counts,
        "job_postings": job_postings,
        "jobs": job_postings,
        "growing_careers": {
            "status": "not_enough_data",
            "reason": (
                "Comparable repeated collection periods are not available; "
                "no hiring-growth ranking is shown."
            ),
            "items": [],
        },
        "skill_related_careers": skill_related_careers,
        "skills": skill_results,
        "coverage": {
            "posting_count": len(ads), "sources": dict(source_counts),
            "first_posted_date": dates[0] if dates else None,
            "last_posted_date": dates[-1] if dates else None,
            "posting_date_range": {
                "first": dates[0] if dates else None,
                "last": dates[-1] if dates else None,
            },
            "collection_days": collection_days,
            "collection_day_count": len(collection_days),
            "collection_windows": windows,
            "geography": "Mixed advertised locations/remote; not a Malaysia-wide vacancy census.",
            "longitudinal_comparison_supported": False,
        },
        "categories": [
            {"id": category, "status": "not_enough_data",
             "reason": "Requires comparable repeated collection periods and consistent source coverage."}
            for category in ("newly_observed_roles", "growing_existing_roles", "changing_skill_requirements")
        ] + [
            {"id": "job_postings",
             "status": "available" if job_postings else "not_enough_data"},
            {"id": "growing_careers", "status": "not_enough_data"},
            {"id": "skills_in_job_ads",
             "status": "available" if skill_results else "not_enough_data"},
        ],
        "methodology": [
            "Exact ESCO occupation matching checks normalized preferred and alternate titles after removing common seniority/level modifiers.",
            "Fine-tuned MiniLM occupation matches are separate semantic suggestions, not verified ESCO links.",
            "Skill mentions require an ESCO candidate term to appear literally in the original ad; MiniLM similarity alone is not evidence.",
            "Skill-related career suggestions require at least two explicit, specific ESCO skill terms linked to an occupation; they are not job openings.",
            "Career and skill lists are alphabetical, not ranked by hiring demand or expected growth.",
            "Posting dates describe the original ads. Collection dates/windows describe when the sample was retrieved.",
            "Growth remains unavailable until repeated, comparable collection windows support a valid comparison.",
            "ESCO skill links do not establish employability, personal experience, or proficiency.",
        ],
    }


def record_run_matches(conn, run_id):
    """Persist real title/skill evidence for one just-recorded collection batch."""
    from futuretwin_occupation_api import get_esco_occupation_catalog
    import jobmarket_store

    with conn.cursor() as cur:
        cur.execute("""
            SELECT o.source, o.source_posting_id, o.title, o.country,
                   o.location, o.remote, o.original_posted_date AS posted_date,
                   p.url, p.description_text, o.observed_at AS collected_at
            FROM job_posting_observations o
            JOIN job_postings p USING (source, source_posting_id)
            WHERE o.run_id = %s AND o.duplicate_of IS NULL
        """, (run_id,))
        columns = [item.name for item in cur.description]
        postings = [dict(zip(columns, row)) for row in cur.fetchall()]
        cur.execute("""
            SELECT s.source, s.source_posting_id, s.skill_uri, s.skill,
                   s.cosine_similarity
            FROM job_posting_skills s
            JOIN job_posting_observations o USING (source, source_posting_id)
            WHERE o.run_id = %s AND o.duplicate_of IS NULL
        """, (run_id,))
        columns = [item.name for item in cur.description]
        mentions = [dict(zip(columns, row)) for row in cur.fetchall()]

    if not postings:
        return {"skills": 0, "occupations": 0, "suggestions": 0}
    occupations, _, relations = get_esco_occupation_catalog()
    derived = _derive_candidates(postings, mentions, occupations, relations)
    skill_rows = []
    for key, matched in derived["explicit_by_ad"].items():
        for skill_uri, skill in matched.items():
            skill_rows.append({
                "run_id": run_id,
                "source": key[0],
                "source_posting_id": key[1],
                "skill_uri": skill_uri,
                "skill_label": skill["label"],
                "matched_term": skill["label"],
                "evidence_quote": skill["quote"],
                "cosine_similarity": skill["cosine_similarity"],
                "matching_method": (
                    "ESCO MiniLM candidate plus literal phrase verification"
                ),
            })
    occupation_rows = []
    for uri, evidence_by_ad in derived["title_by_career"].items():
        for key, evidence in evidence_by_ad.items():
            occupation_rows.append({
                "run_id": run_id,
                "source": key[0],
                "source_posting_id": key[1],
                "occupation_uri": uri,
                "mapping_method": evidence.get("mapping_method", evidence["matching_method"]),
                "supporting_skill_uris": [],
                "evidence_quote": evidence["title"],
            })
    for uri, evidence_by_ad in derived["skill_by_career"].items():
        for key, evidence in evidence_by_ad.items():
            occupation_rows.append({
                "run_id": run_id,
                "source": key[0],
                "source_posting_id": key[1],
                "occupation_uri": uri,
                "mapping_method": "esco_skill_relations_two_plus_explicit_terms",
                "supporting_skill_uris": [
                    item["uri"] for item in evidence["supporting_skills"]
                ],
                "evidence_quote": evidence["evidence_quote"],
            })
    exact_keys = {
        key for evidence_by_ad in derived["title_by_career"].values()
        for key in evidence_by_ad
    }
    semantic_postings = [
        posting for posting in postings
        if (posting["source"], posting["source_posting_id"]) not in exact_keys
    ]
    from datetime import datetime, timezone
    from futuretwin_job_matching import semantic_candidates_batch
    candidate_sets, model_signature = semantic_candidates_batch(
        semantic_postings, derived["explicit_by_ad"], top_k=3
    )
    suggestion_rows = []
    from futuretwin_job_text import relevant_responsibilities
    predicted_at = datetime.now(timezone.utc)
    for posting, candidates in zip(semantic_postings, candidate_sets):
        key = (posting["source"], posting["source_posting_id"])
        for candidate in candidates:
            suggestion_rows.append({
                "source": key[0],
                "source_posting_id": key[1],
                "occupation_uri": candidate["uri"],
                "model_signature": model_signature,
                "candidate_rank": candidate["candidate_rank"],
                "cosine_similarity": candidate["cosine_similarity"],
                "supporting_skill_uris": candidate["supporting_skill_uris"],
                "evidence_quote": (
                    posting.get("title", "") + "\n" +
                    relevant_responsibilities(posting.get("description_text"))[:900]
                ),
                "predicted_at": predicted_at,
            })
    return {
        "skills": jobmarket_store.save_posting_skill_observations(conn, skill_rows),
        "occupations": jobmarket_store.save_posting_occupation_matches(
            conn, occupation_rows),
        "suggestions": jobmarket_store.save_posting_occupation_suggestions(
            conn, suggestion_rows),
    }


def opportunity_radar(limit=12):
    from futuretwin_occupation_api import get_esco_occupation_catalog
    occupations, _, relations = get_esco_occupation_catalog()
    try:
        postings, mentions = _sample(int(time() // 300))
        windows = _collection_windows()
    except Exception:
        return {
            "status": "unavailable", "counts": {}, "jobs": [],
            "job_postings": [], "growing_careers": {
                "status": "unavailable", "items": [],
            }, "skill_related_careers": [], "skills": [], "coverage": {},
            "categories": [], "methodology": [],
            "reason": "Stored vacancy observations are unavailable; no substitute data was generated.",
        }
    return build_opportunities(
        postings, mentions, occupations, relations, limit,
        collection_windows=windows,
    )
