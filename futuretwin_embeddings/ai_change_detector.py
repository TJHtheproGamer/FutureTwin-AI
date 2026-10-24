
import os
import pandas as pd
import psycopg

from pathlib import Path

# ==========================================
# 1. PROJECT CONFIGURATION
# ==========================================

folder = Path(__file__).resolve().parent
data_folder = folder / "data"
data_folder.mkdir(exist_ok=True)

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL not found")

MIN_CHANGE = 0.5

# ==========================================
# 2. CONNECT TO POSTGRESQL
# ==========================================

print("Connecting to PostgreSQL...")

with psycopg.connect(DATABASE_URL) as conn:
    with conn.cursor() as cur:

        # Find the latest two saved snapshots
        cur.execute("""
            SELECT
                snapshot_name,
                MIN(collected_at) AS snapshot_time
            FROM ai_benchmark_measurements
            GROUP BY snapshot_name
            ORDER BY snapshot_time DESC,
                     snapshot_name DESC
            LIMIT 2
        """)

        snapshots = cur.fetchall()

        if len(snapshots) < 2:
            print("Not enough snapshots to compare.")
            raise SystemExit(0)

        latest_name = snapshots[0][0]
        previous_name = snapshots[1][0]

        print("Previous:", previous_name)
        print("Latest:", latest_name)

        # Retrieve measurements for both snapshots
        cur.execute("""
            SELECT
                snapshot_name,
                model_id,
                model_name,
                capability,
                score,
                benchmark_version
            FROM ai_benchmark_measurements
            WHERE snapshot_name IN (%s, %s)
        """, (previous_name, latest_name))

        rows = cur.fetchall()

# ==========================================
# 3. PREPARE DATA
# ==========================================

df = pd.DataFrame(
    rows,
    columns=[
        "snapshot_name",
        "model_id",
        "model_name",
        "capability",
        "score",
        "benchmark_version"
    ]
)

df["score"] = pd.to_numeric(
    df["score"],
    errors="coerce"
)

df = df.dropna(
    subset=["capability", "score"]
)

previous = df[
    df["snapshot_name"] == previous_name
]

latest = df[
    df["snapshot_name"] == latest_name
]

# ==========================================
# 4. COMPARE AI CAPABILITY SCORES
# ==========================================

results = []

capabilities = sorted(
    set(previous["capability"])
    | set(latest["capability"])
)

for capability in capabilities:

    old = previous[
        previous["capability"] == capability
    ]

    new = latest[
        latest["capability"] == capability
    ]

    if old.empty or new.empty:
        continue

    old_best = old.loc[old["score"].idxmax()]
    new_best = new.loc[new["score"].idxmax()]

    old_score = float(old_best["score"])
    new_score = float(new_best["score"])

    # Compare available benchmark version metadata
    old_versions = set(
        old["benchmark_version"]
        .dropna().astype(str)
    )

    new_versions = set(
        new["benchmark_version"]
        .dropna().astype(str)
    )

    comparable = (
        len(old_versions) == 1
        and old_versions == new_versions
    )

    # Check whether the previously leading
    # model is still represented
    old_leader_id = old_best["model_id"]

    old_leader_present = (
        pd.notna(old_leader_id)
        and old_leader_id in
        new["model_id"].values
    )

    change = (
        round(new_score - old_score, 4)
        if comparable and old_leader_present
        else None
    )

    results.append({
        "capability": capability,
        "previous_best": old_score,
        "latest_best": new_score,
        "change": change,
        "comparable": (
            comparable and old_leader_present
        ),
        "leading_model": new_best["model_name"],
        "previous_snapshot": previous_name,
        "latest_snapshot": latest_name
    })

comparison = pd.DataFrame(results)

# ==========================================
# 5. DISPLAY RESULTS
# ==========================================

print("\nAI CAPABILITY COMPARISON")

if comparison.empty:
    print("No comparable capability data found.")
    raise SystemExit(0)

print(
    comparison[
        [
            "capability",
            "previous_best",
            "latest_best",
            "change",
            "comparable"
        ]
    ].to_string(index=False)
)

# ==========================================
# 6. DETECT NEW IMPROVEMENTS
# ==========================================

advancements = comparison[
    (comparison["comparable"] == True)
    & (comparison["change"] >= MIN_CHANGE)
].copy()

if advancements.empty:
    print("\nNo qualifying AI benchmark")
    print("improvements detected.")

else:
    print("\nNEW AI ADVANCEMENTS DETECTED!")

    print(
        advancements[
            [
                "capability",
                "change",
                "leading_model"
            ]
        ].to_string(index=False)
    )

# ==========================================
# 7. SAVE DETECTION RESULTS
# ==========================================

comparison.to_csv(
    data_folder / "ai_capability_changes.csv",
    index=False
)

advancements.to_csv(
    data_folder / "detected_ai_advancements.csv",
    index=False
)

print("\nDatabase comparison completed!")
