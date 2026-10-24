"""Explicit offline import of DOSM's published JMI summary workbook; no inference."""
from __future__ import annotations

import argparse
import csv
from datetime import date, datetime, timezone
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile

DATA = Path(__file__).resolve().parent / "data"
NS = {"s": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
CURRENT_SHA256 = "703468929bc0a16b8a71b16c20ad5a74bad112786c414b447b947b5e2ca22831"
PREVIOUS_SHA256 = "0eaba812b02705f7b69b14b84201f81bc51f2d2d23ff0a7e894357f9da3c5e40"
GROUPS = [
    ("managers", "Managers"),
    ("professionals", "Professionals"),
    ("technicians", "Technicians and associate professionals"),
    ("clerical", "Clerical support workers"),
    ("service-sales", "Service and sales workers"),
    ("agriculture", "Skilled agricultural, forestry, livestock and fishery workers"),
    ("craft", "Craft and related trades workers"),
    ("operators", "Plant and machine operators and assemblers"),
]
SOURCE = {
    "publisher": "Department of Statistics Malaysia",
    "title": "Job Market Insights and My Job Profile, Third Quarter 2024",
    "url": "https://www.dosm.gov.my/portal-main/release-content/big-data-analytics-job-market-insights-and-my-job-profile-q324",
    "download_url": "https://www.dosm.gov.my/portal-main/release-document-log?release_document_id=18396",
    "resolved_download_url": "https://www.dosm.gov.my/uploads/release-content/file_20260327201248.xlsx",
    "terms_url": "https://www.dosm.gov.my/portal-main/article/term-of-use",
    "license": "Government Open Data Terms of Use 1.0, via DOSM portal terms",
    "attribution": "Data source: Department of Statistics Malaysia",
    "endorsement_note": "FutureTwin's extraction and analysis are not endorsed by DOSM.",
    "geography": "Malaysia",
    "classification_system": "DOSM JMI published major occupation groups",
    "classification_version": None,
    "classification_note": (
        "Workbook has group labels, not official occupation codes or a classification version. "
        "source_group_id is a FutureTwin source-row identifier, NOT an official MASCO/ISCO code."
    ),
}


def workbook_cells(path):
    """Read a bounded local XLSX with stdlib; reject formulas without cached values."""
    with zipfile.ZipFile(path) as z:
        if sum(i.file_size for i in z.infolist()) > 20_000_000:
            raise ValueError("Workbook uncompressed size exceeds the import limit.")
        strings = [
            "".join(x.itertext())
            for x in ET.fromstring(z.read("xl/sharedStrings.xml"))
        ]
        root = ET.fromstring(z.read("xl/worksheets/sheet1.xml"))
        cells = {}
        for cell in root.findall("s:sheetData/s:row/s:c", NS):
            value = cell.find("s:v", NS)
            if value is None or value.text is None:
                continue
            text = value.text
            if cell.get("t") == "s":
                text = strings[int(text)]
            cells[cell.attrib["r"]] = text
        return cells


def _column(index):
    result = ""
    while index:
        index, remainder = divmod(index - 1, 26)
        result = chr(65 + remainder) + result
    return result


def extract_quarters(path, *, through=(2024, 3)):
    """Import only observed periods, never the workbook's future zero placeholders."""
    cells = workbook_cells(path)
    if cells.get("B30") != "Table 2: Number of Job Offering Advertised Online by Occupation":
        raise ValueError("Expected DOSM occupation table was not found.")
    for row, (_, label) in enumerate(GROUPS, 35):
        if cells.get(f"B{row}") != label:
            raise ValueError("Occupation grouping changed; review the source before importing.")
    records = []
    for offset in range(24):  # H..AE; actual quarterly section ends at AC
        year = 2019 + (offset + 2) // 4
        quarter = (offset + 2) % 4 + 1
        if (year, quarter) > through:
            break
        col = _column(8 + offset)
        if cells.get(f"{col}33") != f"Q{quarter}":
            raise ValueError("Unexpected quarterly column layout.")
        monthly_columns = [_column(31 + offset * 3 + m) for m in range(3)]
        for row, (identifier, label) in enumerate(GROUPS, 35):
            raw = cells.get(f"{col}{row}", "")
            months = [cells.get(f"{m}{row}", "") for m in monthly_columns]
            if not raw.isdigit() or not all(m.isdigit() for m in months):
                raise ValueError("Missing/suppressed data cannot be converted to zero.")
            if int(raw) != sum(map(int, months)):
                raise ValueError(f"Quarter/month disagreement at {col}{row}.")
            start_month = 3 * quarter - 2
            end = date(year + (quarter == 4), start_month + 3 if quarter < 4 else 1, 1)
            # All periods are full calendar quarters, with an exclusive end.
            records.append({
                "source_group_id": f"dosm-jmi:{identifier}",
                "occupation_label": label,
                "occupation_code": "",
                "classification_system": SOURCE["classification_system"],
                "classification_version": "",
                "scope": "major_group",
                "geography": "Malaysia",
                "period": f"{year}-Q{quarter}",
                "period_start": date(year, start_month, 1).isoformat(),
                "period_end_exclusive": end.isoformat(),
                "vacancies": int(raw),
                "measure": "online_advertised_job_offerings",
                "source_cell": f"{col}{row}",
                "source_sheet": "Summary Table",
                "validation": "quarter_equals_sum_of_three_months",
            })
    return records


def import_history(current_path, previous_path):
    for path, expected in [(current_path, CURRENT_SHA256), (previous_path, PREVIOUS_SHA256)]:
        if hashlib.sha256(Path(path).read_bytes()).hexdigest() != expected:
            raise ValueError("Workbook differs from the reviewed DOSM snapshot; re-audit before import.")
    current = extract_quarters(current_path)
    previous = extract_quarters(previous_path, through=(2024, 2))
    index = {(r["source_group_id"], r["period"]): r["vacancies"] for r in current}
    differences = [
        r for r in previous if index.get((r["source_group_id"], r["period"])) != r["vacancies"]
    ]
    if differences:
        raise ValueError("Overlapping releases disagree; a revision review is required.")
    retrieved = datetime.now(timezone.utc).isoformat()
    current_hash = hashlib.sha256(Path(current_path).read_bytes()).hexdigest()
    csv_path = DATA / "dosm_jmi_group_vacancies.csv"
    fields = list(current[0]) + ["source_url", "retrieved_at", "source_sha256"]
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in current:
            writer.writerow({**row, "source_url": SOURCE["url"],
                             "retrieved_at": retrieved, "source_sha256": current_hash})
    metadata = {
        **SOURCE, "retrieved_at": retrieved, "source_sha256": current_hash,
        "csv_sha256": hashlib.sha256(csv_path.read_bytes()).hexdigest(),
        "observation_count": len(current), "group_count": len(GROUPS),
        "period_start": "2019-Q3", "period_end": "2024-Q3",
        "verified_overlap_observations": len(previous),
        "previous_release": {
            "download_url": "https://www.dosm.gov.my/portal-main/release-document-log?release_document_id=16067",
            "resolved_download_url": "https://www.dosm.gov.my/uploads/release-content/file_20250924161935.xlsx",
            "sha256": hashlib.sha256(Path(previous_path).read_bytes()).hexdigest(),
        },
        "exact_esco_mappings": 0,
        "eligible_for_career_ranking": False,
        "limitations": [
            "Historical snapshot, not current Malaysian vacancies or complete market coverage.",
            "Only eight published broad groups; no precise ESCO career observations or verified MASCO–ESCO crosswalk.",
            "No classification version is specified in the workbook; official occupation codes are not inferred.",
            "Future/unobserved quarter zeros and Unclassified are excluded, not treated as real vacancies.",
            "Q3 2024 occupation total cell AB34 is zero despite nonzero group cells. It is not imported.",
            "Q3 release webpage repeats Q2 group prose; worksheet group cells, monthly sums and prior release are used.",
            "Consistent historical source counts do not establish a fixed recruitment-site sampling frame.",
        ],
    }
    (DATA / "dosm_jmi_group_vacancies.meta.json").write_text(
        json.dumps(metadata, indent=2) + "\n", encoding="utf-8"
    )
    return metadata


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("current_xlsx")
    parser.add_argument("previous_xlsx")
    args = parser.parse_args()
    print(json.dumps(import_history(args.current_xlsx, args.previous_xlsx), indent=2))
