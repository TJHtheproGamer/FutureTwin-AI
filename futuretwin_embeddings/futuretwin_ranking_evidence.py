"""Read-only ranking evidence: paper definitions are not checkpoint provenance."""
from __future__ import annotations

import csv
from datetime import date
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import sqlite3

DATA = Path(__file__).resolve().parent / "data"


def label_audit():
    from futuretwin_distilbert import CLASSIFIER, ModelUnavailable
    try:
        contract = CLASSIFIER.metadata().get("label_contract", {})
        if contract.get("training_label_contract_verified"):
            return contract
    except (ModelUnavailable, OSError, ValueError):
        contract = {}
    try:
        reference = json.loads((DATA / "distilbert_label_provenance.json").read_text())
        paper = reference["research_reference"]
        paper_url, repo_url, e3_note = paper["paper"], paper["repository"], paper["e3_note"]
        missing = reference["missing_evidence"]
    except (OSError, ValueError, KeyError, TypeError):
        return {
            "training_label_contract_verified": False, "status": "audit_unavailable",
            "reason": "Original training-label lineage has not been verified; audit file unavailable.",
        }
    # Reference-paper verification is deliberately not a training-label contract.
    return {
        "training_label_contract_verified": False,
        "status": "training_lineage_unverified",
        "reason": contract.get("reason") or "Paper rubric verified; checkpoint training dataset and label transformation are missing.",
        "paper": paper_url,
        "repository": repo_url,
        "e3_note": e3_note,
        "missing_evidence": missing,
    }


def load_vacancy_rows(data_dir=DATA):
    """Fail closed on source/data mismatch; do not guess codes, geography or units."""
    data_dir = Path(data_dir)
    metadata = json.loads((data_dir / "dosm_jmi_group_vacancies.meta.json").read_text())
    contents = (data_dir / "dosm_jmi_group_vacancies.csv").read_bytes()
    if hashlib.sha256(contents).hexdigest() != metadata["csv_sha256"]:
        raise ValueError("DOSM history does not match its verified import.")
    rows = list(csv.DictReader(contents.decode("utf-8").splitlines()))
    seen = set()
    for row in rows:
        key = (row["source_group_id"], row["period"])
        if (key in seen or row["scope"] != "major_group" or row["occupation_code"]
                or row["classification_version"] or row["geography"] != "Malaysia"
                or row["classification_system"] != metadata["classification_system"]
                or row["measure"] != "online_advertised_job_offerings"
                or row["source_sha256"] != metadata["source_sha256"]
                or row["source_url"] != metadata["url"]
                or not row["vacancies"].isdigit()
                or row["validation"] != "quarter_equals_sum_of_three_months"
                or not metadata["period_start"] <= row["period"] <= metadata["period_end"]):
            raise ValueError("Invalid or incompatible DOSM historical observation.")
        if date.fromisoformat(row["period_start"]) >= date.fromisoformat(row["period_end_exclusive"]):
            raise ValueError("Observation period must have a positive duration.")
        row["vacancies"] = int(row["vacancies"])
        seen.add(key)
    if (len(rows) != metadata["observation_count"]
            or len({r["source_group_id"] for r in rows}) != metadata["group_count"]):
        raise ValueError("DOSM historical coverage does not match its manifest.")
    return rows, metadata


@lru_cache(maxsize=4)
def _vacancy_history(signature):
    rows, metadata = load_vacancy_rows()
    return {
        "status": "historical_group_data_only",
        "source": metadata["publisher"], "source_url": metadata["url"],
        "download_url": metadata["download_url"], "attribution": metadata["attribution"],
        "terms_url": metadata["terms_url"], "retrieved_at": metadata["retrieved_at"],
        "source_sha256": metadata["source_sha256"],
        "observation_count": len(rows), "group_count": metadata["group_count"],
        "period_start": metadata["period_start"], "period_end": metadata["period_end"],
        "geography": metadata["geography"], "scope": "major_group",
        "classification_system": metadata["classification_system"],
        "classification_version": None, "exact_esco_mappings": 0,
        "eligible_occupation_count": 0,
        "reason": "DOSM history is at broad group level; no verified exact MASCO–ESCO vacancy series.",
        "limitations": metadata["limitations"],
        "latest_observations": [
            {"source_group_id": r["source_group_id"], "label": r["occupation_label"],
             "period": r["period"], "vacancies": r["vacancies"], "source_cell": r["source_cell"]}
            for r in rows if r["period"] == metadata["period_end"]
        ],
    }


def vacancy_history():
    try:
        signature = tuple((DATA / name).stat().st_mtime_ns for name in (
            "dosm_jmi_group_vacancies.csv", "dosm_jmi_group_vacancies.meta.json"))
        return _vacancy_history(signature)
    except (OSError, ValueError, KeyError, TypeError):
        return {"status": "unavailable", "eligible_occupation_count": 0,
                "reason": "Verified historical vacancy data could not be read."}


@lru_cache(maxsize=4)
def _inventory(signature, method, verified=False):
    from futuretwin_onet_exposure_db import DATABASE, connect
    from futuretwin_occupation_api import get_esco_occupation_catalog
    occupations, _, _ = get_esco_occupation_catalog()
    with connect(DATABASE, read_only=True) as db:
        metadata = dict(db.execute("SELECT key,value FROM source_metadata"))
        if metadata.get("active_model_fingerprint") != method:
            raise ValueError("Task predictions use a different inference method.")
        db.create_function("task_hash", 1, lambda text: hashlib.sha256(text.encode()).hexdigest()
                           if isinstance(text, str) else None)
        counts = {
            r["target_uri"]: dict(r) for r in db.execute("""
                SELECT m.target_uri, COUNT(t.task_id) AS task_count,
                       COUNT(DISTINCT m.onet_soc_code) AS exact_source_count,
                       COUNT(DISTINCT t.onet_soc_code) AS available_source_count,
                       SUM(CASE WHEN p.label IS NOT NULL THEN 1 ELSE 0 END) AS classified_count,
                       SUM(CASE WHEN p.label='E0' THEN 1 ELSE 0 END) AS e0_count,
                       SUM(CASE WHEN p.label='E1' THEN 1 ELSE 0 END) AS e1_count,
                       SUM(CASE WHEN p.label='E2' THEN 1 ELSE 0 END) AS e2_count,
                       SUM(CASE WHEN p.label IS NOT NULL THEN p.truncated ELSE 0 END) AS truncated_count
                FROM occupation_mappings m
                LEFT JOIN onet_tasks t ON t.onet_soc_code=m.onet_soc_code
                LEFT JOIN task_predictions p ON p.onet_soc_code=t.onet_soc_code
                    AND p.task_id=t.task_id AND p.model_fingerprint=?
                    AND p.text_sha256=task_hash(t.task_text)
                WHERE m.target_system='ESCO' AND m.relationship='exactMatch'
                GROUP BY m.target_uri
            """, (method,))
        }
        mapped = {r[0] for r in db.execute(
            "SELECT DISTINCT target_uri FROM occupation_mappings WHERE target_system='ESCO'")}
        possible = {r[0] for r in db.execute("""
            SELECT DISTINCT m.target_uri FROM occupation_mappings m
            JOIN onet_tasks t ON t.onet_soc_code=m.onet_soc_code
            WHERE m.target_system='ESCO'
        """)}
    result = {}
    for uri, occupation in occupations.items():
        count = counts.get(uri, {})
        total, assessed = count.get("task_count", 0), count.get("classified_count", 0)
        ready = bool(total > 0 and assessed == total and
                     count.get("exact_source_count") == count.get("available_source_count"))
        eligible = bool(ready and verified and not count.get("truncated_count", 0))
        result[uri] = {
            "occupation_uri": uri, "title": occupation["label"],
            "mapping_status": "exact" if count else "possible_only" if uri in possible else
                              "mapped_source_tasks_missing" if uri in mapped else "none",
            "task_count": total, "classified_count": assessed,
            "task_inventory_ready": ready,
            "exact_source_count": count.get("exact_source_count", 0),
            "available_source_count": count.get("available_source_count", 0),
            "truncated_count": count.get("truncated_count", 0),
            **{f"e{i}_count": count.get(f"e{i}_count", 0) for i in range(3)},
            "lower_exposure_eligible": eligible,
            "predicted_task_exposure_share": (
                round(100 * (count["e1_count"] + count["e2_count"]) / assessed, 2)
                if eligible else None),
        }
    return result, {
        "source": "O*NET 31.0 Task Statements",
        "source_url": "https://www.onetcenter.org/dictionary/31.0/csv/task_statements.html",
        "mapping_source": "European Commission ESCO–O*NET crosswalk, v1 September 2022",
        "mapping_url": "https://esco.ec.europa.eu/en/use-esco/other-crosswalks",
        "prediction_fingerprint": method,
        "task_records": int(metadata["task_source_record_count"]),
        "source_occupations": int(metadata["task_unique_occupation_count"]),
        "catalog_occupations": len(occupations),
        "exact_complete_occupations": sum(r["task_inventory_ready"] for r in result.values()),
        "possible_only_occupations": sum(r["mapping_status"] == "possible_only" for r in result.values()),
        "mapped_without_tasks_occupations": sum(
            r["mapping_status"] == "mapped_source_tasks_missing" for r in result.values()),
        "unmapped_occupations": sum(r["mapping_status"] == "none" for r in result.values()),
        "eligible_occupation_count": sum(r["lower_exposure_eligible"] for r in result.values()),
        "eligibility_policy": (
            "Approved label provenance; exact EC crosswalk; every linked source occupation has tasks; "
            "100% matching, untruncated predictions from the same source release and inference fingerprint. "
            "Unweighted source task records, not working hours or job-loss risk."
        ),
    }


def task_inventory():
    from futuretwin_distilbert import CLASSIFIER, prediction_version
    from futuretwin_onet_exposure_db import DATABASE
    model = CLASSIFIER.metadata()
    return _inventory(DATABASE.stat().st_mtime_ns, prediction_version(model),
                      bool(model.get("label_definitions_verified")))


def ranking_evidence():
    try:
        _, tasks = task_inventory()
    except (OSError, sqlite3.Error, ValueError, KeyError, RuntimeError):
        tasks = {"status": "unavailable", "eligible_occupation_count": 0,
                 "reason": "Matching precomputed task inventory could not be verified."}
    return {"labels": label_audit(), "tasks": tasks, "vacancies": vacancy_history()}


def career_ranking_eligibility(exposure):
    """Expose real prerequisites without inventing a broad-exposure percentage."""
    ready = (
        exposure.get("status") == "available"
        and exposure.get("classified_task_count", 0) > 0
        and exposure.get("task_coverage_percentage") == 100
    )
    share = exposure.get("predicted_task_exposure", {})
    verified = bool(exposure.get("label_definitions_verified"))
    eligible = bool(ready and verified and exposure.get("exact_source_inventory_complete")
                    and share.get("status") == "available" and share.get("percentage") is not None)
    return {
        "lower_exposure": {
            "eligible": eligible, "task_inventory_ready": ready,
            "training_label_contract_verified": verified,
            "reason": None if eligible else
                      share.get("reason") or "No verified, complete exact-linked task-exposure share.",
        },
        "growing_jobs": {
            "eligible": False,
            "reason": "No verified exact-occupation vacancy series; broad DOSM groups are not career counts.",
        },
    }


def export_eligibility(path):
    inventory, _ = task_inventory()
    fields = ["occupation_uri", "title", "mapping_status", "task_count", "classified_count",
              "task_inventory_ready", "lower_exposure_eligible", "growing_jobs_eligible",
              "lower_exposure_blocker", "growing_jobs_blocker", "exact_source_count",
              "available_source_count", "truncated_count", "e0_count", "e1_count", "e2_count",
              "predicted_task_exposure_share"]
    with Path(path).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in sorted(inventory.values(), key=lambda r: (r["title"].casefold(), r["occupation_uri"])):
            writer.writerow({
                **row, "growing_jobs_eligible": False,
                "lower_exposure_blocker": "" if row["lower_exposure_eligible"] else
                    "unverified_labels_or_truncated_predictions" if row["task_inventory_ready"]
                    else "insufficient_exact_task_inventory",
                "growing_jobs_blocker": "no_comparable_exact_occupation_vacancy_series",
            })
