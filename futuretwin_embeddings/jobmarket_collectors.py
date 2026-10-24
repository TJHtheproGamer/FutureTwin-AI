"""FutureTwin Phase 2: job-market source connectors.

Connectors for the sources verified accessible (see jobmarket_registry.py):
OpenDOSM labour statistics (Malaysia), Remotive and Remote OK job
advertisements. Unreachable/pending-key sources are reported, never silently
skipped.

Politeness: reuses benchmark_collectors._get_meta — one request per file,
identifying User-Agent, same-day cache under data/cache/, stale-cache
fallback on 429. collected_at is always the TRUE retrieval time (cache file
mtime when served from cache), never "now" for stale bytes.
"""
from __future__ import annotations

import csv
import io
import json
from datetime import datetime, timezone
from html.parser import HTMLParser

from benchmark_collectors import _get_meta
from jobmarket_registry import OPENDOSM_DATASETS, SOURCES
from jobmarket_store import content_hash


class _TextOnly(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        self.parts.append(data)


def _html_to_text(html: str) -> str:
    from futuretwin_job_text import plain_job_text
    return plain_job_text(html)


def _source_datetime(value):
    """Parse provider timestamps without treating an update date as a post date."""
    if value in (None, ""):
        return None
    try:
        if isinstance(value, (int, float)):
            stamp = float(value)
            if stamp > 10_000_000_000:
                stamp /= 1000
            return datetime.fromtimestamp(stamp, tz=timezone.utc)
        text = str(value).strip().replace("Z", "+00:00")
        parsed = datetime.fromisoformat(text)
        return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
    except (TypeError, ValueError, OverflowError, OSError):
        return None


def _workplace_from_location(location: str):
    text = (location or "").casefold()
    if "hybrid" in text:
        return "hybrid", False
    if "remote" in text or "worldwide" in text:
        return "remote", True
    if any(word in text for word in ("on-site", "onsite", "office")):
        return "on-site", False
    return "unspecified", None


def _float_or_none(value):
    try:
        return float(value) if value not in (None, "") else None
    except (TypeError, ValueError):
        return None


def _as_text(value):
    if isinstance(value, list):
        return ", ".join(str(item).strip() for item in value if str(item).strip())
    if isinstance(value, dict):
        return ""
    return str(value or "").strip()


# =====================================
# OPENDOSM (Malaysia labour statistics)
# =====================================

def collect_opendosm() -> tuple[list[dict], dict]:
    base = SOURCES["opendosm"]["data"]
    records: list[dict] = []
    datasets_done = 0

    for dataset, dim_columns in OPENDOSM_DATASETS.items():
        raw, fetched_at, _cached = _get_meta(
            f"{base}labour/{dataset}.csv", f"opendosm_{dataset}.csv")
        reader = csv.DictReader(io.StringIO(raw.decode("utf-8")))
        for row in reader:
            if row.get("sex") not in (None, "", "both"):
                continue  # keep the aggregate series only
            date = (row.get("date") or "").strip()
            if not date:
                continue
            dims = {c: row[c] for c in dim_columns if row.get(c)}
            metrics = {}
            for key, value in row.items():
                if key in ("date", "sex", *dim_columns):
                    continue
                try:
                    metrics[key] = float(value)
                except (TypeError, ValueError):
                    continue
            if not metrics:
                continue
            records.append({
                "source": "opendosm",
                "dataset": dataset,
                "date": date,
                "dims": dims,
                "metrics": metrics,
                "collected_at": fetched_at,
            })
        datasets_done += 1

    status = {"source": "opendosm", "status": "connected",
              "detail": f"{datasets_done} labour datasets, {len(records)} series rows"}
    return records, status


# =====================================
# REMOTIVE (global remote job ads)
# =====================================
# The free API returns only the 10 newest listings total — the category and
# limit parameters are ignored (verified 2026-10-21). One polite request.

def collect_remotive() -> tuple[list[dict], dict]:
    raw, fetched_at, _cached = _get_meta(
        SOURCES["remotive"]["api"], "remotive_jobs.json")
    payload = json.loads(raw)
    records: list[dict] = []

    for job in payload.get("jobs", []):
        job_id = str(job.get("id") or "")
        title = (job.get("title") or "").strip()
        if not job_id or not title:
            continue
        employer = (job.get("company_name") or "").strip()
        description = _html_to_text(job.get("description") or "")
        records.append({
            "source": "remotive",
            "source_posting_id": job_id,
            "title": title,
            "employer": employer,
            "country": "",
            "location": (job.get("candidate_required_location") or "").strip(),
            "remote": True,
            "category": (job.get("category") or "").strip(),
            "posted_date": (job.get("publication_date") or "")[:10] or None,
            "url": job.get("url") or "",
            "description_text": description,
            "content_hash": content_hash(title, employer, description),
            "duplicate_of": None,
            "collected_at": fetched_at,
        })

    status = {"source": "remotive", "status": "connected",
              "detail": f"{len(records)} remote job advertisements "
                        f"(free API returns only the 10 newest listings)"}
    return records, status


# =====================================
# REMOTE OK (global remote job ads; attribution required by their ToS)
# =====================================

def collect_remoteok() -> tuple[list[dict], dict]:
    raw, fetched_at, _cached = _get_meta(
        SOURCES["remoteok"]["api"], "remoteok_jobs.json")
    payload = json.loads(raw)
    records: list[dict] = []

    # Element 0 is Remote OK's legal/metadata object, not a job.
    for job in payload[1:]:
        job_id = str(job.get("id") or "")
        title = (job.get("position") or "").strip()
        if not job_id or not title:
            continue
        employer = (job.get("company") or "").strip()
        description = _html_to_text(job.get("description") or "")
        posted = (job.get("date") or "")[:10]
        if not posted and job.get("epoch"):
            posted = datetime.fromtimestamp(
                int(job["epoch"]), tz=timezone.utc).strftime("%Y-%m-%d")
        records.append({
            "source": "remoteok",
            "source_posting_id": job_id,
            "title": title,
            "employer": employer,
            "country": "",
            "location": (job.get("location") or "").strip(),
            "remote": True,
            "category": "",
            "posted_date": posted or None,
            "url": job.get("url") or job.get("apply_url") or "",
            "description_text": description,
            "content_hash": content_hash(title, employer, description),
            "duplicate_of": None,
            "collected_at": fetched_at,
        })

    status = {"source": "remoteok", "status": "connected",
              "detail": f"{len(records)} current remote job advertisements"}
    return records, status


# =====================================
# HIMALAYAS (free public remote-job feed)
# =====================================
# Anonymous callers share a public allowance. Collect one 20-job page per run;
# the API terms require visible credit and use of applicationLink for Apply.

def collect_himalayas() -> tuple[list[dict], dict]:
    from jobmarket_registry import SOURCES

    raw, fetched_at, _cached = _get_meta(
        f"{SOURCES['himalayas']['api']}?limit=20", "himalayas_jobs.json")
    payload = json.loads(raw)
    records: list[dict] = []
    for job in payload.get("jobs", []):
        job_id = str(job.get("guid") or "").strip()
        title = (job.get("title") or "").strip()
        if not job_id or not title:
            continue
        restrictions = job.get("locationRestrictions") or []
        if not isinstance(restrictions, list):
            restrictions = []
        locations = [str(value).strip() for value in restrictions if str(value).strip()]
        updated = _source_datetime(job.get("pubDate"))
        categories = job.get("categories") or []
        records.append({
            "source": "himalayas",
            "source_posting_id": job_id,
            "title": title,
            "employer": _as_text(job.get("companyName")),
            "country": ", ".join(locations),
            "location": ", ".join(locations) or "Worldwide",
            "remote": True,
            "workplace_type": "remote",
            "category": _as_text(categories),
            "posted_date": None,
            "source_updated_at": updated,
            "expires_at": _source_datetime(job.get("expiryDate")),
            "url": job.get("applicationLink") or "",
            "description_text": _html_to_text(
                job.get("description") or job.get("excerpt") or ""),
            "seniority": _as_text(job.get("seniority")),
            "employment_type": _as_text(job.get("employmentType")),
            "salary_min": _float_or_none(job.get("minSalary")),
            "salary_max": _float_or_none(job.get("maxSalary")),
            "salary_currency": _as_text(job.get("currency")),
            "salary_period": _as_text(job.get("salaryPeriod")),
            "salary_text": "",
            "content_hash": content_hash(
                title, (job.get("companyName") or "").strip(),
                _html_to_text(job.get("description") or job.get("excerpt") or "")),
            "duplicate_of": None,
            "collected_at": fetched_at,
        })
    return records, {
        "source": "himalayas", "status": "connected",
        "detail": f"{len(records)} remote jobs from one anonymous 20-job page; "
                  "Apply links use Himalayas applicationLink",
    }


# =====================================
# GREENHOUSE AND LEVER (public employer-specific boards)
# =====================================

def collect_greenhouse() -> tuple[list[dict], dict]:
    from jobmarket_registry import SOURCES

    records: list[dict] = []
    for board in SOURCES["greenhouse"].get("boards", []):
        token = board["token"]
        url = f"https://boards-api.greenhouse.io/v1/boards/{token}/jobs?content=true"
        raw, fetched_at, _cached = _get_meta(
            url, f"greenhouse_{token}_jobs.json")
        payload = json.loads(raw)
        jobs = payload.get("jobs", [])
        # Keep a bounded, recent sample; this endpoint returns the board in one
        # response and has no documented cross-company search or pagination.
        jobs = sorted(
            jobs, key=lambda item: str(item.get("updated_at") or ""), reverse=True
        )[:150]
        for job in jobs:
            job_id = str(job.get("id") or "").strip()
            title = (job.get("title") or "").strip()
            if not job_id or not title:
                continue
            location = (job.get("location") or {}).get("name", "")
            workplace_type, remote = _workplace_from_location(location)
            description = _html_to_text(job.get("content") or "")
            updated = _source_datetime(job.get("updated_at"))
            records.append({
                "source": "greenhouse",
                "source_posting_id": f"{token}:{job_id}",
                "title": title,
                "employer": board["employer"],
                "country": "",
                "location": location,
                "remote": remote,
                "workplace_type": workplace_type,
                "category": ", ".join(
                    str(row.get("name") or "").strip()
                    for row in job.get("departments", []) if row.get("name")),
                "posted_date": None,
                "source_updated_at": updated,
                "url": job.get("absolute_url") or "",
                "description_text": description,
                "seniority": "",
                "employment_type": "",
                "salary_min": None,
                "salary_max": None,
                "salary_currency": "",
                "salary_period": "",
                "salary_text": "",
                "content_hash": content_hash(
                    title, board["employer"], description, location),
                "duplicate_of": None,
                "collected_at": fetched_at,
            })
    return records, {
        "source": "greenhouse", "status": "connected",
        "detail": f"{len(records)} jobs from configured public employer board(s); "
                  "updated_at is stored separately from posting date",
    }


def collect_lever() -> tuple[list[dict], dict]:
    from jobmarket_registry import SOURCES

    records: list[dict] = []
    for board in SOURCES["lever"].get("boards", []):
        token = board["token"]
        url = f"https://api.lever.co/v0/postings/{token}?mode=json&limit=150"
        raw, fetched_at, _cached = _get_meta(
            url, f"lever_{token}_jobs.json")
        payload = json.loads(raw)
        if not isinstance(payload, list):
            raise ValueError(f"Lever board {token} returned an unexpected response.")
        for job in payload[:150]:
            job_id = str(job.get("id") or "").strip()
            title = (job.get("text") or "").strip()
            if not job_id or not title:
                continue
            categories = job.get("categories") or {}
            location = (categories.get("allLocations") or
                        categories.get("location") or "")
            if isinstance(location, list):
                location = ", ".join(str(v) for v in location if v)
            workplace_type, remote = _workplace_from_location(
                job.get("workplaceType") or location)
            explicit_workplace = str(job.get("workplaceType") or "").casefold()
            if explicit_workplace in {"remote", "on-site", "hybrid"}:
                workplace_type = explicit_workplace
                remote = explicit_workplace == "remote"
            salary = job.get("salaryRange") or {}
            description = (
                job.get("descriptionPlain") or job.get("description") or
                job.get("descriptionBodyPlain") or job.get("descriptionBody") or "")
            description += "\n" + "\n".join(
                str(section.get("text") or "") + "\n" +
                str(section.get("content") or "")
                for section in job.get("lists", []) if isinstance(section, dict)
            )
            description = _html_to_text(description)
            created = _source_datetime(job.get("createdAt"))
            records.append({
                "source": "lever",
                "source_posting_id": f"{token}:{job_id}",
                "title": title,
                "employer": board["employer"],
                "country": (job.get("country") or "").strip(),
                "location": str(location).strip(),
                "remote": remote,
                "workplace_type": workplace_type,
                "category": (categories.get("team") or
                             categories.get("department") or "").strip(),
                "posted_date": created.date() if created else None,
                "source_updated_at": None,
                "url": job.get("applyUrl") or job.get("hostedUrl") or "",
                "description_text": description,
                "seniority": (categories.get("level") or "").strip(),
                "employment_type": (categories.get("commitment") or "").strip(),
                "salary_min": _float_or_none(salary.get("min")),
                "salary_max": _float_or_none(salary.get("max")),
                "salary_currency": (salary.get("currency") or "").strip(),
                "salary_period": (salary.get("interval") or "").strip(),
                "salary_text": (job.get("salaryDescriptionPlain") or "").strip(),
                "content_hash": content_hash(
                    title, board["employer"], description, location),
                "duplicate_of": None,
                "collected_at": fetched_at,
            })
    return records, {
        "source": "lever", "status": "connected",
        "detail": f"{len(records)} jobs from configured public employer board(s); "
                  "Lever provides no global full-text job search",
    }


# =====================================
# SOURCES NOT COLLECTED (reported honestly)
# =====================================

def unavailable_sources() -> list[dict]:
    return [
        {"source": key, "status": meta["access"], "detail": meta["note"]}
        for key, meta in SOURCES.items()
        if meta["access"] != "connected"
    ]


COLLECTORS = {
    "opendosm": collect_opendosm,
    "remotive": collect_remotive,
    "remoteok": collect_remoteok,
    "himalayas": collect_himalayas,
    "greenhouse": collect_greenhouse,
    "lever": collect_lever,
}
