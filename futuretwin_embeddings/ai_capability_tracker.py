
import os
import sys
import json
import time
import requests
import pandas as pd

from pathlib import Path
from datetime import datetime, timezone

# ===================================
# 1. Set up project folders
# ===================================

folder = Path(__file__).resolve().parent
data_folder = folder / "data"
data_folder.mkdir(exist_ok=True)

# ===================================
# 2. API configuration
# ===================================

API_KEY = os.getenv("AA_API_KEY")

if not API_KEY:
    raise ValueError("Missing AA_API_KEY")

API_URL = (
    "https://artificialanalysis.ai/api/v2/"
    "language/models/free"
)

# Respect the AA free tier: 100 requests/day, resetting roughly daily
# (verified from x-ratelimit-* / retry-after headers on 2026-10-22).
# Paginating all models costs ~18 requests, so if today's snapshot is
# already stored, skip the API entirely — a second same-day run would burn
# quota for identical data.
_database_url = os.getenv("DATABASE_URL")
if _database_url:
    try:
        import psycopg as _psycopg
        with _psycopg.connect(_database_url) as _conn:
            with _conn.cursor() as _cur:
                _cur.execute("""
                    SELECT COUNT(*) FROM ai_benchmark_measurements
                    WHERE collected_at::date = CURRENT_DATE
                """)
                _already_today = _cur.fetchone()[0]
        if _already_today:
            print(f"Already collected {_already_today} measurements today; "
                  "skipping the AA API to respect the daily free-tier quota.")
            sys.exit(0)
    except Exception:
        pass  # check is an optimization; proceed to normal collection

# ===================================
# 3. Retrieve all model pages
# ===================================

models = []
page = 1
index_version = None

while True:

    # Polite backoff on free-tier rate limits (429). If the limit persists
    # this script still fails honestly — run_futuretwin.py guards the step
    # and the cycle continues with previously stored snapshots. We do NOT
    # reuse stale data under a fresh timestamp: that would fabricate
    # "current" measurements and corrupt trend detection.
    delay = 5.0
    for attempt in range(4):
        response = requests.get(
            API_URL,
            headers={"x-api-key": API_KEY},
            params={"page": page},
            timeout=30
        )
        if response.status_code != 429:
            break
        if attempt == 3:
            response.raise_for_status()
        print(f"Rate limited (429); retrying in {delay:.0f}s...")
        time.sleep(delay)
        delay *= 2

    response.raise_for_status()
    payload = response.json()

    models.extend(payload.get("data", []))

    index_version = payload.get(
        "intelligence_index_version"
    )

    print(
        f"Page {page}: "
        f"{len(payload.get('data', []))} models"
    )

    pagination = payload.get("pagination", {})

    if not pagination.get("has_more", False):
        break

    page += 1

print("\nTotal models:", len(models))

# ===================================
# 4. Define benchmark categories
# ===================================

CAPABILITIES = {
    "Coding": "artificial_analysis_coding_index",
    "Agentic AI": "artificial_analysis_agentic_index",
    "Finance": "artificial_analysis_finance_and_accounting_index",
    "Legal": "artificial_analysis_legal_index",
    "Healthcare": "artificial_analysis_healthcare_and_medical_index",
    "Engineering": "artificial_analysis_engineering_index",
    "Economics": "artificial_analysis_economics_index",
    "Strategy": "artificial_analysis_strategy_and_ops_index"
}

# ===================================
# 5. Extract capability scores
# ===================================

timestamp = datetime.now(timezone.utc)

records = []

for model in models:

    evaluations = model.get("evaluations") or {}

    for capability, field in CAPABILITIES.items():

        score = evaluations.get(field)

        if score is None:
            continue

        records.append({
            "collected_at": timestamp.isoformat(),
            "model_id": model.get("id"),
            "model_name": model.get("name"),
            "release_date": model.get("release_date"),
            "capability": capability,
            "score": score,
            "intelligence_index_version": index_version
        })

df = pd.DataFrame(records)

if df.empty:
    raise ValueError(
        "No capability measurements available."
    )

# ===================================
# 6. Show leading models
# ===================================

print("\nTOP 3 MODELS PER CAPABILITY")

for capability in CAPABILITIES:

    subset = df[
        df["capability"] == capability
    ].sort_values(
        "score",
        ascending=False
    )

    print("\nCAPABILITY:", capability)

    print(
        subset[
            ["model_name", "score", "release_date"]
        ].head(3).to_string(index=False)
    )

# ===================================
# 7. Save timestamped data
# ===================================

time_id = timestamp.strftime(
    "%Y%m%d_%H%M%S_%f"
)

csv_file = (
    data_folder /
    f"capabilities_{time_id}.csv"
)

json_file = (
    data_folder /
    f"ai_snapshot_{time_id}.json"
)

df.to_csv(csv_file, index=False)

snapshot = {
    "collected_at": timestamp.isoformat(),
    "source": "Artificial Analysis",
    "intelligence_index_version": index_version,
    "models": models
}

with open(json_file, "w", encoding="utf-8") as f:
    json.dump(snapshot, f, indent=2)

print("\nTracking snapshot completed!")
print("Models:", len(models))
print("Measurements:", len(df))
print("CSV:", csv_file)
print("JSON:", json_file)


# =====================================
# STEP 8: SAVE DIRECTLY TO POSTGRESQL
# =====================================

import psycopg

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL not found in Replit."
    )

print("\nSaving measurements to PostgreSQL...")

records = []

for i, row in df.iterrows():

    records.append((
        csv_file.name,
        int(i) + 1,
        row["collected_at"],
        str(row["model_id"])
        if pd.notna(row["model_id"])
        else None,
        row["model_name"],
        row["capability"],
        float(row["score"]),
        str(row["intelligence_index_version"])
        if pd.notna(row["intelligence_index_version"])
        else None
    ))

with psycopg.connect(DATABASE_URL) as conn:

    with conn.cursor() as cur:

        cur.execute("""
            CREATE TABLE IF NOT EXISTS
            ai_benchmark_measurements (
                snapshot_name TEXT NOT NULL,
                row_number INTEGER NOT NULL,
                collected_at TIMESTAMPTZ NOT NULL,
                model_id TEXT,
                model_name TEXT,
                capability TEXT NOT NULL,
                score DOUBLE PRECISION NOT NULL,
                benchmark_version TEXT,
                PRIMARY KEY (snapshot_name, row_number)
            )
        """)


        cur.executemany("""
            INSERT INTO ai_benchmark_measurements (
                snapshot_name,
                row_number,
                collected_at,
                model_id,
                model_name,
                capability,
                score,
                benchmark_version
            )
            VALUES (
                %s, %s, %s, %s,
                %s, %s, %s, %s
            )
            ON CONFLICT DO NOTHING
        """, records)

        cur.execute("""
            SELECT
                COUNT(DISTINCT snapshot_name),
                COUNT(*)
            FROM ai_benchmark_measurements
        """)

        snapshots, measurements = cur.fetchone()

print("\nDATABASE SAVE SUCCESSFUL!")
print("Total snapshots:", snapshots)
print("Total measurements:", measurements)
