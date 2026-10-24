"""Local O*NET/ESCO task data and trained DistilBERT occupation results."""
from __future__ import annotations

import csv
from contextlib import contextmanager
import gzip
import hashlib
import json
from pathlib import Path
import sqlite3
from datetime import datetime, timezone

BASE = Path(__file__).resolve().parent
DATA_DIR = BASE / "data"
DATABASE = BASE.parent / "generated-artifacts/onet_task_exposure.sqlite3"
TASKS_GZIP = DATA_DIR / "onet_task_statements_31_0.csv.gz"
MAPPINGS_GZIP = DATA_DIR / "esco_onet_occupations_v1_2022_09.csv.gz"

TASK_SOURCE = {
    "name": "O*NET 31.0 Task Statements",
    "url": "https://www.onetcenter.org/dictionary/31.0/csv/task_statements.html",
    "download_url": "https://www.onetcenter.org/dl_files/database/db_31_0_csv/task_statements.csv",
    "license": "Creative Commons Attribution 4.0 International (CC BY 4.0)",
    "license_url": "https://creativecommons.org/licenses/by/4.0/",
    "attribution": (
        "This page includes information from the O*NET 31.0 Database by the "
        "U.S. Department of Labor, Employment and Training Administration (USDOL/ETA). "
        "Used under the CC BY 4.0 license. O*NET® is a trademark of USDOL/ETA. "
        "Task classifications and ESCO links are FutureTwin modifications; USDOL/ETA "
        "has not approved, endorsed, or tested these modifications."
    ),
    "source_organization": "U.S. Department of Labor, Employment and Training Administration",
    "snapshot_retrieved": "2026-10-23",
}
MAPPING_SOURCE = {
    "name": "European Commission ESCO–O*NET occupation crosswalk",
    "url": "https://esco.ec.europa.eu/en/use-esco/other-crosswalks",
    "download_url": (
        "https://esco.ec.europa.eu/system/files/2023-08/"
        "ONET_%28Occupations%29_0_updated.csv"
    ),
    "technical_report": (
        "https://esco.ec.europa.eu/en/about-esco/data-science-and-esco/"
        "crosswalk-between-esco-and-onet"
    ),
    "publisher": "ESCO Secretariat, in collaboration with U.S. DOL/ETA",
    "method_note": (
        "The European Commission describes semantic candidate generation followed "
        "by human validation and quality review. Original match types are retained."
    ),
    "snapshot_retrieved": "2026-10-23",
}

SCHEMA = """
CREATE TABLE IF NOT EXISTS source_metadata (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS onet_tasks (
    onet_soc_code TEXT NOT NULL,
    occupation_title TEXT NOT NULL,
    task_id TEXT NOT NULL,
    task_text TEXT NOT NULL,
    task_type TEXT NOT NULL,
    incumbents_responding TEXT NOT NULL,
    task_date TEXT NOT NULL,
    domain_source TEXT NOT NULL,
    PRIMARY KEY (onet_soc_code, task_id)
);
CREATE INDEX IF NOT EXISTS idx_onet_tasks_code ON onet_tasks(onet_soc_code);
CREATE TABLE IF NOT EXISTS occupation_mappings (
    onet_soc_code TEXT NOT NULL,
    onet_title TEXT NOT NULL,
    onet_description TEXT NOT NULL,
    target_uri TEXT NOT NULL,
    target_title TEXT NOT NULL,
    target_description TEXT NOT NULL,
    target_system TEXT NOT NULL,
    relationship TEXT NOT NULL,
    mapping_version TEXT NOT NULL,
    mapping_date TEXT NOT NULL,
    PRIMARY KEY (onet_soc_code, target_uri, relationship)
);
CREATE INDEX IF NOT EXISTS idx_mapping_target
    ON occupation_mappings(target_uri, target_system, relationship);
CREATE TABLE IF NOT EXISTS task_predictions (
    model_fingerprint TEXT NOT NULL,
    onet_soc_code TEXT NOT NULL,
    task_id TEXT NOT NULL,
    text_sha256 TEXT NOT NULL,
    label TEXT NOT NULL CHECK(label IN ('E0', 'E1', 'E2')),
    p_e0 REAL NOT NULL,
    p_e1 REAL NOT NULL,
    p_e2 REAL NOT NULL,
    input_tokens INTEGER NOT NULL,
    processed_tokens INTEGER NOT NULL,
    truncated INTEGER NOT NULL CHECK(truncated IN (0, 1)),
    PRIMARY KEY (model_fingerprint, onet_soc_code, task_id)
);
CREATE INDEX IF NOT EXISTS idx_prediction_model
    ON task_predictions(model_fingerprint, label);
"""


@contextmanager
def connect(path=DATABASE, read_only=False):
    database = Path(path)
    if read_only:
        connection = sqlite3.connect(
            f"file:{database.resolve()}?mode=ro", uri=True, timeout=30
        )
    else:
        database.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(database, timeout=30)
    connection.row_factory = sqlite3.Row
    try:
        if not read_only:
            connection.executescript(SCHEMA)
        yield connection
    finally:
        connection.close()


def _sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _load_tasks(path=TASKS_GZIP):
    required = {
        "O*NET-SOC Code", "Title", "Task ID", "Task", "Task Type",
        "Incumbents Responding", "Date", "Domain Source",
    }
    with gzip.open(path, "rt", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not required.issubset(reader.fieldnames or []):
            raise ValueError("O*NET task file does not match its documented 31.0 schema.")
        rows = []
        seen = set()
        for row in reader:
            code, task_id, text = (
                row["O*NET-SOC Code"].strip(),
                row["Task ID"].strip(),
                row["Task"].strip(),
            )
            key = (code, task_id)
            if not code or not task_id or not text or key in seen:
                raise ValueError("O*NET task file has a blank or duplicate task identity.")
            seen.add(key)
            rows.append((
                code, row["Title"].strip(), task_id, text, row["Task Type"].strip(),
                row["Incumbents Responding"].strip(), row["Date"].strip(),
                row["Domain Source"].strip(),
            ))
    return rows


def _load_mappings(path=MAPPINGS_GZIP):
    fieldnames = None
    metadata = {}
    rows = []
    with gzip.open(path, "rt", encoding="utf-8-sig", newline="") as handle:
        reader = csv.reader(handle)
        for row in reader:
            if row and row[0].strip() == "O*NET Id":
                fieldnames = [value.strip() for value in row]
                break
            if len(row) >= 2 and row[0].strip():
                metadata[row[0].strip()] = row[1].strip()
        if not fieldnames:
            raise ValueError("European Commission crosswalk header was not found.")
        required = {
            "O*NET Id", "O*NET Title", "O*NET Description", "ESCO or ISCO URI",
            "ESCO or ISCO Title", "ESCO or ISCO Description", "Type of Match",
        }
        if not required.issubset(fieldnames):
            raise ValueError("Crosswalk file does not match its published schema.")
        for values in reader:
            row = dict(zip(fieldnames, values))
            code = row["O*NET Id"].strip()
            uri = row["ESCO or ISCO URI"].strip()
            relation = row["Type of Match"].strip()
            if not code or not uri or not relation:
                raise ValueError("Crosswalk contains a row with incomplete mapping provenance.")
            if "/occupation/" in uri:
                target_system = "ESCO"
            elif "isco" in uri.casefold() or relation == "exactISCO":
                target_system = "ISCO"
            else:
                target_system = "unclassified"
            rows.append((
                code, row["O*NET Title"].strip(), row["O*NET Description"].strip(),
                uri, row["ESCO or ISCO Title"].strip(),
                row["ESCO or ISCO Description"].strip(), target_system, relation,
                metadata.get("Mapping project version", ""),
                metadata.get("Mapping project version date", ""),
            ))
    return metadata, rows


def import_source_data(path=DATABASE, tasks_path=TASKS_GZIP, mappings_path=MAPPINGS_GZIP):
    task_hash, mapping_hash = _sha256(tasks_path), _sha256(mappings_path)
    task_rows = _load_tasks(tasks_path)
    mapping_metadata, mapping_rows = _load_mappings(mappings_path)
    if not task_rows or not mapping_rows:
        raise ValueError("Official O*NET tasks and occupation mappings must both be present.")

    metadata = {
        "task_source": TASK_SOURCE,
        "mapping_source": {**MAPPING_SOURCE, "published_metadata": mapping_metadata},
        "task_asset_sha256": task_hash,
        "mapping_asset_sha256": mapping_hash,
        "task_source_record_count": str(len(task_rows)),
        "mapping_source_edge_count": str(len(mapping_rows)),
        "esco_match_type_counts": json.dumps({
            relation: sum(row[6] == "ESCO" and row[7] == relation for row in mapping_rows)
            for relation in sorted({row[7] for row in mapping_rows if row[6] == "ESCO"})
        }, sort_keys=True),
    }
    with connect(path) as connection:
        existing = dict(connection.execute("SELECT key, value FROM source_metadata"))
        if (existing.get("task_asset_sha256") == task_hash
                and existing.get("mapping_asset_sha256") == mapping_hash
                and existing.get("task_source_record_count") == str(len(task_rows))
                and existing.get("mapping_source_edge_count") == str(len(mapping_rows))):
            return {"imported": False, "task_rows": len(task_rows),
                    "mapping_edges": len(mapping_rows), "metadata": metadata}

        with connection:
            connection.execute("DELETE FROM task_predictions")
            connection.execute("DELETE FROM onet_tasks")
            connection.execute("DELETE FROM occupation_mappings")
            connection.executemany(
                "INSERT INTO onet_tasks VALUES (?,?,?,?,?,?,?,?)", task_rows
            )
            connection.executemany(
                "INSERT INTO occupation_mappings VALUES (?,?,?,?,?,?,?,?,?,?)", mapping_rows
            )
            metadata["imported_at_utc"] = datetime.now(timezone.utc).isoformat()
            for key, value in metadata.items():
                connection.execute(
                    "INSERT OR REPLACE INTO source_metadata(key,value) VALUES (?,?)",
                    (key, value if isinstance(value, str) else json.dumps(value, sort_keys=True)),
                )
            connection.execute(
                "INSERT OR REPLACE INTO source_metadata(key,value) VALUES (?,?)",
                ("task_unique_occupation_count", str(connection.execute(
                    "SELECT count(DISTINCT onet_soc_code) FROM onet_tasks"
                ).fetchone()[0])),
            )
            connection.execute(
                "INSERT OR REPLACE INTO source_metadata(key,value) VALUES (?,?)",
                ("mapping_onet_occupation_count", str(connection.execute(
                    "SELECT count(DISTINCT onet_soc_code) FROM occupation_mappings"
                ).fetchone()[0])),
            )
    return {"imported": True, "task_rows": len(task_rows),
            "mapping_edges": len(mapping_rows), "metadata": metadata}


def precompute_database(path=DATABASE, progress=None, activate=True):
    """Import both official sources, then infer all distinct task texts with one local model load."""
    from futuretwin_distilbert import CLASSIFIER, prediction_version

    imported = import_source_data(path=path)
    model = CLASSIFIER.metadata()
    fingerprint = prediction_version(model)
    with connect(path) as connection:
        tasks = connection.execute(
            "SELECT onet_soc_code, task_id, task_text FROM onet_tasks "
            "ORDER BY onet_soc_code, task_id"
        ).fetchall()
        ready_rows = connection.execute(
            "SELECT onet_soc_code,task_id,text_sha256 FROM task_predictions "
            "WHERE model_fingerprint=?",
            (fingerprint,),
        ).fetchall()
        ready = {(row["onet_soc_code"], row["task_id"]): row["text_sha256"]
                 for row in ready_rows}
        if len(ready) == len(tasks) and all(
            ready.get((row["onet_soc_code"], row["task_id"]))
            == hashlib.sha256(row["task_text"].encode("utf-8")).hexdigest()
            for row in tasks
        ):
            if activate:
                with connection:
                    connection.execute(
                        "INSERT OR REPLACE INTO source_metadata(key,value) VALUES (?,?)",
                        ("active_model_fingerprint", fingerprint),
                    )
            return {
                "status": "ready", "source_import": imported, "reused_database": True,
                "task_records": len(tasks), "unique_task_texts": None,
                "model": model, "database": str(Path(path)),
            }

        unique_texts = list(dict.fromkeys(row["task_text"] for row in tasks))
        run = CLASSIFIER.classify_corpus(unique_texts, progress=progress)
        prediction_by_text = dict(zip(unique_texts, run["predictions"]))
        inserts = []
        for row in tasks:
            prediction = prediction_by_text[row["task_text"]]
            probabilities = prediction["probabilities"]
            inserts.append((
                fingerprint, row["onet_soc_code"], row["task_id"],
                hashlib.sha256(row["task_text"].encode("utf-8")).hexdigest(),
                prediction["label"], probabilities["E0"], probabilities["E1"],
                probabilities["E2"], prediction["input_tokens"],
                prediction["processed_tokens"], int(prediction["truncated"]),
            ))
        with connection:
            connection.executemany(
                "INSERT OR REPLACE INTO task_predictions VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                inserts,
            )
            if activate:
                connection.execute(
                    "INSERT OR REPLACE INTO source_metadata(key,value) VALUES (?,?)",
                    ("active_model_fingerprint", fingerprint),
                )
    return {
        "status": "ready", "source_import": imported, "reused_database": False,
        "task_records": len(tasks), "unique_task_texts": len(unique_texts),
        "inferred_unique_texts": len(run["predictions"]),
        "cache_hits": run["cache_hits"], "model": model,
        "database": str(Path(path)),
    }
