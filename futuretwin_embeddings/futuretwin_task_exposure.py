"""Evidence-aware O*NET task distributions kept separate from career fit."""
from __future__ import annotations

from collections import defaultdict
import hashlib
import json
import sqlite3

from futuretwin_distilbert import CLASSIFIER, LABELS, ModelBusy, ModelUnavailable, prediction_version
from futuretwin_onet_exposure_db import DATABASE, connect
from futuretwin_exposure_contract import predicted_share

NEAR_TIE_GAP = 0.05
EXACT_RELATION = "exactMatch"
SOURCE = {
    "name": "O*NET 31.0 Task Statements",
    "kind": "official_task_inventory", "official": True,
    "url": "https://www.onetcenter.org/dictionary/31.0/csv/task_statements.html",
    "license": "CC BY 4.0",
    "license_url": "https://creativecommons.org/licenses/by/4.0/",
    "attribution": (
        "This page includes information from the O*NET 31.0 Database by the U.S. "
        "Department of Labor, Employment and Training Administration (USDOL/ETA). "
        "Used under CC BY 4.0. O*NET® is a USDOL/ETA trademark. FutureTwin added "
        "local task classifications and occupation links; USDOL/ETA has not approved, "
        "endorsed, or tested these modifications."
    ),
}
MAPPING_SOURCE = {
    "name": "European Commission ESCO–O*NET occupation crosswalk",
    "url": "https://esco.ec.europa.eu/en/use-esco/other-crosswalks",
    "technical_report": "https://esco.ec.europa.eu/en/about-esco/data-science-and-esco/crosswalk-between-esco-and-onet",
    "publisher": "ESCO Secretariat with U.S. DOL/ETA",
    "attribution": (
        "This service uses the ESCO classification of the European Commission. "
        "FutureTwin preserves the published crosswalk relation types and adds "
        "its own local task classifications."
    ),
    "relationship_note": (
        "Published relation types are preserved. Only exactMatch links contribute "
        "to the occupation's primary task distribution; other relations remain "
        "separate possible mappings."
    ),
}
INTERPRETATION = (
    "Percentages are unweighted class shares of tasks from exact-mapped O*NET "
    "inventories. They are not work-time, employment, automation, or job-replacement "
    "probabilities. Other crosswalk relationships are shown separately as possible "
    "task sets."
)


def _db_metadata(connection):
    return dict(connection.execute("SELECT key,value FROM source_metadata"))


def _missing(reason):
    return {
        "status": reason, "sample_task_count": 0, "occupation_total_task_count": None,
        "classified_task_count": 0, "task_coverage_percentage": None,
        "distribution": {}, "tasks": [], "candidate_mappings": [],
        "combined_exposure_percentage": None,
        "combined_exposure_note": (
            "No job-replacement percentage. See the separately labelled predicted task-exposure share when eligible."
        ),
        "predicted_task_exposure": {"status": "not_enough_data", "percentage": None,
                                    "reason": "Complete exact-linked task predictions are unavailable."},
    }


def _classification(row):
    probabilities = {label: row[f"p_{label.casefold()}"] for label in LABELS}
    best_two = sorted(probabilities.items(), key=lambda item: item[1], reverse=True)[:2]
    gap = best_two[0][1] - best_two[1][1]
    near_tie_e1_e2 = (
        {best_two[0][0], best_two[1][0]} == {"E1", "E2"} and gap <= NEAR_TIE_GAP
    )
    return {
        "label": row["label"], "probabilities": probabilities,
        "input_tokens": row["input_tokens"], "processed_tokens": row["processed_tokens"],
        "truncated": bool(row["truncated"]),
        "top_two_score_gap": round(gap, 6),
        "near_tie_e1_e2": near_tie_e1_e2,
    }


def _distribution(tasks):
    counts = {label: sum(task["label"] == label for task in tasks) for label in LABELS}
    size = len(tasks)
    return {
        label: {
            "count": count,
            "percentage": round(100 * count / size, 2) if size else None,
        }
        for label, count in counts.items()
    }


def _task_record(row):
    result = {
        "task_id": row["task_id"], "text": row["task_text"],
        "onet_soc_code": row["onet_soc_code"],
        "onet_occupation": row["occupation_title"],
        "task_type": row["task_type"], "incumbents_responding": row["incumbents_responding"],
        "task_date": row["task_date"], "domain_source": row["domain_source"],
    }
    if (row["label"] in LABELS
            and row["text_sha256"] == hashlib.sha256(
                row["task_text"].encode("utf-8")).hexdigest()):
        result.update(_classification(row))
    else:
        result["prediction_status"] = "not_precomputed"
    return result


def _mapping_record(row, tasks, include_tasks=True):
    return {
        "onet_soc_code": row["onet_soc_code"], "onet_occupation": row["onet_title"],
        "esco_uri": row["target_uri"], "esco_occupation": row["target_title"],
        "relationship": row["relationship"],
        "source": MAPPING_SOURCE["name"],
        "mapping_version": row["mapping_version"], "mapping_date": row["mapping_date"],
        "relationship_is_exact": row["relationship"] == EXACT_RELATION,
        "task_record_count": len(tasks),
        "classified_task_count": sum("label" in task for task in tasks),
        "distribution": _distribution([task for task in tasks if "label" in task]),
        "tasks": tasks if include_tasks else [],
    }


def occupation_exposure(uri: str, include_tasks=True, cached_only=True) -> dict:
    """Read stored local predictions; browsing never loads DistilBERT or uses title guesses."""
    model = CLASSIFIER.metadata()
    if not DATABASE.exists():
        return {**_missing("not_precomputed"), "model": model, "source": SOURCE}
    try:
        with connect(DATABASE, read_only=True) as connection:
            metadata = _db_metadata(connection)
            if metadata.get("active_model_fingerprint") != prediction_version(model):
                return {**_missing("not_precomputed"), "model": model, "source": SOURCE}

            published_mapping_metadata = json.loads(
                metadata.get("mapping_source", "{}")
            ).get("published_metadata", {})
            mapping_source = {
                **MAPPING_SOURCE,
                "published_metadata": published_mapping_metadata,
                "asset_sha256": metadata.get("mapping_asset_sha256"),
            }
            task_source = {
                **SOURCE, "asset_sha256": metadata.get("task_asset_sha256"),
            }

            mapping_rows = connection.execute(
                """SELECT * FROM occupation_mappings
                   WHERE target_uri=? AND target_system='ESCO'
                   ORDER BY relationship, onet_soc_code""",
                (uri,),
            ).fetchall()
            if not mapping_rows:
                return {
                    **_missing("not_enough_task_data"), "model": model,
                    "source": task_source, "mapping_source": mapping_source,
                    "mapping_status": "no_published_esco_mapping",
                }

            relation_codes = defaultdict(dict)
            for row in mapping_rows:
                relation_codes[row["relationship"]][row["onet_soc_code"]] = {
                    "onet_soc_code": row["onet_soc_code"],
                    "onet_title": row["onet_title"],
                    "target_uri": row["target_uri"],
                    "target_title": row["target_title"],
                    "relationship": row["relationship"],
                    "mapping_version": row["mapping_version"],
                    "mapping_date": row["mapping_date"],
                    "source": MAPPING_SOURCE["name"],
                }

            def load_grouped_tasks(codes):
                if not codes:
                    return []
                placeholders = ",".join("?" for _ in codes)
                records = connection.execute(
                    f"""SELECT t.*, p.label, p.p_e0, p.p_e1, p.p_e2,
                               p.input_tokens, p.processed_tokens, p.truncated
                        , p.text_sha256 FROM onet_tasks AS t
                        LEFT JOIN task_predictions AS p
                          ON p.onet_soc_code=t.onet_soc_code AND p.task_id=t.task_id
                         AND p.model_fingerprint=?
                        WHERE t.onet_soc_code IN ({placeholders})
                        ORDER BY t.onet_soc_code,t.task_id""",
                    (prediction_version(model), *codes),
                ).fetchall()
                return [_task_record(row) for row in records]

            exact_codes = relation_codes.pop(EXACT_RELATION, {})
            exact_tasks = load_grouped_tasks(list(exact_codes))
            grouped_exact = defaultdict(list)
            for task in exact_tasks:
                grouped_exact[task["onet_soc_code"]].append(task)

            candidates = []
            for relation, sources in sorted(relation_codes.items()):
                candidate_tasks = load_grouped_tasks(list(sources))
                grouped = defaultdict(list)
                for task in candidate_tasks:
                    grouped[task["onet_soc_code"]].append(task)
                for code, mapping in sources.items():
                    candidates.append(_mapping_record(mapping, grouped[code], include_tasks))

            all_exact_tasks = [
                task for tasks in grouped_exact.values() for task in tasks
            ]
            classified = [task for task in all_exact_tasks if "label" in task]
            exact_source_complete = bool(exact_codes) and all(
                grouped_exact.get(code) for code in exact_codes)
            if not exact_codes:
                status = "uncertain_mapping" if candidates else "not_enough_task_data"
                task_coverage = None
                exact_distribution = {}
            else:
                complete = len(classified) == len(all_exact_tasks) and bool(all_exact_tasks)
                status = (
                    "available" if complete else
                    "not_precomputed" if all_exact_tasks else "not_enough_task_data"
                )
                task_coverage = (
                    round(100 * len(classified) / len(all_exact_tasks), 2)
                    if all_exact_tasks else None
                )
                exact_distribution = _distribution(classified) if complete else {}
            share = predicted_share(
                exact_distribution, len(classified),
                ready=status == "available" and exact_source_complete, model=model,
                truncated=sum(task.get("truncated", False) for task in classified),
            )

            mapping_list = [mapping for sources in relation_codes.values()
                            for mapping in sources.values()]
            mapping_list.extend(exact_codes.values())
            return {
                "status": status,
                "mapping_status": (
                    "exact_and_possible" if exact_codes and candidates else
                    "exact" if exact_codes else
                    "possible_only" if candidates else "no_published_esco_mapping"
                ),
                "occupation_uri": uri,
                "model": model, "source": task_source, "mapping_source": mapping_source,
                "sample_task_count": len(classified),
                "occupation_total_task_count": len(all_exact_tasks) if exact_codes else None,
                "classified_task_count": len(classified),
                "mapped_onet_occupation_count": len(exact_codes),
                "task_coverage_percentage": task_coverage,
                "distribution": exact_distribution,
                "label_definitions_verified": model.get("label_definitions_verified", False),
                "exact_source_inventory_complete": exact_source_complete,
                "predicted_task_exposure": share,
                "combined_exposure_percentage": None,
                "combined_exposure_note": (
                    "No job-replacement percentage or weighted exposure score. "
                    "The separately labelled predicted task-exposure share uses E1+E2 task counts only."
                ),
                "interpretation": INTERPRETATION,
                "uncertainty_method": (
                    f"Near-tie display flag: the two largest raw softmax outputs differ "
                    f"by at most {100 * NEAR_TIE_GAP:g} percentage points. This is a display heuristic, not "
                    "calibrated uncertainty or confidence."
                ),
                "near_tie_e1_e2_task_count": sum(
                    task.get("near_tie_e1_e2", False) for task in classified
                ),
                "occupation_mappings": mapping_list,
                "candidate_mappings": candidates,
                "tasks": classified if include_tasks else [],
                "candidate_task_note": (
                    "Possible mapped O*NET tasks are shown separately; they do not "
                    "contribute to the exact-match occupation distribution."
                ),
                "source_task_coverage_note": (
                    "Coverage is the share of task records in the exact-mapped "
                    "O*NET inventory that were classified. It is not the share of "
                    "all tasks performed in the ESCO occupation."
                ),
                "database_source_counts": {
                    "onet_task_records": int(metadata.get("task_source_record_count", 0)),
                    "onet_occupations_with_tasks": int(
                        metadata.get("task_unique_occupation_count", 0)
                    ),
                },
            }
    except (OSError, sqlite3.Error, KeyError, ValueError) as exc:
        raise ModelUnavailable("The precomputed O*NET exposure database is unavailable.") from exc


def safe_occupation_exposure(uri: str, include_tasks=True) -> dict:
    """A local model or data fault must not break existing ESCO/career recommendations."""
    try:
        return occupation_exposure(uri, include_tasks=include_tasks)
    except (ModelUnavailable, ModelBusy, OSError, ValueError, KeyError, sqlite3.Error) as exc:
        return {
            "status": "unavailable", "note": str(exc),
            "combined_exposure_percentage": None, "tasks": [],
            "candidate_mappings": [], "distribution": {},
        }


def precompute(progress=None):
    from futuretwin_onet_exposure_db import precompute_database
    return precompute_database(progress=progress)


if __name__ == "__main__":
    import json
    import torch
    torch.set_num_threads(2)

    def report_progress(done, total):
        if done == total or done % 1000 == 0:
            print(f"Locally classified {done:,}/{total:,} unique task descriptions.", flush=True)

    print(json.dumps(precompute(progress=report_progress), indent=2), flush=True)
