"""FutureTwin Phase 2: job-market evidence source registry.

Single source of truth for labour-market sources: what each offers, what is
genuinely accessible, license/attribution obligations, and known coverage
limits. No network or database access here — pure metadata.

Verified 2026-10-24 from provider documentation and limited public endpoint
checks. Provider access does not imply broad geographic or occupation coverage.
"""
from __future__ import annotations

# access: "connected"    -> machine-readable and collected automatically now
#         "pending_key"  -> free but requires an API key we do not hold
#         "unreachable"  -> no documented API and/or not reachable from here
SOURCES = {
    "opendosm": {
        "name": "OpenDOSM — Dept. of Statistics Malaysia",
        "kind": "statistics",
        "country": "Malaysia",
        "access": "connected",
        "url": "https://open.dosm.gov.my/",
        "data": "https://storage.dosm.gov.my/",
        "license": "Government of Malaysia Open Data Terms of Use 1.0 (open data)",
        "attribution": "Source: Department of Statistics Malaysia (DOSM) via OpenDOSM.",
        "note": (
            "Official labour-market statistics: monthly labour force and "
            "unemployment, wages and employee counts by occupation and by "
            "skill level, employment share by sector. DOSM publishes no "
            "individual job advertisements."
        ),
    },
    "remotive": {
        "name": "Remotive",
        "kind": "job_board",
        "country": "Global (remote)",
        "access": "connected",
        "url": "https://remotive.com/",
        "api": "https://remotive.com/api/remote-jobs",
        "license": "Free public API per Remotive terms",
        "attribution": "Job postings via the Remotive API (remotive.com).",
        "note": (
            "Remote-only job advertisements with full descriptions and "
            "publication dates. The free API returns only the 10 newest "
            "listings total (category/limit parameters ignored), so each "
            "run adds ~10; coverage accumulates over repeated runs. "
            "Skewed toward tech roles."
        ),
    },
    "remoteok": {
        "name": "Remote OK",
        "kind": "job_board",
        "country": "Global (remote)",
        "access": "connected",
        "url": "https://remoteok.com/",
        "api": "https://remoteok.com/api",
        "license": "Remote OK API ToS: must link back and credit Remote OK",
        "attribution": "Job postings via the Remote OK API (remoteok.com).",
        "note": (
            "Remote-only job advertisements with descriptions and dates. "
            "The API serves the current listing window only. Their terms "
            "require visible attribution with a follow link — shown on the "
            "dashboard."
        ),
    },
    "himalayas": {
        "name": "Himalayas",
        "kind": "job_board",
        "country": "Global (remote)",
        "access": "connected",
        "url": "https://himalayas.app/",
        "api": "https://himalayas.app/jobs/api",
        "license": "Free public API; visible Himalayas credit and applicationLink required",
        "attribution": "Jobs via Himalayas — apply through the Himalayas listing.",
        "note": (
            "Remote-only public feed, no key required. One 20-job page per "
            "manual collection run to respect the shared anonymous allowance. "
            "The API requires visible source credit, its applicationLink for "
            "Apply, removal of closed jobs, and prohibits syndication to other "
            "job boards or aggregators."
        ),
    },
    "greenhouse": {
        "name": "Greenhouse public boards",
        "kind": "employer_job_board_api",
        "country": "Employer-specific",
        "access": "connected",
        "url": "https://developers.greenhouse.io/job-board",
        "api": "https://boards-api.greenhouse.io/v1/boards/",
        "license": "Public GET Job Board endpoints; each employer board is a separate feed",
        "attribution": "Employer job board via Greenhouse.",
        "boards": [
            {"token": "stripe", "employer": "Stripe"},
        ],
        "note": (
            "Public GET endpoints require no authentication, but there is no "
            "global job search. The configured Stripe board is a limited "
            "employer sample; it is not representative of the wider market."
        ),
    },
    "lever": {
        "name": "Lever public postings",
        "kind": "employer_job_board_api",
        "country": "Employer-specific",
        "access": "connected",
        "url": "https://github.com/Lever/postings-api",
        "api": "https://api.lever.co/v0/postings/",
        "license": "Public published postings; each employer site is a separate feed",
        "attribution": "Employer job board via Lever.",
        "boards": [
            {"token": "veeva", "employer": "Veeva Systems"},
        ],
        "note": (
            "Published postings are public and no key is required, but the API "
            "is per-employer and does not provide cross-company full-text "
            "search. The configured Veeva board is a limited employer sample."
        ),
    },
    "arbeitnow": {
        "name": "Arbeitnow",
        "kind": "job_board",
        "country": "Primarily Germany / Europe",
        "access": "terms_unverified",
        "url": "https://www.arbeitnow.com/",
        "api": "https://www.arbeitnow.com/api/job-board-api",
        "license": "Public endpoint; site terms restrict copying and public display",
        "attribution": "",
        "note": (
            "The public endpoint is reachable without a key and returns job "
            "records, but the published site terms prohibit copying, public "
            "display, and mirroring. Do not ingest or show these records unless "
            "Arbeitnow provides explicit API reuse permission."
        ),
    },
    "myfuturejobs": {
        "name": "MYFutureJobs (PERKESO, Malaysia)",
        "kind": "job_board",
        "country": "Malaysia",
        "access": "unreachable",
        "url": "https://www.myfuturejobs.gov.my/",
        "license": "Terms not verified",
        "attribution": "",
        "note": (
            "Malaysia's national employment portal. No documented public "
            "API, and the site did not respond from this environment. "
            "Malaysian job advertisements need verified permission/an "
            "endpoint here, or a key-based aggregator."
        ),
    },
    "adzuna": {
        "name": "Adzuna",
        "kind": "aggregator",
        "country": "Multi-country (no Malaysia)",
        "access": "pending_key",
        "url": "https://developer.adzuna.com/",
        "license": "Free developer key",
        "attribution": "",
        "note": (
            "Free API key, but the supported country list does not include "
            "Malaysia (nearest: Singapore). Wire up once a key is provided."
        ),
    },
    "jooble": {
        "name": "Jooble",
        "kind": "aggregator",
        "country": "Multi-country (incl. Malaysia)",
        "access": "pending_key",
        "url": "https://jooble.org/api/about",
        "license": "Free API key on request",
        "attribution": "",
        "note": (
            "Covers Malaysia. Requires a free API key obtained through "
            "their request form; wire up when a key is provided."
        ),
    },
}

# Greenhouse and Lever expose employer-specific boards, not a global vacancy
# index. Keep the exact board slug and display name visible in this registry.

# OpenDOSM datasets collected as hiring-statistics evidence, with the
# dimension columns that define each series (everything else numeric is a
# metric). Rows with sex=male/female are dropped; we keep 'both'.
OPENDOSM_DATASETS = {
    "lfs_month": [],           # labour force + unemployment rate, monthly
    "wages_occupation": ["occupation"],  # wages + employee counts by occupation
    "wages_skill": ["skill"],            # wages + employee counts by skill level
    "employment_sector": ["sector"],     # employment share by sector, annual
}
