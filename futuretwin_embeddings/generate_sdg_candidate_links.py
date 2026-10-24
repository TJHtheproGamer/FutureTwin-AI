"""Build a local, review-only SDG candidate queue from existing ESCO data.

Uses the existing fine-tuned MiniLM checkpoint and cached ESCO skill vectors.
It does not call a network API, train a model, or edit reviewed associations.
Similarity is retrieval ordering only; it is not evidence of contribution.
"""
from __future__ import annotations

import json
import csv
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from futuretwin_occupation_api import get_esco_occupation_catalog
from futuretwin_skill_api import load_index


BASE = Path(__file__).resolve().parent
DATA = BASE / "data"
OUTPUT = DATA / "sdg_candidate_links.json"
OCCUPATION_TARGET = 100
SKILL_TARGET = 200
SKILLS_PER_OCCUPATION_GOAL = 4
SKILL_WEIGHT = 0.7
OCCUPATION_WEIGHT = 0.3

def _encode_text(model, texts: list[str], batch_size: int) -> np.ndarray:
    return model.encode(
        texts,
        batch_size=batch_size,
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=False,
    )


def _nace_metadata() -> dict[str, dict]:
    """Read the free NACE 2.1 occupation tags already shipped with ESCO."""
    result = {}
    with (BASE / "occupations_en.csv").open(encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            codes = [
                value.strip()
                for value in re.split(r"[,\r\n]+", row.get("naceCode") or "")
                if value.strip()
            ]
            divisions = []
            for uri in codes:
                match = re.search(r"/([0-9]+)$", uri)
                if not match or len(match.group(1)) < 2:
                    continue
                division = match.group(1)[:2]
                if division not in divisions:
                    divisions.append(division)
            result[row["conceptUri"]] = {
                "nace_codes": codes,
                "nace_divisions": divisions,
                # The first listed code is only a deterministic diversity bucket;
                # all source-assigned codes remain attached to the candidate.
                "nace_division_anchor": divisions[0] if divisions else "",
            }
    return result


def _retrieval_rows():
    model, skill_catalog, skill_vectors = load_index()
    occupations, _, relations = get_esco_occupation_catalog()
    nace = _nace_metadata()
    target_doc = json.loads((DATA / "sdg_targets_un_v5.json").read_text(encoding="utf-8"))
    targets = target_doc["targets"]
    target_texts = [
        f"SDG {target['goal_code']}, target {target['target_code']}: "
        f"{target['target_title']}"
        + (f". {target['target_description']}"
           if target.get("target_description")
           and target["target_description"] != target["target_title"] else "")
        for target in targets
    ]
    target_vectors = _encode_text(model, target_texts, 32)

    occupation_rows = sorted(occupations.items(), key=lambda item: item[0])
    occupation_texts = [
        f"Occupation: {occupation['label']}. {occupation.get('description', '')}"
        for _, occupation in occupation_rows
    ]
    occupation_vectors = _encode_text(model, occupation_texts, 64)
    occupation_similarities = target_vectors @ occupation_vectors.T

    skill_index = {
        str(uri): i for i, uri in enumerate(skill_catalog["skillUri"].astype(str))
    }
    skill_details = {}
    for i, row in skill_catalog.iterrows():
        uri = str(row["skillUri"])
        skill_details[uri] = {
            "label": str(row["skill"]),
            "description": str(row.get("skill_description", "") or ""),
            "vector_index": i,
        }

    goal_target_indices: dict[str, list[int]] = defaultdict(list)
    for i, target in enumerate(targets):
        goal_target_indices[str(target["goal_code"])].append(i)

    rows = []
    for occupation_index, (occupation_uri, occupation) in enumerate(occupation_rows):
        linked = {}
        for relation in ("essential", "optional"):
            for skill in relations.get(occupation_uri, {}).get(relation, []):
                skill_uri = skill["uri"]
                detail = skill_details.get(skill_uri)
                if not detail:
                    continue
                # Keep the strongest exact ESCO relation if a skill appears twice.
                if skill_uri not in linked or relation == "essential":
                    linked[skill_uri] = {
                        **detail,
                        "relation": relation,
                    }
        if not linked:
            continue
        industry = nace.get(occupation_uri, {})

        skill_uris = list(linked)
        vector_indices = np.asarray(
            [linked[uri]["vector_index"] for uri in skill_uris], dtype=np.int64
        )
        for goal_code, target_indices in goal_target_indices.items():
            target_index_array = np.asarray(target_indices, dtype=np.int64)
            skill_similarities = target_vectors[target_index_array] @ skill_vectors[vector_indices].T
            combined = (
                SKILL_WEIGHT * skill_similarities
                + OCCUPATION_WEIGHT
                * occupation_similarities[target_index_array, occupation_index][:, None]
            )
            flat_order = np.argsort(combined, axis=None)[::-1]
            selected_skills = set()
            selected_count = 0
            for flat_index in flat_order:
                target_row, skill_row = np.unravel_index(flat_index, combined.shape)
                skill_uri = skill_uris[int(skill_row)]
                if skill_uri in selected_skills:
                    continue
                selected_skills.add(skill_uri)
                target_index = int(target_index_array[int(target_row)])
                skill = linked[skill_uri]
                rows.append({
                    "goal_code": goal_code,
                    "target": targets[target_index],
                    "occupation": occupation,
                    "occupation_uri": occupation_uri,
                    "isco_major_group": (occupation.get("isco_group") or "")[:1],
                    **industry,
                    "skill_uri": skill_uri,
                    "skill": skill,
                    "semantic_score": float(combined[target_row, skill_row]),
                    "skill_similarity": float(skill_similarities[target_row, skill_row]),
                    "occupation_similarity": float(
                        occupation_similarities[target_index, occupation_index]
                    ),
                })
                selected_count += 1
                if selected_count >= SKILLS_PER_OCCUPATION_GOAL:
                    break
    return target_doc, rows


def _select_review_queue(rows):
    by_goal: dict[str, list[dict]] = defaultdict(list)
    by_occupation: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        by_goal[row["goal_code"]].append(row)
        by_occupation[row["occupation_uri"]].append(row)
    for values in by_goal.values():
        values.sort(key=lambda row: (-row["semantic_score"], row["occupation_uri"], row["skill_uri"]))
    for values in by_occupation.values():
        values.sort(key=lambda row: (-row["semantic_score"], row["goal_code"], row["skill_uri"]))

    goal_codes = [str(i) for i in range(1, 18)]
    # A balanced review queue across the 17 goals: 6 suggestions for 15 goals,
    # 5 for the remaining two. These are candidates, not verified connections.
    goal_quotas = {goal: 6 if int(goal) <= 15 else 5 for goal in goal_codes}
    selected = []
    occupations_used = set()
    skills_used = set()
    goal_counts = Counter()
    group_counts = Counter()
    industry_counts = Counter()
    group_target = max(1, OCCUPATION_TARGET // 10)
    max_per_group = max(1, (OCCUPATION_TARGET + 4) // 5)
    max_per_industry = 12

    def pick(options, *, apply_group_cap=True):
        if not options:
            return None
        if apply_group_cap:
            diverse_options = [
                row for row in options
                if group_counts[row["isco_major_group"] or "unknown"] < max_per_group
                and industry_counts[row.get("nace_division_anchor") or "unknown"] < max_per_industry
            ]
            if diverse_options:
                options = diverse_options

        def utility(row):
            group = row["isco_major_group"] or "unknown"
            diversity = 0.06 * max(0, group_target - group_counts[group]) / group_target
            industry = row.get("nace_division_anchor") or "unknown"
            industry_diversity = 0.06 * max(0, 4 - industry_counts[industry]) / 4
            return row["semantic_score"] + diversity + industry_diversity

        return max(
            options,
            key=lambda row: (
                utility(row),
                row["semantic_score"],
                row["occupation_uri"],
                row["skill_uri"],
            ),
        )

    # Round-robin selection gives every goal a first pass before any gets a
    # second, while each primary suggestion uses a distinct career and skill.
    for slot in range(max(goal_quotas.values())):
        for goal in goal_codes:
            if goal_counts[goal] >= goal_quotas[goal]:
                continue
            options = [
                row for row in by_goal.get(goal, [])
                if row["occupation_uri"] not in occupations_used
                and row["skill_uri"] not in skills_used
            ]
            row = pick(options)
            if row is None:
                continue
            selected.append(row)
            occupations_used.add(row["occupation_uri"])
            skills_used.add(row["skill_uri"])
            goal_counts[goal] += 1
            group_counts[row["isco_major_group"] or "unknown"] += 1
            industry_counts[row.get("nace_division_anchor") or "unknown"] += 1

    # Fill any remaining occupation slots from the strongest unused rows,
    # retaining distinct skills and broad occupation-group diversity.
    while len(occupations_used) < OCCUPATION_TARGET:
        options = [
            row for row in rows
            if row["occupation_uri"] not in occupations_used
            and row["skill_uri"] not in skills_used
        ]
        row = pick(options)
        if row is None:
            break
        selected.append(row)
        occupations_used.add(row["occupation_uri"])
        skills_used.add(row["skill_uri"])
        goal_counts[row["goal_code"]] += 1
        group_counts[row["isco_major_group"] or "unknown"] += 1
        industry_counts[row.get("nace_division_anchor") or "unknown"] += 1

    # Add a second, distinct skill suggestion for each selected career. If a
    # skill is shared by many careers, it is assigned only once in this starter
    # queue so that the report counts 200 distinct ESCO skills.
    selected_by_occupation = defaultdict(list)
    for row in selected:
        selected_by_occupation[row["occupation_uri"]].append(row)
    secondary_order = sorted(
        occupations_used,
        key=lambda uri: (
            len({r["skill_uri"] for r in by_occupation[uri]}),
            -max(r["semantic_score"] for r in by_occupation[uri]),
            uri,
        ),
    )
    for occupation_uri in secondary_order:
        if len(selected_by_occupation[occupation_uri]) >= 2:
            continue
        options = [
            row for row in by_occupation[occupation_uri]
            if row["skill_uri"] not in skills_used
            and row not in selected_by_occupation[occupation_uri]
        ]
        row = pick(options, apply_group_cap=False)
        if row is None:
            continue
        selected.append(row)
        selected_by_occupation[occupation_uri].append(row)
        skills_used.add(row["skill_uri"])

    # If a small number of careers had no second unique skill, allow a third
    # suggestion on another selected career rather than silently missing the
    # explicit skill target. The skill remains unique across the queue.
    while len(skills_used) < SKILL_TARGET:
        options = [
            row for uri in occupations_used
            if len(selected_by_occupation[uri]) < 3
            for row in by_occupation[uri]
            if row["skill_uri"] not in skills_used
            and row not in selected_by_occupation[uri]
        ]
        row = pick(options, apply_group_cap=False)
        if row is None:
            break
        selected.append(row)
        selected_by_occupation[row["occupation_uri"]].append(row)
        skills_used.add(row["skill_uri"])

    selected = sorted(
        selected,
        key=lambda row: (
            int(row["goal_code"]),
            -row["semantic_score"],
            row["occupation"]["label"].casefold(),
            row["skill"]["label"].casefold(),
        ),
    )
    return selected, goal_counts, group_counts, industry_counts


def _serialize_candidate(row):
    target = row["target"]
    occupation = row["occupation"]
    skill = row["skill"]
    goal_code = str(target["goal_code"])
    occupation_label = occupation["label"]
    skill_label = skill["label"]
    target_code = target["target_code"]
    reason = (
        "Local MiniLM ranked this exact ESCO occupation–skill link near the UN target wording; "
        "it is a review lead, not evidence of contribution or direction."
    )
    return {
        "id": f'candidate:{row["occupation_uri"]}:{target_code}:{row["skill_uri"]}',
        "occupation_uri": row["occupation_uri"],
        "occupation_label": occupation_label,
        "isco_major_group": row["isco_major_group"],
        "nace_codes": row.get("nace_codes", []),
        "nace_divisions": row.get("nace_divisions", []),
        "nace_division_anchor": row.get("nace_division_anchor", ""),
        "skill_uri": row["skill_uri"],
        "skill_label": skill_label,
        "skill_description": skill["description"],
        "skill_relation": skill["relation"],
        "target_code": target_code,
        "goal_code": goal_code,
        "goal_title": target["goal_title"],
        "target_title": target["target_title"],
        "target_description": target.get("target_description", ""),
        "target_uri": target.get("target_uri", ""),
        "review_status": "unreviewed_candidate",
        "relationship_status": "not_assessed",
        "strength": None,
        "direction": None,
        "semantic_score": round(row["semantic_score"], 4),
        "skill_similarity": round(row["skill_similarity"], 4),
        "occupation_similarity": round(row["occupation_similarity"], 4),
        "reason": reason,
        "evidence": [
            {
                "label": "ESCO occupation description",
                "url": row["occupation_uri"],
                "quote": occupation.get("description") or occupation_label,
            },
            {
                "label": f'ESCO {skill["relation"]} skill relation',
                "url": row["skill_uri"],
                "quote": f"{skill_label} — {skill['relation']} skill for {occupation_label}. "
                         f"{skill['description']}".strip(),
            },
            {
                "label": f"Official UN SDG target {target_code}",
                "url": target.get("target_uri")
                      or f"https://sdgs.un.org/goals/goal{goal_code}#targets_and_indicators",
                "quote": target["target_title"],
            },
        ],
    }


def generate() -> dict:
    target_doc, rows = _retrieval_rows()
    selected, goal_counts, group_counts, industry_counts = _select_review_queue(rows)
    candidates = [_serialize_candidate(row) for row in selected]
    occupation_count = len({row["occupation_uri"] for row in candidates})
    skill_count = len({row["skill_uri"] for row in candidates})
    goal_coverage = sorted({row["goal_code"] for row in candidates}, key=int)
    result = {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": {
            "esco_occupations": "occupations_en.csv",
            "esco_skills": "data/embedding_training/skill_catalog.csv",
            "esco_occupation_skill_relations": "occupationSkillRelations_en.csv",
            "un_targets": target_doc["source_url"],
            "un_release": target_doc.get("release"),
        },
        "method": {
            "model": "Existing fine-tuned FutureTwin MiniLM, local CPU inference",
            "model_changed": False,
            "paid_api_used": False,
            "candidate_limit": {
                "occupations": OCCUPATION_TARGET,
                "unique_skills": SKILL_TARGET,
                "skills_per_occupation_goal_before_selection": SKILLS_PER_OCCUPATION_GOAL,
            },
            "ranking": (
                f"{SKILL_WEIGHT:.2f} × target-to-ESCO-skill cosine similarity + "
                f"{OCCUPATION_WEIGHT:.2f} × target-to-ESCO-occupation cosine similarity"
            ),
            "interpretation": (
                "Similarity is used only to order an unreviewed evidence-review queue. "
                "It is not a probability, relationship classification, contribution claim, "
                "or input to Purpose Alignment."
            ),
            "review_status": "unreviewed_candidate",
        },
        "summary": {
            "candidate_link_count": len(candidates),
            "candidate_occupation_count": occupation_count,
            "candidate_skill_count": skill_count,
            "candidate_goal_count": len(goal_coverage),
            "candidate_goals": goal_coverage,
            "primary_suggestions_by_goal": dict(sorted(goal_counts.items(), key=lambda item: int(item[0]))),
            "occupations_by_isco_major_group": dict(sorted(group_counts.items())),
            "candidate_nace_division_count": len(industry_counts),
            "occupations_by_nace_division_anchor": dict(sorted(industry_counts.items())),
        },
        "links": candidates,
    }
    if occupation_count != OCCUPATION_TARGET or skill_count != SKILL_TARGET or len(goal_coverage) != 17:
        raise RuntimeError(
            "Candidate queue did not meet its review-queue targets: "
            f"{occupation_count} occupations, {skill_count} skills, "
            f"{len(goal_coverage)} SDGs."
        )
    return result


def main() -> None:
    document = generate()
    OUTPUT.write_text(
        json.dumps(document, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(document["summary"], ensure_ascii=False, indent=2))
    print(f"Wrote unreviewed candidate queue to {OUTPUT}")


if __name__ == "__main__":
    main()
