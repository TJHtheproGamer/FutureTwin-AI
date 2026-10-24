"""FutureTwin: normalized multi-source benchmark result storage.

Creates and writes two PostgreSQL tables alongside (never replacing) the
existing ai_benchmark_measurements table:

  benchmark_results           one row per model x benchmark x version x task
  frontier_advancements       detected frontier improvements (see
                              frontier_detector.py)
  benchmark_task_descriptions preserved task texts for MiniLM skill matching

All writes are idempotent upserts, safe to re-run on every collection cycle.
"""
from __future__ import annotations

import os
from typing import Any

import psycopg

RESULT_COLUMNS = [
    "source", "benchmark_name", "benchmark_version", "domain", "task",
    "model_id", "model_name", "score", "score_direction", "score_unit",
    "evaluation_date", "model_release_date", "source_url", "collected_at",
    "raw_metadata",
]

SCHEMA = """
CREATE TABLE IF NOT EXISTS benchmark_results (
    source TEXT NOT NULL,
    benchmark_name TEXT NOT NULL,
    benchmark_version TEXT NOT NULL DEFAULT '',
    domain TEXT NOT NULL DEFAULT '',
    task TEXT NOT NULL DEFAULT '',
    model_id TEXT NOT NULL DEFAULT '',
    model_name TEXT NOT NULL,
    score DOUBLE PRECISION NOT NULL,
    score_direction TEXT NOT NULL DEFAULT 'higher_better',
    score_unit TEXT NOT NULL DEFAULT '',
    evaluation_date DATE,
    model_release_date DATE,
    source_url TEXT NOT NULL DEFAULT '',
    collected_at TIMESTAMPTZ NOT NULL,
    raw_metadata JSONB,
    PRIMARY KEY (source, benchmark_name, benchmark_version, task, model_name)
);

CREATE TABLE IF NOT EXISTS frontier_advancements (
    source TEXT NOT NULL,
    benchmark_name TEXT NOT NULL,
    benchmark_version TEXT NOT NULL DEFAULT '',
    model_name TEXT NOT NULL,
    previous_model TEXT,
    previous_best DOUBLE PRECISION,
    new_best DOUBLE PRECISION NOT NULL,
    improvement DOUBLE PRECISION NOT NULL,
    evaluation_date DATE,
    detected_at TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (source, benchmark_name, benchmark_version, model_name)
);

CREATE TABLE IF NOT EXISTS benchmark_task_descriptions (
    benchmark_name TEXT NOT NULL,
    task TEXT NOT NULL DEFAULT '',
    task_text TEXT NOT NULL,
    source TEXT NOT NULL DEFAULT '',
    PRIMARY KEY (benchmark_name, task)
);

CREATE TABLE IF NOT EXISTS benchmark_collection_log (
    run_id TEXT NOT NULL,
    source TEXT NOT NULL,
    started_at TIMESTAMPTZ NOT NULL,
    finished_at TIMESTAMPTZ NOT NULL,
    records INT NOT NULL DEFAULT 0,
    status TEXT NOT NULL,
    detail TEXT NOT NULL DEFAULT '',
    PRIMARY KEY (run_id, source)
);
"""


def connect() -> psycopg.Connection:
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL not found")
    return psycopg.connect(database_url)


def ensure_schema(conn: psycopg.Connection) -> None:
    with conn.cursor() as cur:
        cur.execute(SCHEMA)


def upsert_results(conn: psycopg.Connection, records: list[dict[str, Any]]) -> int:
    """Idempotently store normalized records; refresh score/date on conflict."""
    if not records:
        return 0
    import json

    rows = []
    for r in records:
        rows.append(tuple(
            json.dumps(r.get("raw_metadata")) if c == "raw_metadata"
            else r.get(c) for c in RESULT_COLUMNS
        ))
    placeholders = ", ".join(["%s"] * len(RESULT_COLUMNS))
    columns = ", ".join(RESULT_COLUMNS)
    with conn.cursor() as cur:
        cur.executemany(f"""
            INSERT INTO benchmark_results ({columns})
            VALUES ({placeholders})
            ON CONFLICT (source, benchmark_name, benchmark_version, task, model_name)
            DO UPDATE SET
                score = EXCLUDED.score,
                domain = EXCLUDED.domain,
                score_direction = EXCLUDED.score_direction,
                score_unit = EXCLUDED.score_unit,
                evaluation_date = EXCLUDED.evaluation_date,
                model_release_date = EXCLUDED.model_release_date,
                source_url = EXCLUDED.source_url,
                collected_at = EXCLUDED.collected_at,
                raw_metadata = EXCLUDED.raw_metadata
        """, rows)
    return len(rows)


def migrate_aa_history(conn: psycopg.Connection) -> int:
    """Copy existing ai_benchmark_measurements rows into benchmark_results.

    Read-only on the legacy table; gives the normalized store historical
    depth for Artificial Analysis indexes without touching the old pipeline.
    """
    # capability label in the legacy table -> registry field name
    capability_to_field = {
        "Coding": "artificial_analysis_coding_index",
        "Agentic AI": "artificial_analysis_agentic_index",
        "Finance": "artificial_analysis_finance_and_accounting_index",
        "Legal": "artificial_analysis_legal_index",
        "Healthcare": "artificial_analysis_healthcare_and_medical_index",
        "Engineering": "artificial_analysis_engineering_index",
        "Economics": "artificial_analysis_economics_index",
        "Strategy": "artificial_analysis_strategy_and_ops_index",
    }
    from benchmark_registry import AA_INDEXES

    with conn.cursor() as cur:
        cur.execute("""
            SELECT snapshot_name, collected_at, model_id, model_name,
                   capability, score, benchmark_version
            FROM ai_benchmark_measurements
        """)
        rows = cur.fetchall()

    records = []
    for snapshot, collected_at, model_id, model_name, capability, score, version in rows:
        field = capability_to_field.get(capability)
        if not field:
            continue
        bench, domain, _text = AA_INDEXES[field]
        records.append({
            "source": "artificial_analysis",
            "benchmark_name": bench,
            "benchmark_version": str(version or ""),
            "domain": domain,
            "task": "",
            "model_id": str(model_id or ""),
            "model_name": str(model_name),
            "score": float(score),
            "score_direction": "higher_better",
            "score_unit": "index points",
            "evaluation_date": None,  # Retrieval time is not a source evaluation date.
            "model_release_date": None,
            "source_url": "https://artificialanalysis.ai/",
            "collected_at": collected_at.isoformat() if collected_at else None,
            "raw_metadata": {"migrated_from": "ai_benchmark_measurements",
                             "evaluation_date_source": "not_published",
                             "snapshot_name": snapshot},
        })
    return upsert_results(conn, records)


def upsert_task_descriptions(conn: psycopg.Connection, rows: list[dict]) -> int:
    if not rows:
        return 0
    with conn.cursor() as cur:
        cur.executemany("""
            INSERT INTO benchmark_task_descriptions
                (benchmark_name, task, task_text, source)
            VALUES (%(benchmark_name)s, %(task)s, %(task_text)s, %(source)s)
            ON CONFLICT (benchmark_name, task)
            DO UPDATE SET task_text = EXCLUDED.task_text,
                          source = EXCLUDED.source
        """, rows)
    return len(rows)


def log_collection(conn: psycopg.Connection, entry: dict[str, Any]) -> None:
    """Record one source's collection outcome for the dashboard."""
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO benchmark_collection_log
                (run_id, source, started_at, finished_at, records,
                 status, detail)
            VALUES (%(run_id)s, %(source)s, %(started_at)s, %(finished_at)s,
                    %(records)s, %(status)s, %(detail)s)
            ON CONFLICT (run_id, source) DO UPDATE SET
                finished_at = EXCLUDED.finished_at,
                records = EXCLUDED.records, status = EXCLUDED.status,
                detail = EXCLUDED.detail
        """, entry)


# =====================================
# READ QUERIES (dashboard API)
# =====================================

def _rows(sql: str, params: tuple = ()) -> list[dict]:
    with connect() as conn:
        ensure_schema(conn)
        with conn.cursor() as cur:
            cur.execute(sql, params)
            columns = [d.name for d in cur.description]
            return [dict(zip(columns, r)) for r in cur.fetchall()]


def get_source_summaries() -> list[dict]:
    counts = {
        r["source"]: r for r in _rows("""
            SELECT source, COUNT(*) AS results,
                   COUNT(DISTINCT benchmark_name) AS benchmarks,
                   COUNT(DISTINCT model_name) AS models,
                   MAX(collected_at) AS last_collected
            FROM benchmark_results GROUP BY source
        """)
    }
    latest_run = {
        r["source"]: r for r in _rows("""
            SELECT DISTINCT ON (source) source, status, detail, finished_at
            FROM benchmark_collection_log
            ORDER BY source, finished_at DESC
        """)
    }
    last_success = {
        r["source"]: r["finished_at"] for r in _rows("""
            SELECT DISTINCT ON (source) source, finished_at
            FROM benchmark_collection_log
            WHERE status = 'ok'
            ORDER BY source, finished_at DESC
        """)
    }
    from benchmark_registry import SOURCES
    summaries = []
    for key, meta in SOURCES.items():
        c = counts.get(key, {})
        run = latest_run.get(key, {})
        summaries.append({
            "source": key,
            "name": meta["name"],
            "access": meta["access"],
            "url": meta["url"],
            "attribution": meta["attribution"],
            "note": meta["note"],
            "results": c.get("results", 0),
            "benchmarks": c.get("benchmarks", 0),
            "models": c.get("models", 0),
            "last_collected": str(c.get("last_collected") or ""),
            "last_status": run.get("status", ""),
            "last_run_at": str(run.get("finished_at") or ""),
            "last_error": (run.get("detail", "")
                           if run.get("status") == "error" else ""),
            "last_success": str(last_success.get(key) or ""),
        })
    return summaries


def get_domain_overview() -> list[dict]:
    return _rows("""
        SELECT domain,
               COUNT(DISTINCT benchmark_name) AS benchmarks,
               COUNT(DISTINCT model_name) AS models,
               COUNT(*) AS results,
               MAX(evaluation_date) AS latest_evaluation
        FROM benchmark_results
        WHERE domain <> ''
        GROUP BY domain
        ORDER BY results DESC
    """)


def get_benchmark_list() -> list[dict]:
    return _rows("""
        SELECT source, benchmark_name, benchmark_version, domain,
               COUNT(*) AS results,
               COUNT(DISTINCT model_name) AS models,
               MIN(evaluation_date) AS first_evaluation,
               MAX(evaluation_date) AS latest_evaluation,
               MAX(score) FILTER (WHERE score_direction = 'higher_better')
                   AS best_score,
               MIN(score) FILTER (WHERE score_direction = 'lower_better')
                   AS best_score_lower
        FROM benchmark_results
        GROUP BY source, benchmark_name, benchmark_version, domain
        ORDER BY benchmark_name, benchmark_version
    """)


def get_current_baseline(history_limit: int = 5) -> list[dict[str, Any]]:
    """Return the latest stored result for each comparable benchmark task series.

    Series are kept separate by source, benchmark version, task, unit, and score
    direction. Other model results are included only as same-series context.
    Collection timestamps remain labeled as collection dates, not evaluations.
    """
    rows = _rows("""
        WITH ranked AS (
            SELECT b.source, b.benchmark_name, b.benchmark_version, b.domain,
                   b.task, b.model_id, b.model_name, b.score,
                   b.score_direction, b.score_unit, b.evaluation_date,
                   b.model_release_date, b.source_url, b.collected_at, b.raw_metadata,
                   COALESCE(t.task_text, '') AS task_text,
                   ROW_NUMBER() OVER (
                     PARTITION BY b.source, b.benchmark_name,
                                  b.benchmark_version, b.domain, b.task,
                                  b.score_unit, b.score_direction
                     ORDER BY COALESCE(b.evaluation_date, b.model_release_date,
                                       b.collected_at::date) DESC NULLS LAST,
                              b.collected_at DESC,
                              CASE WHEN b.score_direction = 'lower_better'
                                   THEN b.score ELSE -b.score END ASC,
                              b.model_name
                   ) AS current_rank,
                   ROW_NUMBER() OVER (
                     PARTITION BY b.source, b.benchmark_name,
                                  b.benchmark_version, b.domain, b.task,
                                  b.score_unit, b.score_direction
                     ORDER BY COALESCE(b.evaluation_date, b.model_release_date,
                                       b.collected_at::date) DESC NULLS LAST,
                              b.collected_at DESC, b.model_name
                   ) AS history_rank
            FROM benchmark_results b
            LEFT JOIN benchmark_task_descriptions t
              ON b.benchmark_name = t.benchmark_name AND b.task = t.task
            WHERE b.score IS NOT NULL
        )
        SELECT source, benchmark_name, benchmark_version, domain, task,
               model_id, model_name, score, score_direction, score_unit,
               evaluation_date, model_release_date, source_url, collected_at,
                task_text, current_rank, history_rank, raw_metadata
        FROM ranked
        WHERE current_rank = 1 OR history_rank <= %s
        ORDER BY domain, benchmark_name, benchmark_version, task, history_rank
    """, (max(1, min(int(history_limit), 20)),))

    def iso(value: Any) -> str:
        return value.isoformat() if hasattr(value, "isoformat") else str(value or "")

    def format_result(row: dict[str, Any]) -> dict[str, Any]:
        evaluation = iso(row.get("evaluation_date"))
        raw = row.get("raw_metadata") or {}
        if isinstance(raw, dict) and raw.get("migrated_from") == "ai_benchmark_measurements":
            evaluation = ""
        release = iso(row.get("model_release_date"))
        collected = iso(row.get("collected_at"))
        if evaluation:
            date_label, date_value = "Evaluation date", evaluation[:10]
        elif release:
            date_label, date_value = "Model release date", release[:10]
        elif collected:
            date_label, date_value = "Record collected", collected[:10]
        else:
            date_label, date_value = "", ""
        return {
            "source": row.get("source") or "",
            "benchmark_name": row.get("benchmark_name") or "",
            "benchmark_version": row.get("benchmark_version") or "",
            "domain": row.get("domain") or "",
            "task": row.get("task") or "",
            "task_text": row.get("task_text") or "",
            "model_id": row.get("model_id") or "",
            "model_name": row.get("model_name") or "",
            "score": float(row["score"]) if row.get("score") is not None else None,
            "score_direction": row.get("score_direction") or "",
            "score_unit": row.get("score_unit") or "",
            "evaluation_date": evaluation,
            "model_release_date": release,
            "collected_at": collected,
            "date_label": date_label,
            "date_value": date_value,
            "source_url": row.get("source_url") or "",
        }

    grouped: dict[tuple[str, ...], dict[str, Any]] = {}
    for row in rows:
        key = tuple(str(row.get(name) or "") for name in (
            "source", "benchmark_name", "benchmark_version", "domain",
            "task", "score_unit", "score_direction",
        ))
        group = grouped.setdefault(key, {"current": None, "history": []})
        result = format_result(row)
        if int(row["current_rank"]) == 1:
            group["current"] = result
        if int(row["history_rank"]) <= max(1, min(int(history_limit), 20)):
            group["history"].append(result)

    output = []
    for group in grouped.values():
        current = group["current"]
        if current is None:
            continue
        current_model = current["model_id"] or current["model_name"]
        history = [
            item for item in group["history"]
            if (item["model_id"] or item["model_name"]) != current_model
        ]
        output.append({**current, "history": history})
    return output


def get_benchmark_results(benchmark: str, version: str | None = None,
                          days: int | None = None) -> list[dict]:
    sql = """
        SELECT model_name, score, score_direction, score_unit,
               evaluation_date, model_release_date, source, domain, task,
               collected_at
        FROM benchmark_results
        WHERE benchmark_name = %s
    """
    params: list = [benchmark]
    if version:
        sql += " AND benchmark_version = %s"
        params.append(version)
    if days:
        sql += " AND COALESCE(evaluation_date, model_release_date, collected_at::date) >= CURRENT_DATE - %s * INTERVAL '1 day'"
        params.append(days)
    sql += " ORDER BY score DESC NULLS LAST"
    return _rows(sql, tuple(params))


def get_frontier_events(benchmark: str | None = None, limit: int = 60) -> list[dict]:
    sql = """
        SELECT source, benchmark_name, benchmark_version, model_name,
               previous_model, previous_best, new_best, improvement,
               evaluation_date
        FROM frontier_advancements
    """
    params: list = []
    if benchmark:
        sql += " WHERE benchmark_name = %s"
        params.append(benchmark)
    sql += " ORDER BY evaluation_date DESC NULLS LAST LIMIT %s"
    params.append(limit)
    return _rows(sql, tuple(params))


def get_benchmark_tasks(benchmark: str) -> list[dict]:
    return _rows("""
        SELECT task, task_text, source
        FROM benchmark_task_descriptions
        WHERE benchmark_name = %s
        ORDER BY task
    """, (benchmark,))
