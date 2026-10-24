"""FutureTwin Phase 2: job-market trend computation.

Observed trends only. Two measurements are kept strictly separate (req 6):
  - absolute counts: number of advertisements mentioning a skill
  - share: percentage of that window's advertisements mentioning the skill
A rising share with falling absolute counts (or vice versa) means different
things; both are reported.

AI linkage (req 7/9): frontier benchmark events are juxtaposed with skill
demand changes by date only. Co-occurrence is NEVER presented as causation.
"""
from __future__ import annotations

from datetime import date, timedelta
from typing import Any

from jobmarket_store import (
    get_collection_log,
    get_posting_coverage,
    get_posting_dates,
    get_skill_mentions,
    get_stats_series,
)

WINDOW_DAYS = 28          # recent vs prior comparison window
MIN_MENTIONS = 5          # a skill needs this many recent mentions to trend
# Similarity floor for counting a MiniLM skill extraction as a mention.
# Unvalidated heuristic, same honesty level as the impact engine labels.
SKILL_SIMILARITY_FLOOR = 0.35


def _window_bounds(dates: list[date]) -> dict[str, Any]:
    """Anchor windows on the newest posting date, not wall-clock today."""
    if not dates:
        return {}
    end = max(dates)
    mid = end - timedelta(days=WINDOW_DAYS - 1)
    start = mid - timedelta(days=WINDOW_DAYS)
    return {"recent_start": mid.isoformat(), "recent_end": end.isoformat(),
            "prior_start": start.isoformat(), "prior_end": (mid - timedelta(days=1)).isoformat()}


def compute_skill_trends() -> dict[str, Any]:
    mentions = get_skill_mentions()
    posting_dates = [r["posted_date"] for r in get_posting_dates()]
    bounds = _window_bounds(posting_dates)
    if not bounds:
        return {"windows": {}, "rising": [], "declining": [],
                "monthly": [], "note": "No dated postings yet."}

    recent_start = date.fromisoformat(bounds["recent_start"])
    prior_start = date.fromisoformat(bounds["prior_start"])
    recent_end = date.fromisoformat(bounds["recent_end"])

    def window_of(d: date) -> str | None:
        if d >= recent_start:
            return "recent"
        if d >= prior_start:
            return "prior"
        return None

    postings_in = {"recent": 0, "prior": 0}
    for d in posting_dates:
        w = window_of(d)
        if w:
            postings_in[w] += 1

    per_skill: dict[str, dict[str, int]] = {}
    monthly: dict[str, dict[str, int]] = {}
    for row in mentions:
        if row["cosine_similarity"] < SKILL_SIMILARITY_FLOOR:
            continue
        skill = row["skill"]
        d = row["posted_date"]
        w = window_of(d)
        entry = per_skill.setdefault(skill, {"recent": 0, "prior": 0})
        if w:
            entry[w] += 1
        month = d.strftime("%Y-%m")
        monthly.setdefault(month, {})
        monthly[month][skill] = monthly[month].get(skill, 0) + 1

    trends = []
    for skill, counts in per_skill.items():
        if counts["recent"] < MIN_MENTIONS:
            continue
        share_recent = (counts["recent"] / postings_in["recent"]
                        if postings_in["recent"] else 0)
        share_prior = (counts["prior"] / postings_in["prior"]
                       if postings_in["prior"] else None)
        trends.append({
            "skill": skill,
            "recent_ads": counts["recent"],
            "prior_ads": counts["prior"],
            "share_recent_pct": round(share_recent * 100, 2),
            "share_prior_pct": round(share_prior * 100, 2) if share_prior is not None else None,
            "share_delta_pp": None,  # Collection completeness/consistent sampling is not documented.
            "abs_delta": counts["recent"] - counts["prior"],
        })
    trends.sort(key=lambda t: (-t["recent_ads"], t["skill"].casefold()))

    monthly_rows = [
        {"month": m, "skills": dict(sorted(
            s.items(), key=lambda kv: kv[1], reverse=True)[:15])}
        for m, s in sorted(monthly.items())
    ]
    postings_by_month: dict[str, int] = {}
    for d in posting_dates:
        key = d.strftime("%Y-%m")
        postings_by_month[key] = postings_by_month.get(key, 0) + 1
    return {
        "postings_by_month": [
            {"month": m, "count": n}
            for m, n in sorted(postings_by_month.items())
        ],
        "windows": {**bounds, **{f"postings_{k}": v
                                 for k, v in postings_in.items()}},
        "rising": [],
        "declining": [],
        "observed_sample_skills": trends,
        "comparison_status": "not_enough_comparable_data",
        "note": (
            "Counts describe the collected ad sample. Source completeness and comparable "
            "sampling across periods are not documented, so rising/declining demand and "
            "hiring-growth percentages are unavailable."
        ),
        "monthly": monthly_rows,
        "min_mentions": MIN_MENTIONS,
        "similarity_floor": SKILL_SIMILARITY_FLOOR,
    }


def compute_malaysia_indicators() -> dict[str, Any]:
    """OpenDOSM observed statistics: labour force, wages by occupation/skill,
    employment by sector. No inference — just latest vs a year earlier."""
    out: dict[str, Any] = {}

    lfs = get_stats_series("lfs_month")
    if lfs:
        latest, prior = lfs[-1], (lfs[-13] if len(lfs) >= 13 else lfs[0])
        out["labour_force"] = {
            "latest_date": str(latest["date"]),
            "unemployment_rate": latest["metrics"].get("u_rate"),
            "participation_rate": latest["metrics"].get("p_rate"),
            "employed_thousands": latest["metrics"].get("lf_employed"),
            "year_ago_date": str(prior["date"]),
            "unemployment_rate_year_ago": prior["metrics"].get("u_rate"),
        }

    wages_occ = get_stats_series("wages_occupation")
    if wages_occ:
        by_occ: dict[str, list[dict]] = {}
        for row in wages_occ:
            occ = row["dims"].get("occupation")
            if occ and occ != "overall":
                by_occ.setdefault(occ, []).append(row)
        movers = []
        for occ, series in by_occ.items():
            series.sort(key=lambda r: r["date"])
            latest = series[-1]
            prior = series[-13] if len(series) >= 13 else series[0]
            now_n = latest["metrics"].get("recipients")
            then_n = prior["metrics"].get("recipients")
            if now_n is None or then_n in (None, 0):
                continue
            movers.append({
                "occupation": occ,
                "employees_latest": now_n,
                "employees_year_ago": then_n,
                "change_pct": round((now_n - then_n) / then_n * 100, 1),
                "median_wage": latest["metrics"].get("wages_median"),
                "latest_date": str(latest["date"]),
            })
        movers.sort(key=lambda m: m["change_pct"], reverse=True)
        out["occupation_movers"] = movers

    wages_skill = get_stats_series("wages_skill")
    if wages_skill:
        by_skill: dict[str, dict] = {}
        for row in wages_skill:
            skill = row["dims"].get("skill")
            if skill and skill != "overall":
                by_skill[skill] = row  # ascending dates -> last wins
        out["wages_by_skill"] = sorted(
            ({"skill": s,
              "median_wage": r["metrics"].get("wages_median"),
              "employees": r["metrics"].get("recipients"),
              "date": str(r["date"])}
             for s, r in by_skill.items()),
            key=lambda x: x["median_wage"] or 0, reverse=True)

    sector = get_stats_series("employment_sector")
    if sector:
        by_sector: dict[str, list[dict]] = {}
        for row in sector:
            s = row["dims"].get("sector")
            if s:
                by_sector.setdefault(s, []).append(row)
        shifts = []
        for s, series in by_sector.items():
            series.sort(key=lambda r: r["date"])
            first, latest = series[0], series[-1]
            p0, p1 = (first["metrics"].get("proportion"),
                      latest["metrics"].get("proportion"))
            if p0 is None or p1 is None:
                continue
            shifts.append({"sector": s, "share_first_pct": p0,
                           "share_latest_pct": p1,
                           "delta_pp": round(p1 - p0, 1),
                           "first_date": str(first["date"]),
                           "latest_date": str(latest["date"])})
        shifts.sort(key=lambda x: x["delta_pp"], reverse=True)
        out["sector_shifts"] = shifts

    return out


def get_ai_cooccurrence(limit: int = 15) -> dict[str, Any]:
    """Frontier benchmark events that happened inside the job-ad observation
    window. Juxtaposition only — NOT evidence that AI caused hiring changes.
    """
    dates = [r["posted_date"] for r in get_posting_dates()]
    window = {}
    if dates:
        window = {"earliest_posting": str(min(dates)),
                  "latest_posting": str(max(dates))}
    events: list[dict] = []
    if dates:
        from benchmark_store import _rows as benchmark_rows
        events = benchmark_rows("""
            SELECT source, benchmark_name, model_name, previous_best,
                   new_best, improvement, evaluation_date
            FROM frontier_advancements
            WHERE evaluation_date >= %s AND evaluation_date <= %s
            ORDER BY evaluation_date DESC LIMIT %s
        """, (min(dates), max(dates), limit))
        for e in events:
            if e.get("evaluation_date") is not None:
                e["evaluation_date"] = str(e["evaluation_date"])
    return {
        "window": window,
        "frontier_events": events,
        "label": "OBSERVED benchmark events in the ad-collection window. "
                 "Temporal co-occurrence with hiring trends is NOT evidence "
                 "of causation.",
    }


def get_overview() -> dict[str, Any]:
    from jobmarket_registry import SOURCES
    from jobmarket_store import get_source_health, get_source_successes
    coverage = {r["source"]: r for r in get_posting_coverage()}
    health = {r["source"]: r for r in get_source_health()}
    success = {r["source"]: r["finished_at"] for r in get_source_successes()}
    sources = []
    for key, meta in SOURCES.items():
        c = coverage.get(key, {})
        sources.append({
            "source": key, "name": meta["name"], "kind": meta["kind"],
            "country": meta["country"], "access": meta["access"],
            "url": meta["url"], "license": meta["license"],
            "attribution": meta["attribution"], "note": meta["note"],
            "postings": c.get("postings", 0),
            "canonical": c.get("canonical", 0),
            "duplicates": c.get("duplicates", 0),
            "with_skills": c.get("with_skills", 0),
            "earliest_posting": str(c.get("earliest_posting") or ""),
            "latest_posting": str(c.get("latest_posting") or ""),
            "last_collected": str(c.get("last_collected") or ""),
            "last_status": health.get(key, {}).get("status", ""),
            "last_run_at": str(health.get(key, {}).get("finished_at") or ""),
            "last_error": (health.get(key, {}).get("detail", "")
                           if str(health.get(key, {}).get("status", "")
                                  ).startswith("error") else ""),
            "last_success": str(success.get(key) or ""),
        })
    rows = list(coverage.values())
    earliest = [r["earliest_posting"] for r in rows if r.get("earliest_posting")]
    latest = [r["latest_posting"] for r in rows if r.get("latest_posting")]
    totals = {
        "canonical": sum(int(r.get("canonical") or 0) for r in rows),
        "duplicates": sum(int(r.get("duplicates") or 0) for r in rows),
        "with_skills": sum(int(r.get("with_skills") or 0) for r in rows),
        "earliest": str(min(earliest)) if earliest else "",
        "latest": str(max(latest)) if latest else "",
        # Honest coverage labels: Malaysia contributes official statistics
        # only; job advertisements are global-remote boards.
        "countries": ["Malaysia (official statistics)",
                      "Global remote (job ads)"],
    }
    return {"sources": sources, "collection_log": get_collection_log(8),
            "totals": totals}
