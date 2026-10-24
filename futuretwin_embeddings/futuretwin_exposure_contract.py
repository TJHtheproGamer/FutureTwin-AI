"""Artifact-bound research label contract; never infers lineage from class names."""
from __future__ import annotations

from functools import lru_cache
import hashlib
import json
import math
from pathlib import Path

APPROVED_CHECKPOINT = "66f259fb8947dc06b779334a6cbf7d8e9cad8302260fe94427966bb668cbb5de"
SOURCE_SHA256 = "094378905e1f3349e50a9a83dc69643a2ef227954d611c8316a46da08cb3d8de"
DOCUMENT_HASHES = {
    "final_model/label_provenance.json": "5bf768f123ed4c735f6b75007f25f857c42d1641ce2124a317290a769cb1d451",
    "training_manifest.json": "e7d85cb7522fe1d60fc2e49fb52b85d3096dba90e32ebd0d4d57f53b542e2355",
    "evaluation.json": "0eb178322a31581d93fc37da5ad417c38959dcab6e864d3efe8afffdd7c175c4",
}
PAPER = "https://arxiv.org/abs/2303.10130"
REPOSITORY = "https://github.com/openai/GPTs-are-GPTs"
E3_NOTE = (
    "Preparation policy: drop explicit E3 labels. The selected gpt4_exposure column "
    "contains zero explicit E3 rows, so zero were excluded. This three-class model "
    "does not detect a separate E3/vision category or exclude unseen image tasks. "
    "The paper's separate E3-to-E2 analysis is not an extra transformation applied here."
)


def validate_documents(provenance, manifest, evaluation):
    """Check documented preparation and reported metrics, not reproduce training."""
    p, m, e = provenance, manifest, evaluation
    if not (
        p["source_sha256"] == SOURCE_SHA256
        and p["source_annotation_column"] == "gpt4_exposure"
        and p["source_task_column"] == "Task"
        and p["source_occupation_group_column"] == "O*NET-SOC Code"
        and p["annotation_source"] == "gpt4"
        and p["e3_policy"] == "drop" and p["e3_rows_before_dedup"] == 0
        and p["conflict_policy"] == "drop"
        and p["raw_counts_before_e3_policy"] == {"E0": 8561, "E1": 2702, "E2": 8002}
        and sum(p["prepared_label_counts"].values()) == p["prepared_rows"] == 17940
        and 19265 - p["conflicting_rows_dropped"] - p["duplicate_tasks_removed_after_policy"] == 17940
        and m["dataset_sha256"] == p["data_version_sha256"]
        and m["training_args"]["max_length"] == 160
        and m["model_labels"] == ["E0", "E1", "E2"]
        and sum(s["rows"] for s in e["dataset_split"].values()) == 17940
    ):
        raise ValueError("Unverified or inconsistent training-label preparation.")
    matrix = e["confusion_matrix_e0_e1_e2"]
    if len(matrix) != 3 or any(len(row) != 3 for row in matrix):
        raise ValueError("Expected a three-class confusion matrix.")
    if any(type(n) is not int or n < 0 for row in matrix for n in row):
        raise ValueError("Confusion counts must be nonnegative integers.")
    support = sum(map(sum, matrix))
    if support != 2746 or e["dataset_split"]["test"]["rows"] != support:
        raise ValueError("Held-out support does not match.")
    close = lambda a, b: math.isclose(a, b, abs_tol=1e-10)
    if not close(sum(matrix[i][i] for i in range(3)) / support, e["accuracy"]):
        raise ValueError("Accuracy does not match the reported confusion matrix.")
    for i, label in enumerate(("E0", "E1", "E2")):
        actual, predicted = sum(matrix[i]), sum(row[i] for row in matrix)
        if (e[label]["support"] != actual
                or not close(e[label]["precision"], matrix[i][i] / predicted)
                or not close(e[label]["recall"], matrix[i][i] / actual)
                or not close(e[label]["f1-score"], 2 * matrix[i][i] / (actual + predicted))):
            raise ValueError("Reported per-class metrics are inconsistent.")
    if not close(e["macro avg"]["f1-score"],
                 sum(e[label]["f1-score"] for label in ("E0", "E1", "E2")) / 3):
        raise ValueError("Macro F1 is inconsistent.")


def unverified(reason):
    return {"training_label_contract_verified": False, "status": "training_lineage_unverified",
            "reason": reason, "paper": PAPER, "repository": REPOSITORY}


@lru_cache(maxsize=8)
def _read_contract(parent, signature):
    documents = {}
    for name, expected in DOCUMENT_HASHES.items():
        contents = (Path(parent) / name).read_bytes()
        if hashlib.sha256(contents).hexdigest() != expected:
            raise ValueError("Checkpoint provenance/evaluation document changed.")
        documents[name] = json.loads(contents)
    p = documents["final_model/label_provenance.json"]
    e = documents["evaluation.json"]
    validate_documents(p, documents["training_manifest.json"], e)
    return {
        "training_label_contract_verified": True, "status": "documented_gpt4_annotation_lineage",
        "reason": "Approved v2 package documents gpt4_exposure annotations from the checksum-matched research dataset.",
        "paper": PAPER, "repository": REPOSITORY,
        "source_annotation_column": "gpt4_exposure", "source_sha256": SOURCE_SHA256,
        "prepared_dataset_sha256": p["data_version_sha256"],
        "e3_policy": "drop", "explicit_e3_training_rows_excluded": 0, "e3_note": E3_NOTE,
        "definitions": p["rubric_definitions_if_verified"],
        "verification_scope": (
            "Checkpoint and package-document hashes, known published source checksum, "
            "manifest consistency and confusion-matrix arithmetic checked. Training CSV, "
            "split memberships, conflict audit and training script were not included; "
            "training execution and held-out accuracy were not independently reproduced."
        ),
        "missing_evidence": [],
        "historical_evaluation": {
            "accuracy": e["accuracy"], "macro_f1": e["macro avg"]["f1-score"],
            **{f"{label}_f1": e[label]["f1-score"] for label in ("E0", "E1", "E2")},
            "test_samples": 2746, "independently_verified": False,
            "source": "Uploaded v2 evaluation.json; arithmetic checked against its confusion matrix.",
            "limitation": "Historical research-annotation evaluation, not workplace outcome validation or calibrated confidence.",
        },
    }


def checkpoint_contract(model_dir, checkpoint_fingerprint):
    if checkpoint_fingerprint != APPROVED_CHECKPOINT:
        return unverified("This checkpoint has no approved training-label provenance.")
    try:
        parent = Path(model_dir).parent
        signature = tuple((str(name), (parent / name).stat().st_size,
                           (parent / name).stat().st_mtime_ns) for name in DOCUMENT_HASHES)
        return _read_contract(str(parent), signature)
    except (OSError, ValueError, KeyError, TypeError, ZeroDivisionError):
        return unverified("Approved v2 provenance/evaluation documents are missing, changed or inconsistent.")


def predicted_share(distribution, assessed, *, ready, model, truncated=0):
    """Unweighted argmax class counts; no time weights or employment probability."""
    reason = (
        "Verified training-label provenance is unavailable." if not model.get("label_definitions_verified") else
        "A complete exact-linked source inventory with untruncated predictions is required."
    )
    result = {
        "status": "not_enough_data", "label": "Predicted task-exposure share",
        "percentage": None, "numerator": None, "denominator": assessed or None,
        "formula": "100 * (E1 task count + E2 task count) / assessed task records",
        "weighting": "unweighted_task_records", "reason": reason,
        "e3_note": model.get("label_contract", {}).get("e3_note"),
        "interpretation": "Research-rubric predictions, not current AI capability, automation or job replacement probability.",
    }
    if not ready or truncated or not model.get("label_definitions_verified") or not assessed:
        return result
    counts = [distribution.get(label, {}).get("count") for label in ("E0", "E1", "E2")]
    if any(type(n) is not int or n < 0 for n in counts) or sum(counts) != assessed:
        return {**result, "reason": "Task-class counts are incomplete or inconsistent."}
    numerator = counts[1] + counts[2]
    return {**result, "status": "available", "percentage": round(100 * numerator / assessed, 2),
            "numerator": numerator, "denominator": assessed, "reason": None}
