
import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer

# =====================================
# STEP 1: PROJECT CONFIGURATION
# =====================================

folder = Path(__file__).resolve().parent
data_folder = folder / "data"
data_folder.mkdir(exist_ok=True)

TOP_K = 20
MIN_SIMILARITY = 0.35

# Descriptions used to find related skills.
# These are broad semantic search prompts,
# NOT individual benchmark measurements.

CAPABILITY_TEXT = {
    "Coding": (
        "Write computer programs, generate software "
        "code, debug applications and test software."
    ),
    "Agentic AI": (
        "Plan and execute multi-step workflows, "
        "coordinate tasks and use digital tools."
    ),
    "Finance": (
        "Analyze financial statements, manage "
        "accounting information and financial data."
    ),
    "Legal": (
        "Analyze legal documents, research laws "
        "and prepare legal information."
    ),
    "Healthcare": (
        "Analyze medical information, interpret "
        "clinical records and support healthcare."
    ),
    "Engineering": (
        "Solve engineering problems, analyze "
        "technical systems and evaluate designs."
    ),
    "Economics": (
        "Analyze economic indicators, forecast "
        "economic trends and interpret statistics."
    ),
    "Strategy": (
        "Analyze business operations, develop "
        "strategies and plan organizational activities."
    )
}

# =====================================
# STEP 2: SELECT DETECTED ADVANCEMENTS
# =====================================

parser = argparse.ArgumentParser()

parser.add_argument(
    "--demo",
    choices=list(CAPABILITY_TEXT),
    help="Test one capability without claiming a real advancement"
)

args = parser.parse_args()

demo_mode = args.demo is not None

if demo_mode:

    print("\nDEMONSTRATION MODE")
    print("No real advancement is being claimed.")

    events = pd.DataFrame([{
        "capability": args.demo,
        "change": np.nan,
        "leading_model": "Demo only"
    }])

else:

    event_file = (
        data_folder / "detected_ai_advancements.csv"
    )

    if not event_file.exists():
        raise FileNotFoundError(
            "Run ai_change_detector.py first."
        )

    events = pd.read_csv(event_file)

    if not events.empty:

        events["change"] = pd.to_numeric(
            events["change"],
            errors="coerce"
        )

        events = events[
            events["comparable"].astype(str)
            .str.lower().eq("true")
            & (events["change"] >= 0.5)
        ].copy()

    if events.empty:
        print("\nNo new verified benchmark")
        print("advancements to process.")
        print("Use --demo Coding to test the pipeline.")
        raise SystemExit(0)

# =====================================
# STEP 3: LOAD ESCO DATABASE
# =====================================

print("\nLoading ESCO datasets...")

skills = pd.read_csv(
    folder / "skills_en.csv"
)

occupations = pd.read_csv(
    folder / "occupations_en.csv"
)

relation_files = sorted(
    folder.glob("occupationSkillRelations*.csv")
)

if not relation_files:
    raise FileNotFoundError(
        "ESCO relationship CSV not found."
    )

relations = pd.read_csv(relation_files[0])

skills = skills.dropna(
    subset=["conceptUri", "preferredLabel"]
).drop_duplicates("conceptUri").reset_index(drop=True)

occupations = occupations.dropna(
    subset=["conceptUri", "preferredLabel"]
).drop_duplicates("conceptUri")

relations = relations.dropna(
    subset=["occupationUri", "skillUri"]
).drop_duplicates(
    ["occupationUri", "skillUri"]
)

# =====================================
# STEP 4: GENERATE SKILL EMBEDDINGS
# =====================================

print("\nLoading MiniLM model...")

model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)

skill_texts = skills["preferredLabel"].astype(str)

if "description" in skills.columns:
    skill_texts = (
        skill_texts + ". " +
        skills["description"].fillna("").astype(str)
    )

print("Generating ESCO embeddings...")

skill_embeddings = model.encode(
    skill_texts.tolist(),
    batch_size=32,
    normalize_embeddings=True,
    show_progress_bar=True
)

# =====================================
# STEP 5: PREPARE ESCO RELATIONSHIPS
# =====================================

skill_lookup = skills[
    ["conceptUri", "preferredLabel"]
].rename(columns={
    "conceptUri": "skillUri",
    "preferredLabel": "skill"
})

occupation_lookup = occupations[
    ["conceptUri", "preferredLabel"]
].rename(columns={
    "conceptUri": "occupationUri",
    "preferredLabel": "occupation"
})

# Total skills recorded for each occupation
occupation_sizes = (
    relations.groupby("occupationUri")
    ["skillUri"]
    .nunique()
    .rename("total_esco_skills")
    .reset_index()
)

all_skill_results = []
all_job_results = []

# =====================================
# STEP 6: PROCESS EACH ADVANCEMENT
# =====================================

for _, event in events.iterrows():

    capability = event["capability"]

    if capability not in CAPABILITY_TEXT:
        print("Unknown capability:", capability)
        continue

    print("\n=================================")
    print("CAPABILITY:", capability)
    print("=================================")

    capability_text = CAPABILITY_TEXT[capability]

    # Convert capability text into embedding
    capability_embedding = model.encode(
        capability_text,
        normalize_embeddings=True
    )

    # Cosine similarity
    similarities = (
        skill_embeddings @ capability_embedding
    )

    # Find strongest skill matches
    top_indices = np.argsort(
        similarities
    )[::-1][:TOP_K]

    matched_skills = skills.iloc[
        top_indices
    ].copy()

    matched_skills["similarity"] = (
        similarities[top_indices]
    )

    # Filter very weak similarities
    matched_skills = matched_skills[
        matched_skills["similarity"]
        >= MIN_SIMILARITY
    ].copy()

    if matched_skills.empty:
        print("No skill matches above threshold.")
        continue

    matched_skills["capability"] = capability

    print("\nRELATED ESCO SKILLS")

    print(
        matched_skills[
            ["preferredLabel", "similarity"]
        ].to_string(index=False)
    )

    all_skill_results.append(matched_skills)

    # =====================================
    # STEP 7: MAP SKILLS TO OCCUPATIONS
    # =====================================

    matched_lookup = matched_skills[
        ["conceptUri", "similarity"]
    ].rename(columns={
        "conceptUri": "skillUri"
    })

    job_matches = relations.merge(
        matched_lookup,
        on="skillUri",
        how="inner"
    ).merge(
        skill_lookup,
        on="skillUri",
        how="inner"
    ).merge(
        occupation_lookup,
        on="occupationUri",
        how="inner"
    )

    # Assign exploratory relevance weights
    job_matches["essential"] = (
        job_matches["relationType"]
        .fillna("")
        .str.lower()
        .eq("essential")
    )

    job_matches["weight"] = np.where(
        job_matches["essential"],
        1.0,
        0.5
    )

    job_matches["weighted_similarity"] = (
        job_matches["similarity"]
        * job_matches["weight"]
    )

    # =====================================
    # STEP 8: CALCULATE OCCUPATION RELEVANCE
    # =====================================

    ranking = (
        job_matches.groupby(
            ["occupationUri", "occupation"],
            as_index=False
        )
        .agg(
            matched_skills=("skillUri", "nunique"),
            essential_matches=("essential", "sum"),
            average_similarity=("similarity", "mean"),
            weighted_sum=("weighted_similarity", "sum")
        )
    )

    ranking = ranking.merge(
        occupation_sizes,
        on="occupationUri",
        how="left"
    )

    # Exploratory ranking adjustment
    # Helps reduce bias toward occupations
    # with very large skill lists.
    ranking["relevance_score"] = (
        ranking["weighted_sum"] /
        np.sqrt(
            ranking["total_esco_skills"].clip(lower=1)
        )
    )

    ranking["capability"] = capability
    ranking["benchmark_change"] = event["change"]

    ranking = ranking.sort_values(
        "relevance_score",
        ascending=False
    )

    print("\nTOP RELATED OCCUPATIONS")

    print(
        ranking[
            [
                "occupation",
                "matched_skills",
                "essential_matches",
                "relevance_score"
            ]
        ].head(15).to_string(index=False)
    )

    all_job_results.append(ranking)

# =====================================
# STEP 9: SAVE RESULTS
# =====================================

prefix = "demo_" if demo_mode else ""

if all_skill_results:

    skill_results = pd.concat(
        all_skill_results,
        ignore_index=True
    )

    skill_results.to_csv(
        data_folder /
        f"{prefix}impact_skill_candidates.csv",
        index=False
    )

if all_job_results:

    job_results = pd.concat(
        all_job_results,
        ignore_index=True
    )

    job_results.to_csv(
        data_folder /
        f"{prefix}impact_occupation_candidates.csv",
        index=False
    )

print("\n=================================")
print("AI IMPACT MAPPING COMPLETED")
print("=================================")

print("Mode:", "Demo" if demo_mode else "Live")
print("Processed events:", len(events))
print("Results saved in:", data_folder)
