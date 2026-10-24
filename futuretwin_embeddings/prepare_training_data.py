
import pandas as pd
import numpy as np
from pathlib import Path

# ==========================================
# STEP 1: CONFIGURATION
# ==========================================

SEED = 42

TRAIN_RATIO = 0.80
VAL_RATIO = 0.10
TEST_RATIO = 0.10

BASE_DIR = Path(__file__).resolve().parent

OUTPUT_DIR = BASE_DIR / "data" / "embedding_training"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ==========================================
# STEP 2: LOAD ESCO DATASETS
# ==========================================

print("Loading ESCO datasets...")

occupations = pd.read_csv(
    BASE_DIR / "occupations_en.csv",
    dtype=str,
    low_memory=False
)

skills = pd.read_csv(
    BASE_DIR / "skills_en.csv",
    dtype=str,
    low_memory=False
)

relations = pd.read_csv(
    BASE_DIR / "occupationSkillRelations_en.csv",
    dtype=str,
    low_memory=False
)

print("Total occupations:", len(occupations))
print("Total skills:", len(skills))
print("Total occupation-skill relations:", len(relations))

# ==========================================
# STEP 3: CHECK REQUIRED COLUMNS
# ==========================================

def check_columns(df, required, filename):
    missing = set(required) - set(df.columns)

    if missing:
        raise ValueError(
            f"{filename} missing columns: {missing}"
        )

check_columns(
    occupations,
    ["conceptUri", "preferredLabel"],
    "occupations_en.csv"
)

check_columns(
    skills,
    ["conceptUri", "preferredLabel"],
    "skills_en.csv"
)

check_columns(
    relations,
    ["occupationUri", "skillUri", "relationType"],
    "occupationSkillRelations_en.csv"
)

# Some ESCO versions may have missing descriptions
if "description" not in occupations.columns:
    occupations["description"] = ""

if "description" not in skills.columns:
    skills["description"] = ""

# ==========================================
# STEP 4: CLEAN TEXT
# ==========================================

def clean_text(value):
    if pd.isna(value):
        return ""

    return " ".join(str(value).split())

for df in [occupations, skills]:
    df["preferredLabel"] = (
        df["preferredLabel"].map(clean_text)
    )

    df["description"] = (
        df["description"].map(clean_text)
    )

# ==========================================
# STEP 5: PREPARE OCCUPATIONS
# ==========================================

jobs = occupations[
    ["conceptUri", "preferredLabel", "description"]
].copy()

jobs = jobs.rename(columns={
    "conceptUri": "occupationUri",
    "preferredLabel": "occupation",
    "description": "occupation_description"
})

jobs = jobs.dropna(subset=["occupationUri"])

jobs = jobs[
    jobs["occupation"] != ""
].drop_duplicates(subset=["occupationUri"])

# ==========================================
# STEP 6: PREPARE SKILLS
# ==========================================

skill_data = skills[
    ["conceptUri", "preferredLabel", "description"]
].copy()

skill_data = skill_data.rename(columns={
    "conceptUri": "skillUri",
    "preferredLabel": "skill",
    "description": "skill_description"
})

skill_data = skill_data.dropna(subset=["skillUri"])

skill_data = skill_data[
    skill_data["skill"] != ""
].drop_duplicates(subset=["skillUri"])

# ==========================================
# STEP 7: SELECT ESSENTIAL RELATIONSHIPS
# ==========================================

print("\nFiltering essential skill relationships...")

relations["relationType"] = (
    relations["relationType"]
    .fillna("")
    .str.strip()
    .str.lower()
)

essential_relations = relations[
    relations["relationType"] == "essential"
].copy()

print(
    "Essential relationships:",
    len(essential_relations)
)

# ==========================================
# STEP 8: JOIN OCCUPATIONS AND SKILLS
# ==========================================

print("\nCreating occupation-skill pairs...")

pairs = essential_relations.merge(
    jobs,
    on="occupationUri",
    how="inner"
)

pairs = pairs.merge(
    skill_data,
    on="skillUri",
    how="inner"
)

# Remove duplicate occupation-skill relationships
pairs = pairs.drop_duplicates(
    subset=["occupationUri", "skillUri"]
).copy()

print("Total positive training pairs:", len(pairs))

if pairs.empty:
    raise ValueError(
        "No training pairs generated. "
        "Check ESCO relationship types and URIs."
    )

# ==========================================
# STEP 9: CONSTRUCT TRAINING TEXT
# ==========================================

pairs["job_text"] = (
    "Occupation: "
    + pairs["occupation"]
    + ". "
    + pairs["occupation_description"]
).str.strip()

pairs["skill_text"] = (
    "Skill: "
    + pairs["skill"]
    + ". "
    + pairs["skill_description"]
).str.strip()

# ==========================================
# STEP 10: SPLIT BY OCCUPATION
# ==========================================

print("\nSplitting dataset by occupation...")


occupation_ids = (
    pairs["occupationUri"]
    .dropna()
    .astype(str)
    .unique()
    .tolist()
)

rng = np.random.default_rng(SEED)
rng.shuffle(occupation_ids)

# Verify every occupation occurs exactly once
assert len(occupation_ids) == len(set(occupation_ids))

print("Unique occupation IDs:", len(occupation_ids))
print("Occupation shuffle verified.")


n_occupations = len(occupation_ids)

if n_occupations < 10:
    raise ValueError(
        "Too few occupations for a reliable "
        "train/validation/test split."
    )

train_end = int(
    n_occupations * TRAIN_RATIO
)

val_end = train_end + int(
    n_occupations * VAL_RATIO
)

train_ids = set(
    occupation_ids[:train_end]
)

val_ids = set(
    occupation_ids[train_end:val_end]
)

test_ids = set(
    occupation_ids[val_end:]
)

train_df = pairs[
    pairs["occupationUri"].isin(train_ids)
].copy()

val_df = pairs[
    pairs["occupationUri"].isin(val_ids)
].copy()

test_df = pairs[
    pairs["occupationUri"].isin(test_ids)
].copy()

# ==========================================
# STEP 11: CHECK FOR DATA LEAKAGE
# ==========================================

assert train_ids.isdisjoint(val_ids)
assert train_ids.isdisjoint(test_ids)
assert val_ids.isdisjoint(test_ids)

print("Occupation-level split verified.")

# ==========================================
# STEP 12: SAVE TRAINING DATASETS
# ==========================================

columns = [
    "occupationUri",
    "skillUri",
    "job_text",
    "skill_text"
]

train_df[columns].to_csv(
    OUTPUT_DIR / "train_pairs.csv",
    index=False
)

val_df[columns].to_csv(
    OUTPUT_DIR / "val_pairs.csv",
    index=False
)

test_df[columns].to_csv(
    OUTPUT_DIR / "test_pairs.csv",
    index=False
)

# Save full ESCO skill catalogue
# Needed during skill retrieval evaluation

skill_data[
    ["skillUri", "skill", "skill_description"]
].to_csv(
    OUTPUT_DIR / "skill_catalog.csv",
    index=False
)

# ==========================================
# STEP 13: DISPLAY DATASET STATISTICS
# ==========================================

print("\n====================================")
print("DATASET PREPARATION COMPLETED!")
print("====================================")

print("\nUnique occupations:")
print("Training:", len(train_ids))
print("Validation:", len(val_ids))
print("Testing:", len(test_ids))

print("\nOccupation-skill pairs:")
print("Training pairs:", len(train_df))
print("Validation pairs:", len(val_df))
print("Test pairs:", len(test_df))

print("\nUnique skills:")
print(
    "Training:",
    train_df["skillUri"].nunique()
)
print(
    "Validation:",
    val_df["skillUri"].nunique()
)
print(
    "Testing:",
    test_df["skillUri"].nunique()
)

print("\nEXAMPLE TRAINING PAIRS:")

print(
    train_df[
        ["occupation", "skill"]
    ].head(10).to_string(index=False)
)

print("\nFiles saved to:")
print(OUTPUT_DIR)

print("\nReady for baseline evaluation and RunPod training!")
