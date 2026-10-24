"""Current measured benchmark capability -> candidate ESCO skill overlaps.

IMPORTANT:
  * A current capability baseline does not require a newly detected advancement.
  * Benchmarks are evidence of performance on specific evaluations, NOT observed
    workforce outcomes. ESCO semantic links remain hypotheses pending review.
  * Read-only SQL; no paid inference APIs or data collection.
  * Designed for the existing FutureTwin project (2026-10-22 project archive).
"""
from __future__ import annotations

from collections import defaultdict
from functools import lru_cache
from time import time
from typing import Any

MIN_SIMILARITY = 0.35  # candidate retrieval floor, NOT impact/probability threshold
MAX_TASKS = 80  # keep first-query CPU work bounded
PER_TASK_TOP_K = 50
MAX_LINKS = 6
MAX_TASK_GROUPS = 6
REFRESH_SECONDS = 3600

# Use a SQL window to select the strongest measured model WITHIN EACH benchmark
# version and task. The version is never mixed into its score comparison.
# The application subsequently selects the latest *observed* version series.
SQL = """
WITH best_per_version AS (
    SELECT b.source, b.benchmark_name, b.benchmark_version,
           b.task, b.domain, b.model_name, b.score, b.score_direction,
           b.score_unit, b.evaluation_date, b.model_release_date,
           b.collected_at, b.source_url, b.raw_metadata, t.task_text,
           ROW_NUMBER() OVER (
             PARTITION BY b.source, b.benchmark_name, b.task, b.benchmark_version
             ORDER BY CASE WHEN b.score_direction = 'lower_better'
                           THEN -b.score ELSE b.score END DESC,
                      COALESCE(b.evaluation_date, b.model_release_date,
                               b.collected_at::date) DESC,
                      b.model_name
           ) AS score_rank
    FROM benchmark_results b
    JOIN benchmark_task_descriptions t
      ON b.benchmark_name = t.benchmark_name AND b.task = t.task
    WHERE b.score IS NOT NULL AND LENGTH(TRIM(t.task_text)) > 15
), latest_available_series AS (
    SELECT *, ROW_NUMBER() OVER (
       PARTITION BY source, benchmark_name, task
       ORDER BY COALESCE(evaluation_date, model_release_date,
                         collected_at::date) DESC,
                benchmark_version DESC
    ) AS series_rank
    FROM best_per_version WHERE score_rank = 1
)
SELECT source, benchmark_name, benchmark_version, task, domain,
       model_name, score, score_direction, score_unit,
       evaluation_date, model_release_date, collected_at, source_url, raw_metadata, task_text
FROM latest_available_series
WHERE series_rank = 1
ORDER BY source, benchmark_name, task
"""


def _iso_value(value: Any) -> str:
    if value is None:
        return ""
    return value.isoformat() if hasattr(value, "isoformat") else str(value)


def _date_fields(benchmark: dict[str, Any]) -> dict[str, str]:
    evaluation_date = _iso_value(benchmark.get("evaluation_date"))
    raw = benchmark.get("raw_metadata") or {}
    if isinstance(raw, dict) and raw.get("migrated_from") == "ai_benchmark_measurements":
        evaluation_date = ""  # Legacy imported rows used retrieval dates; do not repeat that claim.
    model_release_date = _iso_value(benchmark.get("model_release_date"))
    collected_at = _iso_value(benchmark.get("collected_at"))
    if evaluation_date:
        date_label, date_value = "Evaluation date", evaluation_date[:10]
    elif model_release_date:
        date_label, date_value = "Model release date", model_release_date[:10]
    elif collected_at:
        date_label, date_value = "Record collected", collected_at[:10]
    else:
        date_label, date_value = "", ""
    return {
        "evaluation_date": evaluation_date,
        "model_release_date": model_release_date,
        "collected_at": collected_at,
        "date_label": date_label,
        "date_value": date_value,
    }


def _task_key(match: dict[str, Any]) -> tuple[str, ...]:
    return (
        match["source"],
        match["benchmark"],
        match["benchmark_version"],
        match["benchmark_task_id"] or match["task"],
        match["task"],
    )


def _group_task_matches(matches: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Group MiniLM skill candidates under their measured benchmark task."""
    groups: dict[tuple[str, ...], dict[str, Any]] = {}
    for match in matches:
        key = _task_key(match)
        group = groups.get(key)
        if group is None:
            group = {
                name: match[name]
                for name in (
                    "capability", "task", "benchmark_task_id", "benchmark",
                    "benchmark_version", "source", "source_url", "model",
                    "score", "score_direction", "score_unit", "evaluation_date",
                    "model_release_date", "collected_at", "date_label", "date_value",
                )
            }
            group.update({
                "relationship_type": "semantic_candidate",
                "independently_verified": False,
                "skills": [],
                "_skills_by_uri": {},
            })
            groups[key] = group

        skill = {
            "skill": match["skill"],
            "skill_uri": match["skill_uri"],
            "relation": match["relation"],
            "similarity": match["similarity"],
            "relationship_type": "semantic_candidate",
            "independently_verified": False,
        }
        previous = group["_skills_by_uri"].get(skill["skill_uri"])
        if previous is None or skill["similarity"] > previous["similarity"]:
            group["_skills_by_uri"][skill["skill_uri"]] = skill

    grouped = []
    for group in groups.values():
        group["skills"] = sorted(
            group.pop("_skills_by_uri").values(),
            key=lambda skill: (
                -skill["similarity"],
                skill["relation"] != "essential",
                skill["skill"].casefold(),
            ),
        )
        grouped.append(group)

    grouped.sort(key=lambda group: (
        group["source"] == "artificial_analysis",
        not any(skill["relation"] == "essential" for skill in group["skills"]),
        -max((skill["similarity"] for skill in group["skills"]), default=0.0),
        group["benchmark"].casefold(),
        group["task"].casefold(),
    ))
    return grouped


@lru_cache(maxsize=3)
def _benchmark_baseline(bucket: int) -> tuple[dict[str, Any], ...]:
    """Get best observed scores from an available version of each task series.

    Caveat: where multiple benchmark versions are present, the 'latest' version
    is chosen from the dated evidence available in the DB; this is a pragmatic
    MVP and should be replaced with a curated version release ordering.
    """
    from benchmark_store import connect

    with connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute(SQL)
            rows = cursor.fetchall()
            columns = [column.name for column in cursor.description]

    out = []
    for values in rows:
        record = dict(zip(columns, values))
        # An observed higher-better score of zero is not evidence of success.
        if record["score_direction"] != "lower_better" and float(record["score"]) <= 0:
            continue
        out.append(record)
    return tuple(out[:MAX_TASKS])


@lru_cache(maxsize=3)
def _task_skill_candidates(bucket: int) -> tuple[dict[str, Any], ...]:
    """Cache MiniLM retrieval per unique benchmark task text for one hour."""
    from futuretwin_skill_api import match_skills

    # Reuse retrieval results across benchmarks that describe the same task.
    matches_by_task: dict[str, list[dict[str, Any]]] = {}
    task_records = []
    for record in _benchmark_baseline(bucket):
        description = record["task_text"]
        if description not in matches_by_task:
            matches_by_task[description] = match_skills(
                description, top_k=PER_TASK_TOP_K
            )
        task_records.append({**record, "candidates": matches_by_task[description]})
    return tuple(task_records)


def get_occupation_baseline(occupation_uri: str) -> dict[str, Any]:
    """Return candidate task overlaps for one ESCO occupation, without using
    the latest-two-snapshots advancement check.

    This is potential task exposure, not estimated probability of automation.
    """
    from futuretwin_occupation_api import _load_esco

    _, _, occupation_skills = _load_esco()
    groups = occupation_skills.get(occupation_uri, {"essential": [], "optional": []})
    skill_by_uri = {
        row["uri"]: {"label": row["label"], "relation": rel}
        for rel in ("essential", "optional")
        for row in groups.get(rel, [])
    }
    if not skill_by_uri:
        return {"status": "not_enough_data", "links": [],
                "note": "No ESCO skill relationships are available for this occupation."}

    bucket = int(time() // REFRESH_SECONDS)
    try:
        rows = _task_skill_candidates(bucket)
    except Exception:
        # Do not disclose DB connection string, secret values or raw tracebacks.
        return {"status": "unavailable", "links": [],
                "note": "Stored benchmark evidence or local MiniLM could not be loaded."}

    if not rows:
        return {"status": "not_enough_data", "links": [],
                "note": "No usable current benchmark scores and task descriptions are stored."}

    matches = []
    for benchmark in rows:
        for candidate in benchmark["candidates"]:
            uri = candidate.get("skill_uri")
            selected = skill_by_uri.get(uri)
            similarity = candidate.get("cosine_similarity")
            if not selected or similarity is None or float(similarity) < MIN_SIMILARITY:
                continue
            source = str(benchmark["source"])
            dates = _date_fields(benchmark)
            matches.append({
                "capability": str(benchmark["domain"] or benchmark["benchmark_name"]),
                "skill": selected["label"] or candidate.get("skill", ""),
                "skill_uri": uri,
                "relation": selected["relation"],
                "task": str(benchmark["task_text"]),
                "benchmark_task_id": str(benchmark["task"] or ""),
                "benchmark": str(benchmark["benchmark_name"]),
                "benchmark_version": str(benchmark["benchmark_version"]),
                "source": source,
                "source_url": str(benchmark["source_url"] or ""),
                "model": str(benchmark["model_name"]),
                "score": float(benchmark["score"]),
                "score_direction": str(benchmark["score_direction"] or ""),
                "score_unit": str(benchmark["score_unit"] or ""),
                **dates,
                "similarity": round(float(similarity), 4),
                "relationship_type": "semantic_candidate",
                "independently_verified": False,
            })

    if not matches:
        return {"status": "not_enough_data", "links": [],
                "note": "Benchmark evidence is available, but no sufficiently relevant ESCO skill overlap was retrieved for this occupation. This does not mean AI has no effect."}

    # Similarity ranks candidate relevance only; it is not an impact score.
    matches.sort(key=lambda m: (
        m["source"] == "artificial_analysis",
        m["relation"] != "essential",
        -m["similarity"],
    ))
    task_groups = _group_task_matches(matches)[:MAX_TASK_GROUPS]
    selected_group_keys = {_task_key(group) for group in task_groups}
    # Keep the old flat links field for API consumers that still use it.
    selected_links = [
        match for match in matches if _task_key(match) in selected_group_keys
    ][:MAX_LINKS]
    return {
        "status": "possible_links",  # compatible with existing career frontend
        "links": selected_links,
        "task_groups": task_groups,
        "note": (
            "Current benchmark baseline, separate from newly detected advances. "
            "ESCO skill links are MiniLM semantic candidates, not independently "
            "verified task relationships or validated automation, augmentation, "
            "or complementary-skill classifications. Similarity is not an "
            "automation probability."
        ),
        "basis": "current_benchmark_baseline",
        "benchmark_tasks_considered": len(rows),
    }
