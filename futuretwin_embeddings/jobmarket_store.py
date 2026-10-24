"""FutureTwin Phase 2: job-market evidence storage.

PostgreSQL tables for job advertisements and labour-market statistics,
created alongside (never replacing) all existing FutureTwin tables:

  job_postings              one row per source posting, dedup-aware
  job_posting_skills        ESCO skills extracted per posting (fine-tuned MiniLM)
  jobmarket_stats           generic statistics series (OpenDOSM): dims + metrics JSONB
  jobmarket_collection_log  per-run coverage tracking (req 4)

Dedup rule (req 4): a posting is canonical unless another posting with the
same content hash (normalized title+employer+description) already exists;
duplicates are stored with duplicate_of set and excluded from trend queries.
"""
from __future__ import annotations

import hashlib
import json
import os
from typing import Any

import psycopg

SCHEMA = """
CREATE TABLE IF NOT EXISTS job_postings (
    source TEXT NOT NULL,
    source_posting_id TEXT NOT NULL,
    title TEXT NOT NULL,
    employer TEXT NOT NULL DEFAULT '',
    country TEXT NOT NULL DEFAULT '',
    location TEXT NOT NULL DEFAULT '',
    remote BOOLEAN NOT NULL DEFAULT TRUE,
    category TEXT NOT NULL DEFAULT '',
    posted_date DATE,
    source_updated_at TIMESTAMPTZ,
    expires_at TIMESTAMPTZ,
    url TEXT NOT NULL DEFAULT '',
    description_text TEXT NOT NULL DEFAULT '',
    workplace_type TEXT,
    seniority TEXT,
    employment_type TEXT,
    salary_min NUMERIC,
    salary_max NUMERIC,
    salary_currency TEXT,
    salary_period TEXT,
    salary_text TEXT,
    content_hash TEXT NOT NULL,
    duplicate_of TEXT,
    skills_extracted BOOLEAN NOT NULL DEFAULT FALSE,
    collected_at TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (source, source_posting_id)
);
ALTER TABLE job_postings ADD COLUMN IF NOT EXISTS source_updated_at TIMESTAMPTZ;
ALTER TABLE job_postings ADD COLUMN IF NOT EXISTS expires_at TIMESTAMPTZ;
ALTER TABLE job_postings ADD COLUMN IF NOT EXISTS workplace_type TEXT;
ALTER TABLE job_postings ADD COLUMN IF NOT EXISTS seniority TEXT;
ALTER TABLE job_postings ADD COLUMN IF NOT EXISTS employment_type TEXT;
ALTER TABLE job_postings ADD COLUMN IF NOT EXISTS salary_min NUMERIC;
ALTER TABLE job_postings ADD COLUMN IF NOT EXISTS salary_max NUMERIC;
ALTER TABLE job_postings ADD COLUMN IF NOT EXISTS salary_currency TEXT;
ALTER TABLE job_postings ADD COLUMN IF NOT EXISTS salary_period TEXT;
ALTER TABLE job_postings ADD COLUMN IF NOT EXISTS salary_text TEXT;
ALTER TABLE job_postings ALTER COLUMN remote DROP NOT NULL;
ALTER TABLE job_postings ALTER COLUMN remote DROP DEFAULT;
CREATE INDEX IF NOT EXISTS job_postings_hash_idx ON job_postings (content_hash);
CREATE INDEX IF NOT EXISTS job_postings_posted_idx ON job_postings (posted_date);

CREATE TABLE IF NOT EXISTS job_posting_skills (
    source TEXT NOT NULL,
    source_posting_id TEXT NOT NULL,
    skill_uri TEXT NOT NULL,
    skill TEXT NOT NULL,
    cosine_similarity DOUBLE PRECISION NOT NULL,
    PRIMARY KEY (source, source_posting_id, skill_uri)
);

CREATE TABLE IF NOT EXISTS jobmarket_stats (
    source TEXT NOT NULL,
    dataset TEXT NOT NULL,
    date DATE NOT NULL,
    dims JSONB NOT NULL,
    metrics JSONB NOT NULL,
    collected_at TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (source, dataset, date, dims)
);

CREATE TABLE IF NOT EXISTS jobmarket_collection_log (
    run_id TEXT NOT NULL,
    source TEXT NOT NULL,
    started_at TIMESTAMPTZ NOT NULL,
    finished_at TIMESTAMPTZ NOT NULL,
    fetched INT NOT NULL DEFAULT 0,
    stored INT NOT NULL DEFAULT 0,
    new_postings INT NOT NULL DEFAULT 0,
    duplicates INT NOT NULL DEFAULT 0,
    min_date DATE,
    max_date DATE,
    status TEXT NOT NULL,
    detail TEXT NOT NULL DEFAULT '',
    PRIMARY KEY (run_id, source)
);

-- Idempotent upgrade for tables created before new_postings existed.
ALTER TABLE jobmarket_collection_log
    ADD COLUMN IF NOT EXISTS new_postings INT NOT NULL DEFAULT 0;

-- One immutable row per source posting observed in a collection batch.
-- Observation timestamps are separate from the original posting date.
CREATE TABLE IF NOT EXISTS job_posting_observations (
    run_id TEXT NOT NULL,
    source TEXT NOT NULL,
    source_posting_id TEXT NOT NULL,
    observed_at TIMESTAMPTZ NOT NULL,
    original_posted_date DATE,
    title TEXT NOT NULL,
    country TEXT NOT NULL DEFAULT '',
    location TEXT NOT NULL DEFAULT '',
    remote BOOLEAN,
    content_hash TEXT NOT NULL,
    duplicate_of TEXT,
    PRIMARY KEY (run_id, source, source_posting_id),
    FOREIGN KEY (run_id, source)
        REFERENCES jobmarket_collection_log (run_id, source),
    FOREIGN KEY (source, source_posting_id)
        REFERENCES job_postings (source, source_posting_id)
);
ALTER TABLE job_posting_observations ALTER COLUMN remote DROP NOT NULL;
ALTER TABLE job_posting_observations ALTER COLUMN remote DROP DEFAULT;
ALTER TABLE job_posting_observations
    ADD COLUMN IF NOT EXISTS source_fetched_at TIMESTAMPTZ;
CREATE INDEX IF NOT EXISTS job_posting_observations_seen_idx
    ON job_posting_observations (source, source_posting_id, observed_at);

-- Evidence is recorded per collection batch; MiniLM similarity remains a
-- candidate score and is never treated as proof without a literal term.
CREATE TABLE IF NOT EXISTS job_posting_skill_observations (
    run_id TEXT NOT NULL,
    source TEXT NOT NULL,
    source_posting_id TEXT NOT NULL,
    skill_uri TEXT NOT NULL,
    skill_label TEXT NOT NULL,
    matched_term TEXT NOT NULL,
    evidence_quote TEXT NOT NULL,
    cosine_similarity DOUBLE PRECISION NOT NULL,
    matching_method TEXT NOT NULL,
    PRIMARY KEY (run_id, source, source_posting_id, skill_uri),
    FOREIGN KEY (run_id, source, source_posting_id)
        REFERENCES job_posting_observations (run_id, source, source_posting_id)
);

-- Occupation links retain their method and the explicit skill evidence that
-- supported them; title matches and skill-related candidates remain distinct.
CREATE TABLE IF NOT EXISTS job_posting_occupation_matches (
    run_id TEXT NOT NULL,
    source TEXT NOT NULL,
    source_posting_id TEXT NOT NULL,
    occupation_uri TEXT NOT NULL,
    mapping_method TEXT NOT NULL,
    supporting_skill_uris JSONB NOT NULL DEFAULT '[]'::jsonb,
    evidence_quote TEXT NOT NULL DEFAULT '',
    PRIMARY KEY (run_id, source, source_posting_id, occupation_uri, mapping_method),
    FOREIGN KEY (run_id, source, source_posting_id)
        REFERENCES job_posting_observations (run_id, source, source_posting_id)
);

-- Current semantic suggestions are kept separate from observed title/skill
-- matches and from collection timestamps. They are never verified links.
CREATE TABLE IF NOT EXISTS job_posting_occupation_suggestions (
    source TEXT NOT NULL,
    source_posting_id TEXT NOT NULL,
    occupation_uri TEXT NOT NULL,
    model_signature TEXT NOT NULL,
    candidate_rank INT NOT NULL,
    cosine_similarity DOUBLE PRECISION NOT NULL,
    supporting_skill_uris JSONB NOT NULL DEFAULT '[]'::jsonb,
    evidence_quote TEXT NOT NULL DEFAULT '',
    predicted_at TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (source, source_posting_id, occupation_uri, model_signature),
    FOREIGN KEY (source, source_posting_id)
        REFERENCES job_postings (source, source_posting_id)
);
CREATE INDEX IF NOT EXISTS job_posting_occupation_suggestions_uri_idx
    ON job_posting_occupation_suggestions (occupation_uri, cosine_similarity);

-- No legacy rows are backfilled: first/last seen become available only after
-- the collector has captured actual observation batches.
CREATE OR REPLACE VIEW job_posting_observation_lifecycle AS
SELECT source, source_posting_id,
       MIN(observed_at) AS first_seen_at,
       MAX(observed_at) AS last_seen_at,
       COUNT(DISTINCT run_id) AS observation_count
FROM job_posting_observations
WHERE duplicate_of IS NULL
GROUP BY source, source_posting_id;
"""

POSTING_COLUMNS = [
    "source", "source_posting_id", "title", "employer", "country", "location",
    "remote", "category", "posted_date", "source_updated_at", "expires_at", "url",
    "description_text", "workplace_type", "seniority", "employment_type",
    "salary_min", "salary_max", "salary_currency", "salary_period",
    "salary_text",
    "content_hash", "duplicate_of", "collected_at",
]


def connect() -> psycopg.Connection:
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL not found")
    return psycopg.connect(database_url)


def ensure_schema(conn: psycopg.Connection) -> None:
    with conn.cursor() as cur:
        cur.execute(SCHEMA)


def content_hash(title: str, employer: str, description: str, location: str = "") -> str:
    """Conservative duplicate key: full source text and explicit location."""
    norm = " ".join(
        f"{title}|{employer}|{location}|{description}".lower().split())
    return hashlib.sha1(norm.encode("utf-8")).hexdigest()


def upsert_postings(conn: psycopg.Connection,
                    records: list[dict[str, Any]]) -> dict[str, int]:
    """Idempotently store postings; flag duplicates by content hash."""
    if not records:
        return {"stored": 0, "duplicates": 0}
    hashes = [r["content_hash"] for r in records]
    with conn.cursor() as cur:
        cur.execute(
            "SELECT content_hash, source, source_posting_id, duplicate_of FROM job_postings "
            "WHERE content_hash = ANY(%s)",
            (hashes,))
        existing: dict[str, set[tuple]] = {}
        canonical_holders = {}
        for h, src, pid, duplicate in cur.fetchall():
            existing.setdefault(h, set()).add((src, pid))
            if duplicate is None:
                canonical_holders.setdefault(h, set()).add((src, pid))
        keys = [(r["source"], r["source_posting_id"]) for r in records]
        cur.execute(
            "SELECT p.source, p.source_posting_id FROM job_postings p "
            "JOIN (VALUES " + ",".join(["(%s,%s)"] * len(keys)) + ") AS v(s, i) "
            "ON p.source = v.s AND p.source_posting_id = v.i",
            tuple(x for k in keys for x in k))
        existing_keys = set(cur.fetchall())
    members = {h: set(keys) for h, keys in existing.items()}
    for r in records:
        members.setdefault(r["content_hash"], set()).add(
            (r["source"], r["source_posting_id"]))
    canonical = {
        h: min(canonical_holders.get(h) or keys)
        for h, keys in members.items()
    }
    duplicates = 0
    for r in records:
        h = r["content_hash"]
        # Keep one stable canonical even when every member is refreshed.
        if (r["source"], r["source_posting_id"]) != canonical[h]:
            r["duplicate_of"] = h
            duplicates += 1
        else:
            r["duplicate_of"] = None
    placeholders = ", ".join(["%s"] * len(POSTING_COLUMNS))
    columns = ", ".join(POSTING_COLUMNS)
    updates = ", ".join(
        f"{c} = EXCLUDED.{c}" for c in POSTING_COLUMNS
        if c not in ("source", "source_posting_id"))
    rows = [tuple(r.get(c) for c in POSTING_COLUMNS) for r in records]
    with conn.cursor() as cur:
        cur.executemany(f"""
            INSERT INTO job_postings ({columns}) VALUES ({placeholders})
            ON CONFLICT (source, source_posting_id) DO UPDATE SET {updates}
        """, rows)
        # Repair all-duplicate groups left by older collectors without
        # deleting advertisements or historical observations.
        cur.execute("""
            WITH ranked AS (
              SELECT source, source_posting_id, content_hash,
                     ROW_NUMBER() OVER (
                       PARTITION BY content_hash
                       ORDER BY (duplicate_of IS NOT NULL), source, source_posting_id
                     ) AS n
              FROM job_postings WHERE content_hash = ANY(%s)
            )
            UPDATE job_postings p
            SET duplicate_of = CASE WHEN r.n = 1 THEN NULL ELSE r.content_hash END
            FROM ranked r
            WHERE p.source = r.source AND p.source_posting_id = r.source_posting_id
        """, (hashes,))
    new_count = sum(1 for k in keys if k not in existing_keys)
    # Postings are never deleted: history survives even when a listing
    # disappears from the source API (req 4).
    return {"stored": len(rows), "new": new_count,
            "updated": len(rows) - new_count, "duplicates": duplicates}


def upsert_stats(conn: psycopg.Connection, records: list[dict[str, Any]]) -> int:
    if not records:
        return 0
    rows = [{
        **r,
        "dims": json.dumps(r.get("dims") or {}),
        "metrics": json.dumps(r.get("metrics") or {}),
    } for r in records]
    with conn.cursor() as cur:
        cur.executemany("""
            INSERT INTO jobmarket_stats
                (source, dataset, date, dims, metrics, collected_at)
            VALUES (%(source)s, %(dataset)s, %(date)s, %(dims)s, %(metrics)s,
                    %(collected_at)s)
            ON CONFLICT (source, dataset, date, dims) DO UPDATE SET
                metrics = EXCLUDED.metrics,
                collected_at = EXCLUDED.collected_at
        """, rows)
    return len(rows)


def log_collection(conn: psycopg.Connection, entry: dict[str, Any]) -> None:
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO jobmarket_collection_log
                (run_id, source, started_at, finished_at, fetched, stored,
                 new_postings, duplicates, min_date, max_date, status, detail)
            VALUES (%(run_id)s, %(source)s, %(started_at)s, %(finished_at)s,
                    %(fetched)s, %(stored)s, %(new_postings)s, %(duplicates)s,
                    %(min_date)s, %(max_date)s, %(status)s, %(detail)s)
            ON CONFLICT (run_id, source) DO UPDATE SET
                finished_at = EXCLUDED.finished_at,
                fetched = EXCLUDED.fetched, stored = EXCLUDED.stored,
                new_postings = EXCLUDED.new_postings,
                duplicates = EXCLUDED.duplicates,
                min_date = EXCLUDED.min_date, max_date = EXCLUDED.max_date,
                status = EXCLUDED.status, detail = EXCLUDED.detail
        """, entry)


def record_posting_observations(
    conn: psycopg.Connection,
    run_id: str,
    source: str,
    records: list[dict[str, Any]],
    observed_at: Any,
) -> int:
    """Persist this batch's actual observation window without backfilling history."""
    if not records:
        return 0
    rows = [
        (
            run_id,
            source,
            str(record["source_posting_id"]),
            observed_at,
            record.get("posted_date") or None,
            str(record.get("title") or ""),
            str(record.get("country") or ""),
            str(record.get("location") or ""),
            record.get("remote"),
            str(record.get("content_hash") or ""),
            record.get("duplicate_of"),
            record.get("collected_at"),
        )
        for record in records
        if record.get("source_posting_id")
    ]
    with conn.cursor() as cur:
        cur.executemany("""
            INSERT INTO job_posting_observations
                (run_id, source, source_posting_id, observed_at,
                 original_posted_date, title, country, location, remote,
                 content_hash, duplicate_of, source_fetched_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (run_id, source, source_posting_id) DO UPDATE SET
                observed_at = EXCLUDED.observed_at,
                original_posted_date = EXCLUDED.original_posted_date,
                title = EXCLUDED.title, country = EXCLUDED.country,
                location = EXCLUDED.location, remote = EXCLUDED.remote,
                content_hash = EXCLUDED.content_hash,
                duplicate_of = EXCLUDED.duplicate_of
        """, rows)
    return len(rows)


def save_posting_skill_observations(
    conn: psycopg.Connection, rows: list[dict[str, Any]]
) -> int:
    if not rows:
        return 0
    with conn.cursor() as cur:
        cur.executemany("""
            INSERT INTO job_posting_skill_observations
                (run_id, source, source_posting_id, skill_uri, skill_label,
                 matched_term, evidence_quote, cosine_similarity, matching_method)
            VALUES (%(run_id)s, %(source)s, %(source_posting_id)s, %(skill_uri)s,
                    %(skill_label)s, %(matched_term)s, %(evidence_quote)s,
                    %(cosine_similarity)s, %(matching_method)s)
            ON CONFLICT (run_id, source, source_posting_id, skill_uri)
            DO UPDATE SET skill_label = EXCLUDED.skill_label,
                          matched_term = EXCLUDED.matched_term,
                          evidence_quote = EXCLUDED.evidence_quote,
                          cosine_similarity = EXCLUDED.cosine_similarity,
                          matching_method = EXCLUDED.matching_method
        """, rows)
    return len(rows)


def save_posting_occupation_matches(
    conn: psycopg.Connection, rows: list[dict[str, Any]]
) -> int:
    if not rows:
        return 0
    prepared = [
        {**row, "supporting_skill_uris": json.dumps(
            row.get("supporting_skill_uris") or [])}
        for row in rows
    ]
    with conn.cursor() as cur:
        cur.executemany("""
            INSERT INTO job_posting_occupation_matches
                (run_id, source, source_posting_id, occupation_uri,
                 mapping_method, supporting_skill_uris, evidence_quote)
            VALUES (%(run_id)s, %(source)s, %(source_posting_id)s,
                    %(occupation_uri)s, %(mapping_method)s,
                    %(supporting_skill_uris)s::jsonb, %(evidence_quote)s)
            ON CONFLICT
                (run_id, source, source_posting_id, occupation_uri, mapping_method)
            DO UPDATE SET supporting_skill_uris = EXCLUDED.supporting_skill_uris,
                          evidence_quote = EXCLUDED.evidence_quote
        """, prepared)
    return len(prepared)


def save_posting_occupation_suggestions(
    conn: psycopg.Connection, rows: list[dict[str, Any]]
) -> int:
    """Persist model-ranked candidates as suggestions, never as verified links."""
    if not rows:
        return 0
    prepared = [
        {**row, "supporting_skill_uris": json.dumps(
            row.get("supporting_skill_uris") or [])}
        for row in rows
    ]
    with conn.cursor() as cur:
        # Replace this derived candidate cache atomically; retain source ads,
        # observations and predictions from other model versions.
        cur.executemany("""
            DELETE FROM job_posting_occupation_suggestions
            WHERE source = %s AND source_posting_id = %s AND model_signature = %s
        """, sorted({
            (row["source"], row["source_posting_id"], row["model_signature"])
            for row in rows
        }))
        cur.executemany("""
            INSERT INTO job_posting_occupation_suggestions
                (source, source_posting_id, occupation_uri, model_signature,
                 candidate_rank, cosine_similarity, supporting_skill_uris,
                 evidence_quote, predicted_at)
            VALUES (%(source)s, %(source_posting_id)s, %(occupation_uri)s,
                    %(model_signature)s, %(candidate_rank)s,
                    %(cosine_similarity)s, %(supporting_skill_uris)s::jsonb,
                    %(evidence_quote)s, %(predicted_at)s)
            ON CONFLICT
                (source, source_posting_id, occupation_uri, model_signature)
            DO UPDATE SET candidate_rank = EXCLUDED.candidate_rank,
                          cosine_similarity = EXCLUDED.cosine_similarity,
                          supporting_skill_uris = EXCLUDED.supporting_skill_uris,
                          evidence_quote = EXCLUDED.evidence_quote,
                          predicted_at = EXCLUDED.predicted_at
        """, prepared)
    return len(prepared)


# =====================================
# SKILL EXTRACTION SUPPORT
# =====================================

def postings_needing_skills(conn: psycopg.Connection, limit: int,
                           refresh: bool = False) -> list[dict]:
    """Canonical postings with a description but no skill extraction yet."""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT source, source_posting_id, title, description_text
            FROM job_postings
            WHERE (%s OR skills_extracted = FALSE)
              AND duplicate_of IS NULL
              AND description_text <> ''
            ORDER BY posted_date DESC NULLS LAST
            LIMIT %s
        """, (refresh, limit))
        cols = [d.name for d in cur.description]
        return [dict(zip(cols, r)) for r in cur.fetchall()]


def save_posting_skills(conn: psycopg.Connection, source: str,
                        source_posting_id: str, skills: list[dict]) -> None:
    with conn.cursor() as cur:
        cur.executemany("""
            INSERT INTO job_posting_skills
                (source, source_posting_id, skill_uri, skill, cosine_similarity)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (source, source_posting_id, skill_uri)
            DO UPDATE SET skill = EXCLUDED.skill,
                          cosine_similarity = EXCLUDED.cosine_similarity
        """, [(source, source_posting_id, s["skill_uri"], s["skill"],
               float(s["cosine_similarity"])) for s in skills])
        cur.execute("""
            UPDATE job_postings SET skills_extracted = TRUE
            WHERE source = %s AND source_posting_id = %s
        """, (source, source_posting_id))


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


def get_posting_coverage() -> list[dict]:
    return _rows("""
        SELECT source,
               COUNT(*) AS postings,
               COUNT(*) FILTER (WHERE duplicate_of IS NULL) AS canonical,
               COUNT(*) FILTER (WHERE duplicate_of IS NOT NULL) AS duplicates,
               COUNT(*) FILTER (WHERE skills_extracted) AS with_skills,
               MIN(posted_date) AS earliest_posting,
               MAX(posted_date) AS latest_posting,
               MAX(collected_at) AS last_collected
        FROM job_postings GROUP BY source ORDER BY source
    """)


def get_skill_mentions() -> list[dict]:
    """Raw (posted_date, skill) pairs for canonical postings — small enough
    to aggregate honestly in Python."""
    return _rows("""
        SELECT p.source,p.source_posting_id,p.posted_date,s.skill,
               MAX(s.cosine_similarity) AS cosine_similarity
        FROM job_posting_skills s
        JOIN job_postings p USING (source, source_posting_id)
        WHERE p.duplicate_of IS NULL AND p.posted_date IS NOT NULL
        GROUP BY p.source,p.source_posting_id,p.posted_date,s.skill
    """)


def get_posting_dates() -> list[dict]:
    return _rows("""
        SELECT posted_date FROM job_postings
        WHERE duplicate_of IS NULL AND posted_date IS NOT NULL
    """)


def get_stats_series(dataset: str) -> list[dict]:
    return _rows("""
        SELECT date, dims, metrics FROM jobmarket_stats
        WHERE source = 'opendosm' AND dataset = %s
        ORDER BY date
    """, (dataset,))


def get_collection_log(limit: int = 20) -> list[dict]:
    return _rows("""
        SELECT * FROM jobmarket_collection_log
        ORDER BY finished_at DESC LIMIT %s
    """, (limit,))


def get_source_health() -> list[dict]:
    """Latest collection-log entry per source, any status."""
    return _rows("""
        SELECT DISTINCT ON (source) source, status, detail, finished_at
        FROM jobmarket_collection_log
        ORDER BY source, finished_at DESC
    """)


def get_source_successes() -> list[dict]:
    """Latest successful collection per source."""
    return _rows("""
        SELECT DISTINCT ON (source) source, finished_at
        FROM jobmarket_collection_log
        WHERE status = 'ok'
        ORDER BY source, finished_at DESC
    """)
