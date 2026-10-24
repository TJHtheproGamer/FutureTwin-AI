"""Precomputed ESCO-to-SDG semantic map snapshots for FutureTwin."""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from typing import Any

import numpy as np

MAP_SNAPSHOT_KEY = "sdg-map-v1"
SDG_COLORS = {
    "1": "#E5243B", "2": "#DDA63A", "3": "#4C9F38", "4": "#C5192D",
    "5": "#FF3A21", "6": "#26BDE2", "7": "#FCC30B", "8": "#A21942",
    "9": "#FD6925", "10": "#DD1367", "11": "#FD9D24", "12": "#BF8B2E",
    "13": "#3F7E44", "14": "#0A97D9", "15": "#56C02B", "16": "#00689D",
    "17": "#19486A",
}


def _unit_vector(value: np.ndarray) -> np.ndarray:
    norm = float(np.linalg.norm(value))
    if not np.isfinite(norm) or norm == 0:
        raise ValueError("An embedding cannot be normalized.")
    return value / norm


def _primary_goal(node: dict[str, Any], candidate_scores: dict[str, dict[str, float]],
                  reviewed_links: list[dict[str, Any]]) -> tuple[str | None, str | None]:
    scores = candidate_scores.get(node["id"], {})
    if scores:
        goal = min(scores, key=lambda code: (-scores[code], int(code)))
        return goal, "unreviewed_candidate"

    strength_order = {"direct": 0, "indirect": 1, "weak": 2}
    direction_order = {"positive": 0, "mixed": 1, "negative": 2}
    linked = [
        row for row in reviewed_links
        if (row["occupation_uri"] == node["uri"] if node["type"] == "occupation"
            else row["skills"][0]["uri"] == node["uri"])
    ]
    if not linked:
        return None, None
    linked.sort(key=lambda row: (
        strength_order.get(row.get("strength"), 9),
        direction_order.get(row.get("direction"), 9),
        str(row.get("target_code", "")),
    ))
    return str(linked[0]["target"]["goal_code"]), "reviewed"


def _map_link(row: dict[str, Any], status: str) -> dict[str, Any]:
    target = row["target"]
    skill = row["skills"][0]
    occupation = row["occupation"]
    return {
        "id": f'{status}:{occupation["uri"]}:{skill["uri"]}:{target["target_code"]}',
        "occupation_uri": occupation["uri"],
        "occupation_label": occupation["label"],
        "skill_uri": skill["uri"],
        "skill_label": skill["label"],
        "skill_relation": skill["relation"],
        "target_code": target["target_code"],
        "goal_code": str(target["goal_code"]),
        "target_title": target["target_title"],
        "target_uri": target["target_uri"],
        "review_status": status,
        "semantic_score": row.get("semantic_score"),
        "strength": row.get("strength"),
        "direction": row.get("direction"),
        "reason": row.get("reason", ""),
        "evidence": row.get("evidence", []),
    }


def _pca_coordinates(
    node_ids: list[str],
    entity_vectors: dict[str, np.ndarray],
    primary_goals: dict[str, str | None],
    goal_vectors: dict[str, np.ndarray],
) -> dict[str, tuple[float, float]]:
    """Project fixed MiniLM vectors to a normalized, deterministic 2D layout."""
    from sklearn.decomposition import PCA

    blended = []
    for node_id in node_ids:
        entity = _unit_vector(np.asarray(entity_vectors[node_id], dtype=np.float64))
        goal = primary_goals.get(node_id)
        if goal and goal in goal_vectors:
            # A small official-goal anchor makes colour-coded goal groups legible
            # without replacing the entity's own semantic embedding.
            entity = _unit_vector(.78 * entity + .22 * _unit_vector(goal_vectors[goal]))
        blended.append(entity)
    matrix = np.vstack(blended)
    if len(node_ids) == 1:
        return {node_ids[0]: (.5, .5)}

    projected = PCA(n_components=2, svd_solver="full").fit_transform(matrix)
    lower = projected.min(axis=0)
    span = projected.max(axis=0) - lower
    safe_span = np.where(span > 1e-12, span, 1.0)
    normalized = .06 + .88 * (projected - lower) / safe_span
    return {
        node_id: (round(float(point[0]), 6), round(float(point[1]), 6))
        for node_id, point in zip(node_ids, normalized)
    }


def build_map_snapshot() -> dict[str, Any]:
    """Build the map offline from existing ESCO data, local MiniLM vectors and UN targets."""
    from futuretwin_career_insurance import skill_descriptions
    from futuretwin_occupation_api import get_esco_occupation_catalog
    from futuretwin_sdg import (
        candidate_records, catalog, public_catalog, reviewed_links, semantic_index,
    )
    from futuretwin_skill_api import load_index

    occupations, _, relations = get_esco_occupation_catalog()
    reviewed = reviewed_links()
    candidates = candidate_records()
    document, _ = catalog()
    summary = public_catalog()
    model, skill_rows, skill_vectors = load_index()
    target_rows, target_vectors, _, skill_indices = semantic_index()

    skill_desc = skill_descriptions()
    skill_info: dict[str, dict[str, str]] = {}
    for occupation_uri, groups in relations.items():
        for relation in ("optional", "essential"):
            for skill in groups.get(relation, []):
                skill_info.setdefault(skill["uri"], {
                    "uri": skill["uri"],
                    "label": skill["label"],
                    "relation": relation,
                    "description": skill_desc.get(skill["uri"], {}).get("description", ""),
                })

    reviewed_keys = {
        (row["occupation_uri"], row["target_code"], row["skills"][0]["uri"])
        for row in reviewed
    }
    candidate_rows = [
        row for row in candidates
        if (row["occupation_uri"], row["target_code"], row["skills"][0]["uri"])
        not in reviewed_keys
    ]
    links = [
        _map_link(row, "unreviewed_candidate") for row in candidate_rows
    ] + [
        _map_link(row, row["review_status"]) for row in reviewed
    ]

    nodes: dict[str, dict[str, Any]] = {}
    candidate_scores: dict[str, dict[str, float]] = {}
    for link in links:
        for entity_type, uri, label in (
            ("occupation", link["occupation_uri"], link["occupation_label"]),
            ("skill", link["skill_uri"], link["skill_label"]),
        ):
            node_id = f"{entity_type}:{uri}"
            node = nodes.setdefault(node_id, {
                "id": node_id,
                "type": entity_type,
                "uri": uri,
                "label": label,
                "goal_codes": set(),
                "review_statuses": set(),
                "connection_count": 0,
            })
            node["goal_codes"].add(link["goal_code"])
            node["review_statuses"].add(link["review_status"])
            node["connection_count"] += 1
            if link["review_status"] == "unreviewed_candidate":
                score = float(link["semantic_score"])
                candidate_scores.setdefault(node_id, {})
                old = candidate_scores[node_id].get(link["goal_code"])
                if old is None or score > old:
                    candidate_scores[node_id][link["goal_code"]] = score

    ordered_ids = sorted(nodes, key=lambda node_id: (
        nodes[node_id]["type"], nodes[node_id]["label"].casefold(), node_id
    ))
    primary_goals: dict[str, str | None] = {}
    primary_basis: dict[str, str | None] = {}
    for node_id in ordered_ids:
        primary_goals[node_id], primary_basis[node_id] = _primary_goal(
            nodes[node_id], candidate_scores, reviewed
        )

    skill_frame_index = {
        str(row.skillUri): i for i, row in skill_rows.iterrows()
    }
    skill_vectors = np.asarray(skill_vectors)
    entity_vectors: dict[str, np.ndarray] = {}
    occupation_ids = [node_id for node_id in ordered_ids
                      if nodes[node_id]["type"] == "occupation"]
    occupation_texts = []
    for node_id in occupation_ids:
        occupation = occupations[nodes[node_id]["uri"]]
        occupation_texts.append(
            f'Occupation: {occupation["label"]}. {occupation.get("description", "")}'.strip()
        )
    if occupation_ids:
        encoded = model.encode(
            occupation_texts, normalize_embeddings=True, convert_to_numpy=True,
            batch_size=32, show_progress_bar=False,
        )
        entity_vectors.update({
            node_id: np.asarray(vector) for node_id, vector in zip(occupation_ids, encoded)
        })

    missing_skill_ids = []
    for node_id in ordered_ids:
        node = nodes[node_id]
        if node["type"] != "skill":
            continue
        uri = node["uri"]
        index = skill_frame_index.get(uri, skill_indices.get(uri))
        if index is None:
            missing_skill_ids.append(node_id)
        else:
            entity_vectors[node_id] = skill_vectors[index]
    if missing_skill_ids:
        missing_texts = [
            "Skill: " + skill_info[nodes[node_id]["uri"]]["label"] + ". " +
            skill_info[nodes[node_id]["uri"]]["description"]
            for node_id in missing_skill_ids
        ]
        encoded = model.encode(
            missing_texts, normalize_embeddings=True, convert_to_numpy=True,
            batch_size=32, show_progress_bar=False,
        )
        entity_vectors.update({
            node_id: np.asarray(vector)
            for node_id, vector in zip(missing_skill_ids, encoded)
        })

    target_by_goal: dict[str, list[np.ndarray]] = {}
    for target, vector in zip(target_rows, target_vectors):
        target_by_goal.setdefault(str(target["goal_code"]), []).append(np.asarray(vector))
    goal_vectors = {
        code: _unit_vector(np.mean(vectors, axis=0))
        for code, vectors in target_by_goal.items()
    }
    positions = _pca_coordinates(
        ordered_ids, entity_vectors, primary_goals, goal_vectors
    )

    goal_node_counts = {str(code): 0 for code in range(1, 18)}
    final_nodes = []
    for node_id in ordered_ids:
        node = nodes[node_id]
        goal_codes = sorted(node["goal_codes"], key=int)
        for code in goal_codes:
            goal_node_counts[code] += 1
        x, y = positions[node_id]
        final_nodes.append({
            "id": node_id,
            "type": node["type"],
            "uri": node["uri"],
            "label": node["label"],
            "x": x,
            "y": y,
            "primary_goal_code": primary_goals[node_id],
            "primary_goal_basis": primary_basis[node_id],
            "goal_codes": goal_codes,
            "review_statuses": sorted(node["review_statuses"]),
            "connection_count": node["connection_count"],
        })

    targets_by_goal = {str(code): 0 for code in range(1, 18)}
    for target in document["targets"]:
        targets_by_goal[str(target["goal_code"])] += 1
    goals = [
        {
            "code": str(goal["code"]),
            "title": goal["title"],
            "color": SDG_COLORS[str(goal["code"])],
            "target_count": targets_by_goal[str(goal["code"])],
            "node_count": goal_node_counts[str(goal["code"])],
        }
        for goal in document["goals"]
    ]
    reviewed_goal_codes = sorted({
        str(row["target"]["goal_code"]) for row in reviewed
    }, key=int)
    candidate_goal_codes = sorted({
        row["goal_code"] for row in links
        if row["review_status"] == "unreviewed_candidate"
    }, key=int)
    total_occupations = len(occupations)
    reviewed_occupations = {row["occupation_uri"] for row in reviewed}
    candidate_occupations = {row["occupation_uri"] for row in candidate_rows}
    candidate_skills = {row["skills"][0]["uri"] for row in candidate_rows}
    assistant_reviewed = sum(
        row["review_status"] == "assistant_desk_reviewed" for row in reviewed
    )
    human_approved = sum(
        row["review_status"] == "independently_human_approved" for row in reviewed
    )
    content_fingerprint = hashlib.sha256(json.dumps(
        {"nodes": final_nodes, "links": links},
        ensure_ascii=False, sort_keys=True, separators=(",", ":"),
    ).encode("utf-8")).hexdigest()[:12]

    return {
        "schema_version": 1,
        "snapshot_id": f"{MAP_SNAPSHOT_KEY}-{content_fingerprint}",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "projection": {
            "method": "PCA",
            "model": "FutureTwin fine-tuned MiniLM (local)",
            "stable": True,
            "note": (
                "Two-dimensional PCA of normalized local MiniLM vectors, blended "
                "with official SDG target anchors. Coordinates are precomputed and "
                "stored; colors mark the strongest available association, not impact."
            ),
        },
        "coverage": {
            "candidate_link_count": len(candidate_rows),
            "candidate_occupation_count": len(candidate_occupations),
            "candidate_skill_count": len(candidate_skills),
            "candidate_goal_count": len(candidate_goal_codes),
            "candidate_goal_codes": candidate_goal_codes,
            "reviewed_link_count": len(reviewed),
            "assistant_desk_reviewed_count": assistant_reviewed,
            "independently_human_approved_count": human_approved,
            "reviewed_goal_count": len(reviewed_goal_codes),
            "reviewed_goal_codes": reviewed_goal_codes,
            "total_goal_count": len(document["goals"]),
            "total_esco_occupation_count": total_occupations,
            "occupations_without_reviewed_evidence": (
                total_occupations - len(reviewed_occupations)
            ),
            "node_count": len(final_nodes),
            "occupation_node_count": sum(n["type"] == "occupation" for n in final_nodes),
            "skill_node_count": sum(n["type"] == "skill" for n in final_nodes),
            "connection_count": len(links),
        },
        "goals": goals,
        "nodes": final_nodes,
        "links": links,
    }


def save_map_snapshot(payload: dict[str, Any]) -> None:
    """Upsert the precomputed snapshot; schema is managed by the SQL migration."""
    from futuretwin_resume_api import _database_connection

    generated_at = datetime.fromisoformat(
        payload["generated_at"].replace("Z", "+00:00")
    ).astimezone(timezone.utc)
    with _database_connection() as conn:
        conn.execute(
            """
            INSERT INTO futuretwin_sdg_map_snapshots
                (snapshot_key, payload, generated_at)
            VALUES (%s, %s::jsonb, %s)
            ON CONFLICT (snapshot_key) DO UPDATE SET
                payload = EXCLUDED.payload,
                generated_at = EXCLUDED.generated_at
            """,
            (
                MAP_SNAPSHOT_KEY,
                json.dumps(payload, ensure_ascii=False, allow_nan=False),
                generated_at,
            ),
        )
        conn.commit()


def read_map_snapshot() -> dict[str, Any] | None:
    from futuretwin_resume_api import _database_connection

    with _database_connection() as conn:
        row = conn.execute(
            "SELECT payload FROM futuretwin_sdg_map_snapshots WHERE snapshot_key = %s",
            (MAP_SNAPSHOT_KEY,),
        ).fetchone()
    if not row:
        return None
    value = row[0]
    return json.loads(value) if isinstance(value, str) else value


def map_entity_detail(entity_type: str, uri: str) -> dict[str, Any] | None:
    """Return exact ESCO relations and stored connections for one map entity."""
    snapshot = read_map_snapshot()
    if not snapshot:
        return None
    node = next((
        item for item in snapshot["nodes"]
        if item["type"] == entity_type and item["uri"] == uri
    ), None)
    if not node:
        return None

    from futuretwin_career_insurance import skill_descriptions
    from futuretwin_occupation_api import get_esco_occupation_catalog

    occupations, _, relations = get_esco_occupation_catalog()
    descriptions = skill_descriptions()
    if entity_type == "occupation":
        occupation = occupations.get(uri)
        if not occupation:
            return None
        skills = []
        for relation in ("essential", "optional"):
            for skill in relations.get(uri, {}).get(relation, []):
                skills.append({
                    "uri": skill["uri"],
                    "label": skill["label"],
                    "relation": relation,
                    "description": descriptions.get(skill["uri"], {}).get("description", ""),
                })
        skills.sort(key=lambda item: (
            item["relation"] != "essential", item["label"].casefold(), item["uri"]
        ))
        entity = {
            "type": entity_type,
            "uri": uri,
            "label": occupation["label"],
            "description": occupation.get("description", ""),
        }
        related_occupations = []
    elif entity_type == "skill":
        skill = next((
            row for groups in relations.values()
            for relation in ("essential", "optional")
            for row in groups.get(relation, [])
            if row["uri"] == uri
        ), None)
        if not skill:
            return None
        skill_description = descriptions.get(uri, {}).get("description", "")
        entity = {
            "type": entity_type,
            "uri": uri,
            "label": skill["label"],
            "description": skill_description,
        }
        skills = []
        related_occupations = []
        for occupation_uri, groups in relations.items():
            relation = next((
                kind for kind in ("essential", "optional")
                if any(row["uri"] == uri for row in groups.get(kind, []))
            ), None)
            if relation and occupation_uri in occupations:
                related_occupations.append({
                    "uri": occupation_uri,
                    "label": occupations[occupation_uri]["label"],
                    "relation": relation,
                })
        related_occupations.sort(key=lambda item: (item["label"].casefold(), item["uri"]))
        related_occupation_count = len(related_occupations)
        related_occupations = related_occupations[:40]
    else:
        return None

    connections = []
    for link in snapshot["links"]:
        if ((entity_type == "occupation" and link["occupation_uri"] == uri)
                or (entity_type == "skill" and link["skill_uri"] == uri)):
            connections.append({
                "target_code": link["target_code"],
                "goal_code": link["goal_code"],
                "target_title": link["target_title"],
                "target_uri": link["target_uri"],
                "skill": {
                    "uri": link["skill_uri"],
                    "label": link["skill_label"],
                    "relation": link["skill_relation"],
                },
                "review_status": link["review_status"],
                "semantic_score": link["semantic_score"],
                "strength": link["strength"],
                "direction": link["direction"],
                "reason": link["reason"],
                "evidence": link["evidence"],
            })
    connections.sort(key=lambda item: (
        {"independently_human_approved": 0, "assistant_desk_reviewed": 1,
         "unreviewed_candidate": 2}.get(item["review_status"], 3),
        int(item["goal_code"]), item["target_code"],
        -(item["semantic_score"] or 0),
    ))
    return {
        "entity": entity,
        "skills": skills,
        "occupations": related_occupations,
        "occupation_count": (
            related_occupation_count if entity_type == "skill"
            else len(related_occupations)
        ),
        "connections": connections,
        "notice": (
            "Unreviewed MiniLM links are retrieval suggestions only. Reviewed links "
            "retain their review status; none of these associations measures impact."
        ),
    }
