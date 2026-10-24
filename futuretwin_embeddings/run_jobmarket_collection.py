"""FutureTwin Phase 2: job-market collection orchestrator.

Collects labour-market evidence from every connected source
(jobmarket_registry.py), deduplicates postings, extracts ESCO skills from ad
descriptions with the fine-tuned MiniLM, and logs coverage per run.

Usage:
  python3 futuretwin_embeddings/run_jobmarket_collection.py
  python3 futuretwin_embeddings/run_jobmarket_collection.py --source remotive
  python3 futuretwin_embeddings/run_jobmarket_collection.py --skip-skills
  python3 futuretwin_embeddings/run_jobmarket_collection.py --skill-limit 300

Never modifies the benchmark or legacy pipeline tables.
"""
from __future__ import annotations

import argparse
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import jobmarket_collectors
import jobmarket_store as store
from jobmarket_registry import SOURCES


def run(source_filter: str | None, skip_skills: bool, skill_limit: int,
        refresh_skills: bool = False) -> None:
    run_id = uuid.uuid4().hex[:12]
    started = datetime.now(timezone.utc)
    print(f"=== FutureTwin job-market collection run {run_id} ===\n", flush=True)

    with store.connect() as conn:
        store.ensure_schema(conn)
        conn.commit()

        names = ([source_filter] if source_filter
                 else list(jobmarket_collectors.COLLECTORS))
        totals = {"fetched": 0, "stored": 0, "duplicates": 0}

        for name in names:
            collector = jobmarket_collectors.COLLECTORS.get(name)
            if not collector:
                print(f"[{name}] no collector (status: "
                      f"{SOURCES.get(name, {}).get('access', 'unknown')})")
                continue
            t0 = datetime.now(timezone.utc)
            try:
                records, status = collector()
                if name == "opendosm":
                    result = {"stored": store.upsert_stats(conn, records),
                              "new": None, "updated": None, "duplicates": 0}
                else:
                    result = store.upsert_postings(conn, records)
                conn.commit()
                dates = sorted(
                    r.get("posted_date") or r.get("date") or ""
                    for r in records)
                dates = [d for d in dates if d]
                finished_at = datetime.now(timezone.utc)
                store.log_collection(conn, {
                    "run_id": run_id, "source": name,
                    "started_at": t0.isoformat(),
                    "finished_at": finished_at.isoformat(),
                    "fetched": len(records),
                    "stored": result["stored"],
                    "new_postings": result.get("new") or 0,
                    "duplicates": result["duplicates"],
                    "min_date": dates[0] if dates else None,
                    "max_date": dates[-1] if dates else None,
                    "status": "ok", "detail": status["detail"],
                })
                conn.commit()
                if name != "opendosm" and records:
                    store.record_posting_observations(
                        conn, run_id, name, records, finished_at)
                    conn.commit()
                totals["fetched"] += len(records)
                totals["stored"] += result["stored"]
                totals["duplicates"] += result["duplicates"]
                extra = (f"new {result['new']}, refreshed {result['updated']}, "
                         f"duplicates {result['duplicates']}"
                         if result.get("new") is not None
                         else f"{result['stored']} rows stored")
                print(f"[{name}] {status['status']}: {status['detail']} "
                      f"({extra})", flush=True)
            except Exception as exc:  # one source failing must not stop others
                conn.rollback()
                store.log_collection(conn, {
                    "run_id": run_id, "source": name,
                    "started_at": t0.isoformat(),
                    "finished_at": datetime.now(timezone.utc).isoformat(),
                    "fetched": 0, "stored": 0, "new_postings": 0,
                    "duplicates": 0,
                    "min_date": None, "max_date": None,
                    "status": "error", "detail": str(exc)[:500],
                })
                conn.commit()
                print(f"[{name}] ERROR: {exc}", flush=True)

        # Unavailable sources are logged as skipped, never silently dropped.
        for unavail in jobmarket_collectors.unavailable_sources():
            print(f"[{unavail['source']}] {unavail['status']}: "
                  f"{unavail['detail'][:110]}...")
            store.log_collection(conn, {
                "run_id": run_id, "source": unavail["source"],
                "started_at": started.isoformat(),
                "finished_at": datetime.now(timezone.utc).isoformat(),
                "fetched": 0, "stored": 0, "new_postings": 0, "duplicates": 0,
                "min_date": None, "max_date": None,
                "status": f"skipped ({unavail['status']})",
                "detail": unavail["detail"][:500],
            })
        conn.commit()

        # ---- ESCO skill extraction (fine-tuned MiniLM, unchanged) ----
        if skip_skills:
            print("\nSkill extraction skipped (--skip-skills).")
        else:
            pending = store.postings_needing_skills(
                conn, skill_limit, refresh=refresh_skills)
            print(f"\nExtracting ESCO skills for {len(pending)} new canonical "
                  f"postings (fine-tuned MiniLM)...", flush=True)
            from futuretwin_skill_api import match_skills
            from futuretwin_job_text import relevant_responsibilities
            done = 0
            for posting in pending:
                text = f"{posting['title']}. {relevant_responsibilities(posting['description_text'])[:1500]}"
                skills = match_skills(text, top_k=8)
                store.save_posting_skills(
                    conn, posting["source"], posting["source_posting_id"],
                    skills)
                done += 1
                if done % 50 == 0:
                    conn.commit()
                    print(f"  {done}/{len(pending)}...", flush=True)
            conn.commit()
            print(f"Skill extraction complete: {done} postings.", flush=True)

        # Store title/skill mapping methods and source-text evidence for this
        # batch. Historical observations are only added from this run forward.
        from futuretwin_opportunities import record_run_matches
        recorded = record_run_matches(conn, run_id)
        conn.commit()
        print(f"Stored {recorded['skills']} explicit skill and "
              f"{recorded['occupations']} exact/skill evidence matches; "
              f"{recorded['suggestions']} unverified MiniLM occupation "
              "suggestions.",
              flush=True)

    # ---- Run report ----
    print("\n=== RUN REPORT ===")
    print(f"Fetched {totals['fetched']} records; stored {totals['stored']}; "
          f"flagged {totals['duplicates']} duplicate advertisements.")
    for row in store.get_posting_coverage():
        print(f"  {row['source']}: {row['canonical']} canonical postings, "
              f"{row['duplicates']} duplicates, {row['with_skills']} with "
              f"skills, dates {row['earliest_posting']} → "
              f"{row['latest_posting']}")
    print(f"\nFinished in "
          f"{(datetime.now(timezone.utc) - started).seconds}s.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", choices=list(SOURCES), default=None,
                        help="collect only this source")
    parser.add_argument("--skip-skills", action="store_true",
                        help="collect postings without MiniLM skill extraction")
    parser.add_argument("--skill-limit", type=int, default=1500,
                        help="max postings to skill-extract per run")
    parser.add_argument("--refresh-skills", action="store_true",
                        help="Refresh local skill candidates; preserve historical observations.")
    args = parser.parse_args()
    run(args.source, args.skip_skills, args.skill_limit, args.refresh_skills)


if __name__ == "__main__":
    main()
