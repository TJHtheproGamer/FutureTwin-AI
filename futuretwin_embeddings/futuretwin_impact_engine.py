"""FutureTwin: AI Advancement -> Skill -> Occupation impact engine.

Companion to the existing pipeline files. Reuses, without modification:
  * PostgreSQL ai_benchmark_measurements (written by ai_capability_tracker.py)
  * The fine-tuned MiniLM index via futuretwin_skill_api.load_index()
  * ESCO skills / occupations / occupationSkillRelations CSV files
  * Task-level descriptions from data/tasks.csv

Endpoints are registered in futuretwin_dashboard.py:
  GET /api/advancements          -> snapshot comparison + detected advancements
  GET /api/advancements/impact   -> full impact report for one capability

CLI:
  python futuretwin_embeddings/futuretwin_impact_engine.py --compare
  python futuretwin_embeddings/futuretwin_impact_engine.py --demo Coding
  python futuretwin_embeddings/futuretwin_impact_engine.py --report Coding

HONESTY CONTRACT (keep in sync with the UI):
  * Benchmark changes are OBSERVED measurements.
  * Skill matches are SEMANTIC HYPOTHESES from a fine-tuned MiniLM; cosine
    similarity is NOT an automation probability.
  * Impact classes are UNVALIDATED RULE-BASED HEURISTICS, recorded with their
    rule name so every label can be audited.
  * If snapshots show no comparable improvement, we say so instead of
    manufacturing an advancement.
"""
from __future__ import annotations

import argparse
import os
import re
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

folder = Path(__file__).resolve().parent
data_folder = folder / "data"

# =====================================
# CONFIGURATION
# =====================================

MIN_CHANGE = 0.5          # same threshold as ai_change_detector.py
MIN_SIMILARITY = 0.35     # same floor as ai_impact_pipeline.py
AUTOMATION_SIMILARITY = 0.55  # strong task overlap -> exposure hypothesis
PER_TASK_TOP_K = 8        # skills retrieved per task description
DEFAULT_TOP_K = 15

# Broad fallback text (used only when a capability has no task-level evidence).
CAPABILITY_FALLBACK_TEXT = {
    "Coding": "Write computer programs, generate software code, debug applications and test software.",
    "Agentic AI": "Plan and execute multi-step workflows, coordinate tasks and use digital tools.",
    "Finance": "Analyze financial statements, manage accounting information and financial data.",
    "Legal": "Analyze legal documents, research laws and prepare legal information.",
    "Healthcare": "Analyze medical information, interpret clinical records and support healthcare.",
    "Engineering": "Solve engineering problems, analyze technical systems and evaluate designs.",
    "Economics": "Analyze economic indicators, forecast economic trends and interpret statistics.",
    "Strategy": "Analyze business operations, develop strategies and plan organizational activities.",
}

# Which occupations in data/tasks.csv supply benchmark-supported task
# descriptions for each capability. Deliberately conservative: a capability
# without a defensible task source falls back to capability-level text and is
# flagged as such in every report.
CAPABILITY_TASK_OCCUPATIONS = {
    "Coding": ["Software Developer"],
    "Finance": ["Accountant"],
    "Healthcare": ["Nurse"],
    "Engineering": ["Civil Engineer"],
    "Economics": ["Data Scientist"],
}

# Human-centred work signals: high semantic overlap with an AI task does not
# imply these skills are automatable, so they are classed as augmentation.
HUMAN_CENTRED_RE = re.compile(
    r"\b(advise|advising|counsel|negotiat|teach|teaching|mentor|supervis|"
    r"lead|leadership|collaborat|empath|emotional support|motivat|persuad|"
    r"communicat|care for|caring)\b",
    re.I,
)

# Skills that plausibly GAIN value as AI spreads (oversight, data quality...).
COMPLEMENTARY_RE = re.compile(
    r"\b(artificial intelligence|machine learning|ai system|prompt|"
    r"algorithm|automat|data quality|data annotation|model evaluation)\b",
    re.I,
)


# =====================================
# STEP 1: AI ADVANCEMENT DETECTION (PostgreSQL)
# =====================================

def get_snapshot_comparison() -> dict[str, Any]:
    """Compare the latest two stored benchmark snapshots.

    Mirrors ai_change_detector.py logic: best score per capability, benchmark
    version comparability, and whether the previous leader is still measured.
    Read-only; never writes to the database.
    """
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        return {"status": "error", "error": "DATABASE_URL not found",
                "snapshots": [], "comparisons": [], "advancements": []}

    import psycopg  # local import: engine metadata endpoints must not need a DB

    with psycopg.connect(database_url) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT snapshot_name, MIN(collected_at) AS snapshot_time
                FROM ai_benchmark_measurements
                GROUP BY snapshot_name
                ORDER BY snapshot_time DESC, snapshot_name DESC
            """)
            all_snapshots = cur.fetchall()

            if len(all_snapshots) < 2:
                return {
                    "status": "insufficient_snapshots",
                    "snapshots": [
                        {"snapshot_name": n, "collected_at": str(t)}
                        for n, t in all_snapshots
                    ],
                    "comparisons": [], "advancements": [],
                    "note": "Need at least two stored snapshots to compare.",
                }

            latest_name, latest_time = all_snapshots[0]
            previous_name, previous_time = all_snapshots[1]

            cur.execute("""
                SELECT snapshot_name, model_id, model_name, capability,
                       score, benchmark_version
                FROM ai_benchmark_measurements
                WHERE snapshot_name IN (%s, %s)
            """, (previous_name, latest_name))
            rows = cur.fetchall()

    df = pd.DataFrame(rows, columns=[
        "snapshot_name", "model_id", "model_name",
        "capability", "score", "benchmark_version",
    ])
    df["score"] = pd.to_numeric(df["score"], errors="coerce")
    df = df.dropna(subset=["capability", "score"])

    previous = df[df["snapshot_name"] == previous_name]
    latest = df[df["snapshot_name"] == latest_name]

    comparisons: list[dict[str, Any]] = []
    for capability in sorted(set(previous["capability"]) | set(latest["capability"])):
        old = previous[previous["capability"] == capability]
        new = latest[latest["capability"] == capability]
        if old.empty or new.empty:
            comparisons.append({
                "capability": capability, "previous_best": None,
                "latest_best": None, "change": None, "comparable": False,
                "leading_model": None,
                "note": "Capability missing from one snapshot.",
            })
            continue

        old_best = old.loc[old["score"].idxmax()]
        new_best = new.loc[new["score"].idxmax()]
        old_score, new_score = float(old_best["score"]), float(new_best["score"])

        old_versions = set(old["benchmark_version"].dropna().astype(str))
        new_versions = set(new["benchmark_version"].dropna().astype(str))
        version_comparable = len(old_versions) == 1 and old_versions == new_versions

        old_leader_id = old_best["model_id"]
        leader_present = (
            pd.notna(old_leader_id)
            and old_leader_id in new["model_id"].values
        )
        comparable = bool(version_comparable and leader_present)
        change = round(new_score - old_score, 4) if comparable else None

        note = None
        if not version_comparable:
            note = "Benchmark version changed or inconsistent; scores not comparable."
        elif not leader_present:
            note = "Previous leading model not re-measured; change not comparable."

        comparisons.append({
            "capability": capability,
            "previous_best": old_score,
            "latest_best": new_score,
            "change": change,
            "comparable": comparable,
            "leading_model": str(new_best["model_name"]),
            "benchmark_version": sorted(new_versions) or None,
            "note": note,
        })

    advancements = [
        c for c in comparisons
        if c["comparable"] and c["change"] is not None and c["change"] >= MIN_CHANGE
    ]

    return {
        "status": "ok",
        "snapshots": [
            {"snapshot_name": n, "collected_at": str(t)} for n, t in all_snapshots
        ],
        "previous_snapshot": previous_name,
        "latest_snapshot": latest_name,
        "previous_time": str(previous_time),
        "latest_time": str(latest_time),
        "min_change_threshold": MIN_CHANGE,
        "comparisons": comparisons,
        "advancements": advancements,
        "note": (
            "No meaningful advancement detected between the latest comparable "
            "snapshots." if not advancements else
            f"{len(advancements)} capability improvement(s) detected."
        ),
    }


# =====================================
# STEP 2: CAPABILITY -> TASK DESCRIPTIONS
# =====================================

@lru_cache(maxsize=1)
def _load_tasks() -> pd.DataFrame:
    path = data_folder / "tasks.csv"
    if not path.exists():
        return pd.DataFrame(columns=["task_id", "occupation", "task_text"])
    tasks = pd.read_csv(path)
    return tasks.dropna(subset=["occupation", "task_text"])


def get_capability_tasks(capability: str) -> dict[str, Any]:
    """Specific occupational task descriptions where the benchmark supports
    them; otherwise a flagged capability-level fallback."""
    occupations = CAPABILITY_TASK_OCCUPATIONS.get(capability, [])
    tasks = _load_tasks()
    subset = tasks[tasks["occupation"].isin(occupations)] if occupations else tasks.iloc[0:0]

    if not subset.empty:
        return {
            "task_granularity": "occupation_tasks",
            "task_source_occupations": occupations,
            "tasks": [
                {"task_id": str(r.task_id), "occupation": str(r.occupation),
                 "task_text": str(r.task_text)}
                for r in subset.itertuples(index=False)
            ],
        }
    return {
        "task_granularity": "capability_level_fallback",
        "task_source_occupations": [],
        "tasks": [{
            "task_id": None,
            "occupation": None,
            "task_text": CAPABILITY_FALLBACK_TEXT.get(
                capability, f"Perform occupational tasks related to {capability}."
            ),
        }],
    }


# =====================================
# STEP 3: CAPABILITY -> ESCO SKILL MATCHING (fine-tuned MiniLM)
# =====================================

def match_capability_skills(
    capability: str,
    top_k: int = DEFAULT_TOP_K,
    per_task_k: int = PER_TASK_TOP_K,
    min_similarity: float = MIN_SIMILARITY,
) -> dict[str, Any]:
    """Match each task description against the ESCO catalogue with the
    fine-tuned FutureTwin MiniLM, then merge per skill (best similarity wins).
    """
    from futuretwin_skill_api import match_skills  # reuses cached model+vectors

    task_info = get_capability_tasks(capability)
    merged: dict[str, dict[str, Any]] = {}

    for task in task_info["tasks"]:
        for candidate in match_skills(task["task_text"], top_k=per_task_k):
            uri = candidate["skill_uri"]
            sim = candidate["cosine_similarity"]
            entry = merged.get(uri)
            if entry is None:
                entry = {
                    "skill_uri": uri,
                    "skill": candidate["skill"],
                    "description": candidate["description"],
                    "cosine_similarity": sim,
                    "matched_tasks": [],
                }
                merged[uri] = entry
            entry["cosine_similarity"] = max(entry["cosine_similarity"], sim)
            entry["matched_tasks"].append({
                "task_id": task["task_id"],
                "occupation": task["occupation"],
                "task_text": task["task_text"],
                "cosine_similarity": sim,
            })

    skills = sorted(
        merged.values(), key=lambda s: s["cosine_similarity"], reverse=True
    )
    skills = [s for s in skills if s["cosine_similarity"] >= min_similarity]
    skills = skills[: max(1, min(top_k, 50))]

    for rank, skill in enumerate(skills, 1):
        skill["rank"] = rank
        skill["matched_tasks"].sort(
            key=lambda t: t["cosine_similarity"], reverse=True
        )
        skill["impact"] = classify_impact(skill)

    return {**task_info, "skills": skills, "min_similarity": min_similarity}


def match_task_texts(
    tasks: list[dict[str, Any]],
    per_task_k: int = PER_TASK_TOP_K,
    min_similarity: float = MIN_SIMILARITY,
    top_k: int = 15,
) -> list[dict[str, Any]]:
    """Generic version of capability matching: embed arbitrary preserved task
    descriptions (e.g. from a benchmark) and merge ESCO skill candidates.
    Same honesty rules: cosine similarity is not a probability.
    """
    from futuretwin_skill_api import match_skills

    merged: dict[str, dict[str, Any]] = {}
    for task in tasks:
        for candidate in match_skills(task["task_text"], top_k=per_task_k):
            uri = candidate["skill_uri"]
            entry = merged.setdefault(uri, {
                "skill_uri": uri,
                "skill": candidate["skill"],
                "description": candidate["description"],
                "cosine_similarity": candidate["cosine_similarity"],
                "matched_tasks": [],
            })
            entry["cosine_similarity"] = max(
                entry["cosine_similarity"], candidate["cosine_similarity"])
            entry["matched_tasks"].append({
                "task_text": task["task_text"],
                "task": task.get("task") or "",
                "cosine_similarity": candidate["cosine_similarity"],
            })

    skills = sorted(merged.values(),
                    key=lambda s: s["cosine_similarity"], reverse=True)
    skills = [s for s in skills if s["cosine_similarity"] >= min_similarity]
    skills = skills[: max(1, min(top_k, 50))]
    for rank, skill in enumerate(skills, 1):
        skill["rank"] = rank
        skill["matched_tasks"].sort(
            key=lambda t: t["cosine_similarity"], reverse=True)
        skill["impact"] = classify_impact(skill)
    return skills


# =====================================
# STEP 4: IMPACT CLASSIFICATION (rule-based, unvalidated)
# =====================================

def classify_impact(skill: dict[str, Any]) -> dict[str, Any]:
    """Assign a hypothesis class with the rule that produced it.

    Classes: potential_automation_exposure, ai_augmentation_opportunity,
    complementary_or_emerging, unknown_impact.
    """
    text = f"{skill['skill']}. {skill.get('description') or ''}"
    sim = float(skill["cosine_similarity"])

    if COMPLEMENTARY_RE.search(text):
        return {
            "classification": "complementary_or_emerging",
            "rule": "skill_content_references_ai_or_automation",
            "basis": "Skill text mentions AI, algorithms or automation; such "
                     "skills may become more valuable alongside AI.",
        }
    if HUMAN_CENTRED_RE.search(text):
        return {
            "classification": "ai_augmentation_opportunity",
            "rule": "human_centred_skill_content",
            "basis": "Skill involves advising, teaching, caring or leading; "
                     "AI is more plausibly a support tool than a substitute.",
        }
    if sim >= AUTOMATION_SIMILARITY:
        return {
            "classification": "potential_automation_exposure",
            "rule": "strong_task_overlap",
            "basis": f"Cosine similarity {sim:.4f} >= {AUTOMATION_SIMILARITY} to "
                     "a benchmark-supported AI task. Similarity is not an "
                     "automation probability.",
        }
    if sim >= MIN_SIMILARITY:
        return {
            "classification": "ai_augmentation_opportunity",
            "rule": "moderate_task_overlap",
            "basis": f"Cosine similarity {sim:.4f} is between {MIN_SIMILARITY} "
                     f"and {AUTOMATION_SIMILARITY}; partial task overlap "
                     "suggests assistance rather than replacement.",
        }
    return {
        "classification": "unknown_impact",
        "rule": "weak_or_no_signal",
        "basis": "Semantic signal too weak for a hypothesis.",
    }


# =====================================
# STEP 5: SKILL -> OCCUPATION MAPPING (ESCO relations)
# =====================================

@lru_cache(maxsize=1)
def _load_relations() -> pd.DataFrame:
    relation_files = sorted(folder.glob("occupationSkillRelations*.csv"))
    if not relation_files:
        raise FileNotFoundError("ESCO occupation-skill relationship CSV not found.")
    relations = pd.read_csv(relation_files[0])
    relations = relations.dropna(subset=["occupationUri", "skillUri"])
    return relations.drop_duplicates(["occupationUri", "skillUri"])


def map_skills_to_occupations(
    skills: list[dict[str, Any]], top_n: int = 15
) -> dict[str, Any]:
    """Map matched skills to ESCO occupations via existing relations.

    Distinguishes essential vs optional relations, deduplicates, and keeps the
    full evidence chain occupation -> skill -> task -> capability.
    """
    if not skills:
        return {"occupations": [], "links": []}

    relations = _load_relations()
    matched = pd.DataFrame([
        {
            "skillUri": s["skill_uri"],
            "skill": s["skill"],
            "similarity": float(s["cosine_similarity"]),
            "classification": s["impact"]["classification"],
        }
        for s in skills
    ])

    links = relations.merge(matched, on="skillUri", how="inner")
    links = links.drop_duplicates(["occupationUri", "skillUri"])
    links["essential"] = (
        links["relationType"].fillna("").astype(str).str.lower().eq("essential")
    )
    links["weight"] = np.where(links["essential"], 1.0, 0.5)
    links["weighted_similarity"] = links["similarity"] * links["weight"]

    occupation_sizes = (
        relations.groupby("occupationUri")["skillUri"]
        .nunique().rename("total_esco_skills").reset_index()
    )

    ranking = (
        links.groupby(["occupationUri", "occupationLabel"], as_index=False)
        .agg(
            matched_skills=("skillUri", "nunique"),
            essential_matches=("essential", "sum"),
            average_similarity=("similarity", "mean"),
            weighted_sum=("weighted_similarity", "sum"),
        )
        .merge(occupation_sizes, on="occupationUri", how="left")
    )
    # Same size-bias adjustment as ai_impact_pipeline.py.
    ranking["relevance_score"] = (
        ranking["weighted_sum"]
        / np.sqrt(ranking["total_esco_skills"].clip(lower=1))
    )
    ranking = ranking.sort_values("relevance_score", ascending=False).head(top_n)

    occupations = []
    for rank, row in enumerate(ranking.itertuples(index=False), 1):
        occ_links = links[links["occupationUri"] == row.occupationUri]
        evidence = [
            {
                "skill_uri": l.skillUri,
                "skill": l.skill,
                "relation": "essential" if l.essential else "optional",
                "cosine_similarity": round(float(l.similarity), 4),
                "classification": l.classification,
            }
            for l in occ_links.itertuples(index=False)
        ]
        evidence.sort(key=lambda e: e["cosine_similarity"], reverse=True)
        occupations.append({
            "rank": rank,
            "occupation_uri": str(row.occupationUri),
            "occupation": str(row.occupationLabel),
            "matched_skills": int(row.matched_skills),
            "essential_matches": int(row.essential_matches),
            "optional_matches": int(row.matched_skills - row.essential_matches),
            "average_similarity": round(float(row.average_similarity), 4),
            "relevance_score": round(float(row.relevance_score), 4),
            "total_esco_skills": int(row.total_esco_skills),
            "evidence": evidence,
        })

    link_rows = [
        {
            "occupation_uri": str(l.occupationUri),
            "occupation": str(l.occupationLabel),
            "skill_uri": str(l.skillUri),
            "skill": str(l.skill),
            "relation": "essential" if l.essential else "optional",
        }
        for l in links.itertuples(index=False)
    ]
    return {"occupations": occupations, "links": link_rows}


# =====================================
# STEP 6: FULL IMPACT REPORT
# =====================================

def build_impact_report(
    capability: str,
    demo: bool = False,
    top_k: int = DEFAULT_TOP_K,
) -> dict[str, Any]:
    """Assemble the end-to-end report for one capability.

    demo=True runs a clearly-marked simulated scenario (no advancement claim).
    demo=False only reports impact when a real, comparable improvement was
    detected for the capability; otherwise it says so explicitly.
    """
    if capability not in CAPABILITY_FALLBACK_TEXT:
        raise ValueError(
            f"Unknown capability {capability!r}. "
            f"Choose one of: {', '.join(sorted(CAPABILITY_FALLBACK_TEXT))}."
        )

    comparison = get_snapshot_comparison()
    event = next(
        (a for a in comparison.get("advancements", [])
         if a["capability"] == capability),
        None,
    )

    if demo:
        advancement_status = "simulated_scenario"
        event_out = {
            "capability": capability,
            "change": None,
            "leading_model": "Demo only — no real advancement claimed",
        }
    elif event is not None:
        advancement_status = "detected"
        event_out = event
    else:
        return {
            "capability": capability,
            "mode": "live",
            "advancement_status": "no_meaningful_advancement",
            "event": None,
            "comparison": comparison,
            "skills": [],
            "occupations": [],
            "warnings": [
                "No comparable measured improvement for this capability between "
                "the latest two snapshots, so no skill/occupation impact is "
                "inferred. Use demo mode to preview the pipeline mechanics.",
            ],
        }

    matched = match_capability_skills(capability, top_k=top_k)
    occupation_map = map_skills_to_occupations(matched["skills"])

    return {
        "capability": capability,
        "mode": "demo" if demo else "live",
        "advancement_status": advancement_status,
        "demo_notice": (
            "DEMONSTRATION SCENARIO: matches below are simulated for pipeline "
            "verification. No real AI advancement is being claimed."
            if demo else None
        ),
        "event": event_out,
        "comparison": comparison,
        "task_granularity": matched["task_granularity"],
        "task_source_occupations": matched["task_source_occupations"],
        "capability_tasks": matched["tasks"],
        "skills": matched["skills"],
        "occupations": occupation_map["occupations"],
        "links": occupation_map["links"],
        "method": {
            "detection": (
                "Best measured score per capability compared between the latest "
                "two PostgreSQL snapshots; only comparable benchmark versions "
                "with a re-measured leader count as advancements "
                f"(change >= {MIN_CHANGE})."
            ),
            "skill_matching": (
                "Fine-tuned FutureTwin MiniLM matches benchmark-supported task "
                "descriptions to ESCO skills; per skill the strongest task "
                "match wins. Cosine similarity is not a probability."
            ),
            "occupation_mapping": (
                "Existing ESCO occupationSkillRelations; essential relations "
                "weigh 1.0, optional 0.5; relevance is size-adjusted "
                "(weighted sum / sqrt(total ESCO skills))."
            ),
            "classification": (
                "Rule-based heuristics (unvalidated): every label records the "
                "rule that produced it."
            ),
        },
        "warnings": [
            "Skill matches and impact classes are hypotheses, not observed "
            "employment effects.",
            "Cosine similarity is not an automation probability.",
            "Impact classification rules are unvalidated; audit via the rule "
            "name and basis before drawing conclusions.",
        ],
    }


# =====================================
# CLI
# =====================================

def _print_report(report: dict[str, Any]) -> None:
    print("\n=================================")
    print("CAPABILITY:", report["capability"])
    print("MODE:", report["mode"].upper(),
          "| STATUS:", report["advancement_status"])
    print("=================================")
    if report.get("demo_notice"):
        print(report["demo_notice"])
    if report["advancement_status"] == "no_meaningful_advancement":
        print(report["warnings"][0])
        return

    print("Task granularity:", report["task_granularity"],
          "| tasks:", len(report["capability_tasks"]))
    print("\nTOP SKILLS (fine-tuned MiniLM)")
    for s in report["skills"][:10]:
        print(f"  {s['rank']:>2}. {s['skill'][:52]:<52} "
              f"{s['cosine_similarity']:.4f}  "
              f"[{s['impact']['classification']}]")
    print("\nTOP OCCUPATIONS (ESCO relations)")
    for o in report["occupations"][:10]:
        print(f"  {o['rank']:>2}. {o['occupation'][:44]:<44} "
              f"skills={o['matched_skills']} "
              f"essential={o['essential_matches']} "
              f"score={o['relevance_score']:.3f}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--compare", action="store_true",
                       help="Print the real snapshot comparison only")
    group.add_argument("--demo", choices=sorted(CAPABILITY_FALLBACK_TEXT),
                       help="Simulated scenario (no real advancement claimed)")
    group.add_argument("--report", choices=sorted(CAPABILITY_FALLBACK_TEXT),
                       help="Impact report only if a real advancement exists")
    args = parser.parse_args()

    if args.compare:
        comparison = get_snapshot_comparison()
        print("Snapshots:", len(comparison.get("snapshots", [])))
        for c in comparison.get("comparisons", []):
            print(f"  {c['capability']:<12} prev={c['previous_best']} "
                  f"latest={c['latest_best']} change={c['change']} "
                  f"comparable={c['comparable']}")
        print("Advancements:", len(comparison.get("advancements", [])))
        print(comparison.get("note"))
        return

    _print_report(build_impact_report(args.demo or args.report,
                                      demo=bool(args.demo)))


if __name__ == "__main__":
    main()
