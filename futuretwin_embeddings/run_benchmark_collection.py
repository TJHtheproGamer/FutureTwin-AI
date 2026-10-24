"""FutureTwin: multi-source benchmark collection runner.

Runs every available source connector, stores normalized results and task
descriptions in PostgreSQL, then recomputes frontier advancements.

CLI:
  python3 futuretwin_embeddings/run_benchmark_collection.py           # full cycle
  python3 futuretwin_embeddings/run_benchmark_collection.py --status  # source report only

Never raises on a single source failure: every source reports its own status
so the dashboard and logs show exactly what connected and what did not.
"""
from __future__ import annotations

import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import uuid
from datetime import datetime, timezone

from benchmark_collectors import COLLECTORS, unavailable_sources
from benchmark_registry import SOURCES, task_descriptions
from benchmark_store import (
    connect,
    ensure_schema,
    log_collection,
    migrate_aa_history,
    upsert_results,
    upsert_task_descriptions,
)
from frontier_detector import detect_frontier_advancements


def run_collection() -> dict:
    run_id = uuid.uuid4().hex[:12]
    statuses = []
    totals = {}

    def log(source: str, started: datetime, records: int,
            status: str, detail: str) -> None:
        """Persist every source outcome so the dashboard can show collection
        status, last successful refresh and errors without digging logs."""
        with connect() as conn:
            ensure_schema(conn)
            log_collection(conn, {
                "run_id": run_id, "source": source,
                "started_at": started.isoformat(),
                "finished_at": datetime.now(timezone.utc).isoformat(),
                "records": records, "status": status,
                "detail": detail[:500],
            })
            conn.commit()

    with connect() as conn:
        ensure_schema(conn)
        upsert_task_descriptions(conn, task_descriptions())
        # Fold the existing AA snapshot history into the normalized store.
        # Read-only on ai_benchmark_measurements; the legacy pipeline is untouched.
        totals["aa_history_migrated"] = migrate_aa_history(conn)
        conn.commit()

    for source_key, collector in COLLECTORS.items():
        started = datetime.now(timezone.utc)
        try:
            records, status = collector()
        except Exception as exc:  # one bad source must not kill the cycle
            traceback.print_exc()
            statuses.append({"source": source_key, "status": "error",
                             "detail": str(exc)})
            log(source_key, started, 0, "error", str(exc))
            continue
        statuses.append(status)
        if records:
            with connect() as conn:
                ensure_schema(conn)
                totals[source_key] = upsert_results(conn, records)
                conn.commit()
        log(source_key, started, len(records), "ok", status["detail"])

    for unavail in unavailable_sources():
        statuses.append(unavail)
        log(unavail["source"], datetime.now(timezone.utc), 0,
            f"skipped ({unavail['status']})", unavail["detail"])

    events = detect_frontier_advancements()
    return {"statuses": statuses, "stored": totals,
            "frontier_advancements": len(events)}


def print_report(report: dict) -> None:
    print("\n========================================")
    print("MULTI-SOURCE BENCHMARK COLLECTION REPORT")
    print("========================================")
    for status in report["statuses"]:
        meta = SOURCES.get(status["source"], {})
        label = {"connected": "CONNECTED ", "paid": "PAID TIER ",
                 "local_only": "LOCAL ONLY", "error": "ERROR    "}.get(
            status["status"], status["status"])
        print(f"  [{label}] {meta.get('name', status['source'])}")
        print(f"             {status['detail']}")
    print("\nRecords stored this cycle:", report["stored"])
    print("Frontier advancements known:", report["frontier_advancements"])


def main() -> None:
    if "--status" in sys.argv:
        for status in unavailable_sources():
            print(status["source"], "->", status["status"])
        print("connected collectors:", ", ".join(sorted(COLLECTORS)))
        return
    print_report(run_collection())


if __name__ == "__main__":
    main()
