
import subprocess
import sys
from pathlib import Path

# Locate the current project folder
folder = Path(__file__).resolve().parent

def run_script(filename):

    print("\n" + "=" * 50)
    print("RUNNING:", filename)
    print("=" * 50)

    subprocess.run(
        [sys.executable, str(folder / filename)],
        check=True
    )

# STEPS 1-3 are guarded like steps 4-5: a failure in one API or collector
# must not interrupt the monitoring cycle. Steps 2-3 work from PostgreSQL
# snapshots, so they stay meaningful even if collection fails (e.g. the
# Artificial Analysis free tier rate-limits).
for step in (
    "ai_capability_tracker.py",    # STEP 1: Collect latest AI benchmarks
    "ai_change_detector.py",       # STEP 2: Detect AI advancement
    "ai_impact_pipeline.py",       # STEP 3: Find affected skills and jobs
):
    try:
        run_script(step)
    except subprocess.CalledProcessError as exc:
        print(f"WARNING: {step} failed: {exc}")

# STEP 4: Multi-source benchmark collection (non-fatal: free sources can
# rate-limit; a failure here must not fail the whole monitoring cycle)
try:
    run_script("run_benchmark_collection.py")
except subprocess.CalledProcessError as exc:
    print("WARNING: benchmark collection step failed:", exc)

# STEP 5: Job-market evidence collection (non-fatal: free job-board APIs can
# fail or rate-limit. Postings are upserted idempotently, deduplicated by
# content hash, and never deleted, so history survives source API churn.
# Each source is isolated inside the runner; a failure here must not fail
# the whole monitoring cycle either.)
try:
    run_script("run_jobmarket_collection.py")
except subprocess.CalledProcessError as exc:
    print("WARNING: job-market collection step failed:", exc)

print("\n====================================")
print("FUTURETWIN MONITORING CYCLE FINISHED")
print("====================================")
