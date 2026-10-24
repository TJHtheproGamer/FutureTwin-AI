"""FutureTwin: frontier advancement detection over normalized benchmark results.

An advancement = a model with a dated result on (benchmark, version) whose
score beats the previous best VALID result on that SAME benchmark version by
at least MIN_IMPROVEMENT points.

Deliberate properties:
  * Anchored on the historical best, not on the latest two snapshots —
    an unchanged snapshot is never treated as evidence that no progress
    occurred, and progress is detected whenever a dated new result arrives.
  * Same benchmark version only: cross-version comparisons are invalid.
  * Results without any date can enter the baseline but cannot BE an
    advancement (we cannot establish what they improved upon).
  * score_direction is respected (lower_better supported).
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from benchmark_store import connect, ensure_schema

MIN_IMPROVEMENT = 0.5  # absolute points on the benchmark's own scale


def _effective_date(row: dict) -> Any:
    return (
        row.get("evaluation_date")
        or row.get("model_release_date")
        or (row.get("collected_at").date() if row.get("collected_at") else None)
    )


def detect_frontier_advancements() -> list[dict[str, Any]]:
    """Recompute advancement events from benchmark_results and upsert them."""
    import pandas as pd

    with connect() as conn:
        ensure_schema(conn)
        with conn.cursor() as cur:
            cur.execute("""
                SELECT source, benchmark_name, benchmark_version, model_name,
                       score, score_direction, evaluation_date,
                       model_release_date, collected_at
                FROM benchmark_results
            """)
            rows = pd.DataFrame(cur.fetchall(), columns=[
                "source", "benchmark_name", "benchmark_version", "model_name",
                "score", "score_direction", "evaluation_date",
                "model_release_date", "collected_at",
            ])

    events: list[dict[str, Any]] = []
    now = datetime.now(timezone.utc)

    for (source, bench, version), group in rows.groupby(
        ["source", "benchmark_name", "benchmark_version"]
    ):
        entries = []
        for r in group.itertuples(index=False):
            effective = _effective_date({
                "evaluation_date": r.evaluation_date,
                "model_release_date": r.model_release_date,
                "collected_at": r.collected_at,
            })
            entries.append({
                "model": r.model_name,
                "score": float(r.score),
                "direction": r.score_direction or "higher_better",
                "date": effective,
            })
        # Deterministic order: dated results by date; undated first as baseline.
        entries.sort(key=lambda e: (e["date"] is not None, e["date"] or datetime.min.date()))

        best_score = None
        best_model = None
        best_date = None
        for entry in entries:
            score = entry["score"]
            if best_score is None:
                best_score, best_model, best_date = score, entry["model"], entry["date"]
                continue
            if entry["direction"] == "lower_better":
                improvement = best_score - score
            else:
                improvement = score - best_score
            qualifies = (
                improvement >= MIN_IMPROVEMENT
                and entry["date"] is not None
                and best_date is not None
                and entry["date"] > best_date
            )
            if qualifies:
                events.append({
                    "source": source,
                    "benchmark_name": bench,
                    "benchmark_version": version,
                    "model_name": entry["model"],
                    "previous_model": best_model,
                    "previous_best": round(best_score, 4),
                    "new_best": round(score, 4),
                    "improvement": round(improvement, 4),
                    "evaluation_date": entry["date"],
                    "detected_at": now.isoformat(),
                })
            if improvement > 0:
                best_score, best_model, best_date = score, entry["model"], entry["date"] or best_date

    with connect() as conn:
        ensure_schema(conn)
        with conn.cursor() as cur:
            # Recompute semantics: rebuild the table atomically.
            cur.execute("TRUNCATE frontier_advancements")
            cur.executemany("""
                INSERT INTO frontier_advancements (
                    source, benchmark_name, benchmark_version, model_name,
                    previous_model, previous_best, new_best, improvement,
                    evaluation_date, detected_at
                ) VALUES (
                    %(source)s, %(benchmark_name)s, %(benchmark_version)s,
                    %(model_name)s, %(previous_model)s, %(previous_best)s,
                    %(new_best)s, %(improvement)s, %(evaluation_date)s,
                    %(detected_at)s
                )
                ON CONFLICT (source, benchmark_name, benchmark_version, model_name)
                DO NOTHING
            """, events)
    return events


def main() -> None:
    events = detect_frontier_advancements()
    print(f"\nFRONTIER ADVANCEMENTS DETECTED: {len(events)}")
    for e in sorted(events, key=lambda x: (x["benchmark_name"], str(x["evaluation_date"]))):
        print(f"  {e['evaluation_date']}  {e['benchmark_name']:<38} "
              f"{e['previous_best']} -> {e['new_best']} "
              f"(+{e['improvement']})  {e['model_name']}")
    if not events:
        print("  None. That is a statement about dated new results,")
        print("  not proof that no AI progress occurred.")


if __name__ == "__main__":
    main()
