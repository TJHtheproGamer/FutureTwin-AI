#!/usr/bin/env python3
"""Verify private runtime assets without loading models or opening user data."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "runtime-assets.json"
PATHS = [
    "futuretwin_embeddings/models/futuretwin_minilm",
    "futuretwin_embeddings/models/distilbert_v2",
    "generated-artifacts/onet_task_exposure.sqlite3",
]


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-manifest", action="store_true",
                        help="Explicit maintainer action: record approved assets; never run automatically.")
    args = parser.parse_args()
    if args.write_manifest:
        rows = []
        for name in PATHS:
            path = ROOT / name
            if not path.exists():
                raise SystemExit(f"Required runtime path missing: {name}")
            for file in sorted(path.rglob("*")) if path.is_dir() else [path]:
                if file.is_file():
                    rows.append({"path": file.relative_to(ROOT).as_posix(),
                                 "bytes": file.stat().st_size, "sha256": digest(file)})
        MANIFEST.write_text(json.dumps({"schema_version": 1, "files": rows}, indent=2) + "\n")
        print(f"Recorded {len(rows)} private runtime files; no weights copied into Git.")
        return
    rows = json.loads(MANIFEST.read_text())["files"]
    failures = []
    for row in rows:
        path = ROOT / row["path"]
        if not path.is_file():
            failures.append(f"Missing: {row['path']}")
        elif path.stat().st_size != row["bytes"] or digest(path) != row["sha256"]:
            failures.append(f"Checksum mismatch: {row['path']}")
    if failures:
        raise SystemExit("\n".join(failures))
    print(f"Verified {len(rows)} runtime files against SHA-256 manifest.")


if __name__ == "__main__":
    main()
