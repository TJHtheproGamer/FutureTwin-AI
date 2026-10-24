"""FutureTwin: source connectors for the multi-source benchmark system.

Each connector fetches machine-readable results from one source and returns
normalized records ready for benchmark_store.upsert_results(). Sources without
a machine-readable feed (METR, OSWorld) are reported as local_only, never
silently skipped.

Politeness: one request per file, explicit User-Agent, raw responses cached
under data/cache/ so re-runs and debugging don't hammer sources.
"""
from __future__ import annotations

import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

from benchmark_registry import (
    AA_INDEXES,
    LIVEBENCH_DOMAINS,
    LIVEBENCH_TASKS,
    SOURCES,
    SWEBENCH_LEADERBOARDS,
)

folder = Path(__file__).resolve().parent
CACHE_DIR = folder / "data" / "cache"

USER_AGENT = "FutureTwinAI/1.0 (research; https://replit.com) benchmark-collection"

# LiveBench release tables verified to exist (see livebench.github.io repo).
LIVEBENCH_RELEASES = [
    "2024_06_24", "2024_07_26", "2024_08_31", "2024_11_25",
    "2025_04_02", "2025_04_25", "2025_05_30", "2025_11_25",
    "2025_12_23", "2026_01_08", "2026_06_25",
]


def _file_time_iso(path: Path) -> str:
    return datetime.fromtimestamp(
        path.stat().st_mtime, tz=timezone.utc).isoformat()


def _get_meta(url: str, cache_name: str, headers: dict | None = None,
              params: dict | None = None,
              timeout: int = 60) -> tuple[bytes, str, bool]:
    """Fetch with cache + rate-limit awareness.

    Returns (content, fetched_at, from_cache) where fetched_at is the TRUE
    retrieval time — the cache file's mtime for cached copies, now for live
    fetches — so stored records never present cached data as freshly
    observed. AA's free tier is a DAILY quota (100 req/day, verified via
    x-ratelimit-* headers 2026-10-22), so a long retry-after skips pointless
    sleeps and degrades straight to the newest stale cache copy.
    """
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d")
    cache_path = CACHE_DIR / f"{stamp}_{cache_name}"
    if cache_path.exists():
        return cache_path.read_bytes(), _file_time_iso(cache_path), True
    merged = {"User-Agent": USER_AGENT, **(headers or {})}
    delay = 3.0
    for attempt in range(4):
        response = requests.get(url, headers=merged, params=params,
                                timeout=timeout)
        if response.status_code != 429:
            response.raise_for_status()
            cache_path.write_bytes(response.content)
            time.sleep(0.4)  # gentle on free/public endpoints
            return (response.content,
                    datetime.now(timezone.utc).isoformat(), False)
        try:
            retry_after = int(response.headers.get("retry-after") or 0)
        except ValueError:
            retry_after = 0
        if retry_after > 120 or attempt == 3:
            stale = sorted(CACHE_DIR.glob(f"*_{cache_name}"))
            if stale:
                print(f"429 on {url} (retry-after {retry_after}s); reusing "
                      f"cached copy {stale[-1].name}", flush=True)
                return stale[-1].read_bytes(), _file_time_iso(stale[-1]), True
            response.raise_for_status()
        time.sleep(min(delay, retry_after) if retry_after else delay)
        delay *= 2
    raise RuntimeError("unreachable")


def _get(url: str, cache_name: str, headers: dict | None = None,
         params: dict | None = None, timeout: int = 60) -> bytes:
    """Content-only wrapper around _get_meta (legacy callers)."""
    return _get_meta(url, cache_name, headers=headers, params=params,
                     timeout=timeout)[0]


def _parse_date(value: Any) -> str | None:
    """Normalize date-ish values (ISO str, yyyymmdd int) to ISO date strings."""
    if value in (None, "", 0):
        return None
    s = str(value).strip()
    if s.isdigit() and len(s) == 8:  # SWE-bench model_release_date: 20251217
        return f"{s[:4]}-{s[4:6]}-{s[6:]}"
    return s[:10]


# =====================================
# ARTIFICIAL ANALYSIS (existing integration, normalized)
# =====================================

def collect_artificial_analysis() -> tuple[list[dict], dict]:
    """Composite indexes only: the free tier exposes no individual benchmarks."""
    api_key = os.getenv("AA_API_KEY")
    if not api_key:
        return [], {"source": "artificial_analysis", "status": "error",
                    "detail": "AA_API_KEY not set"}

    records: list[dict] = []
    page = 1
    index_version = None
    models_seen = 0
    while page <= 60:  # hard cap: never loop forever on a misbehaving API
        raw, fetched_at, from_cache = _get_meta(
            SOURCES["artificial_analysis"]["api"],
            f"aa_models_p{page}.json",
            headers={"x-api-key": api_key},
            params={"page": page},  # AA silently returns page 1 without this
        )
        payload = json.loads(raw)
        index_version = payload.get("intelligence_index_version")
        models = payload.get("data", [])
        if not models:
            break  # empty page: end of results, stop honestly
        models_seen += len(models)
        for model in models:
            evaluations = model.get("evaluations") or {}
            for field, (bench, domain, _task_text) in AA_INDEXES.items():
                score = evaluations.get(field)
                if score is None:
                    continue
                records.append({
                    "source": "artificial_analysis",
                    "benchmark_name": bench,
                    "benchmark_version": str(index_version or ""),
                    "domain": domain,
                    "task": "",
                    "model_id": str(model.get("id") or ""),
                    "model_name": str(model.get("name") or model.get("slug") or ""),
                    "score": float(score),
                    "score_direction": "higher_better",
                    "score_unit": "index points",
                    "evaluation_date": None,  # AA does not publish per-score dates on free tier
                    "model_release_date": _parse_date(model.get("release_date")),
                    "source_url": SOURCES["artificial_analysis"]["url"],
                    "collected_at": fetched_at,  # true retrieval time
                    "raw_metadata": {"composite_index": True,
                                     "tier": payload.get("tier"),
                                     "served_from_cache": from_cache},
                })
        if not payload.get("pagination", {}).get("has_more", False):
            break
        page += 1

    status = {"source": "artificial_analysis", "status": "connected",
              "detail": f"{models_seen} models, {len(records)} composite-index "
                        f"scores (individual benchmarks not on free tier)"}
    return records, status


# =====================================
# SWE-BENCH (official leaderboard JSON)
# =====================================

def collect_swebench() -> tuple[list[dict], dict]:
    raw, fetched_at, from_cache = _get_meta(
        SOURCES["swebench"]["data"], "swebench_leaderboards.json")
    payload = json.loads(raw)
    records: list[dict] = []

    for leaderboard in payload.get("leaderboards", []):
        board = leaderboard.get("name")
        if board not in SWEBENCH_LEADERBOARDS:
            continue
        for entry in leaderboard.get("results", []):
            score = entry.get("resolved")
            name = entry.get("name")
            if score is None or not name:
                continue
            records.append({
                "source": "swebench",
                "benchmark_name": f"SWE-bench {board}",
                "benchmark_version": board,
                "domain": "Coding",
                "task": "",
                "model_id": str(entry.get("folder") or ""),
                "model_name": str(name),
                "score": float(score),
                "score_direction": "higher_better",
                "score_unit": "percent resolved",
                "evaluation_date": _parse_date(entry.get("date")),
                "model_release_date": _parse_date(entry.get("model_release_date")),
                "source_url": SOURCES["swebench"]["url"],
                "collected_at": fetched_at,
                "raw_metadata": {
                    "served_from_cache": from_cache,
                    "agent": entry.get("agent"),
                    "agent_org": entry.get("agent_org"),
                    "model_display": entry.get("model_display"),
                    "model_org": entry.get("model_org"),
                    "checked": entry.get("checked"),
                    "warning": entry.get("warning"),
                    "open_source_system": entry.get("os_system"),
                },
            })

    status = {"source": "swebench", "status": "connected",
              "detail": f"{len(records)} leaderboard results across "
                        f"{len(SWEBENCH_LEADERBOARDS)} boards"}
    return records, status


# =====================================
# LIVEBENCH (per-release score tables)
# =====================================

def collect_livebench() -> tuple[list[dict], dict]:
    records: list[dict] = []
    releases_done = 0
    base = SOURCES["livebench"]["data"]

    for release in LIVEBENCH_RELEASES:
        try:
            table_raw, fetched_at, from_cache = _get_meta(
                f"{base}table_{release}.csv", f"livebench_table_{release}.csv")
            cats_raw, _cats_at, _cats_cache = _get_meta(
                f"{base}categories_{release}.json",
                f"livebench_categories_{release}.json")
        except requests.HTTPError:
            continue  # release not published anymore; skip honestly
        categories: dict[str, list[str]] = json.loads(cats_raw)
        sub_to_suite = {
            sub: suite for suite, subs in categories.items() for sub in subs
        }

        lines = table_raw.decode("utf-8").strip().splitlines()
        if len(lines) < 2:
            continue
        header = lines[0].split(",")
        for line in lines[1:]:
            cells = line.split(",")
            if len(cells) != len(header):
                continue
            model_slug = cells[0].strip()
            for col, value in zip(header[1:], cells[1:]):
                value = value.strip()
                if not value:
                    continue  # 'n/a'/blank: model not evaluated on this subcategory
                sub = col.strip()
                suite = sub_to_suite.get(sub, "")
                records.append({
                    "source": "livebench",
                    "benchmark_name": "LiveBench",
                    "benchmark_version": release.replace("_", "-"),
                    "domain": LIVEBENCH_DOMAINS.get(suite, suite),
                    "task": sub,
                    "model_id": model_slug,
                    "model_name": model_slug,
                    "score": float(value),
                    "score_direction": "higher_better",
                    "score_unit": "percent",
                    "evaluation_date": None,  # per-model eval dates not published
                    "model_release_date": None,
                    "source_url": SOURCES["livebench"]["url"],
                    "collected_at": fetched_at,
                    "raw_metadata": {"suite": suite,
                                     "served_from_cache": from_cache},
                })
        releases_done += 1

    status = {"source": "livebench", "status": "connected",
              "detail": f"{releases_done} release tables, "
                        f"{len(records)} subcategory scores"}
    return records, status


# =====================================
# SOURCES WITHOUT A MACHINE-READABLE FEED
# =====================================

def unavailable_sources() -> list[dict]:
    return [
        {"source": key, "status": meta["access"],
         "detail": meta["note"]}
        for key, meta in SOURCES.items()
        if meta["access"] != "connected"
    ]


COLLECTORS = {
    "artificial_analysis": collect_artificial_analysis,
    "swebench": collect_swebench,
    "livebench": collect_livebench,
}
