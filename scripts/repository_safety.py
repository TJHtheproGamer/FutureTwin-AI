#!/usr/bin/env python3
"""Redacted credential/history checks and a clean, no-history source export.

This never pushes, rewrites Git history, opens environment variables, or prints
credential values. Heuristics are not a guarantee that no secret ever existed.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GITHUB_EXPORT_EXCLUDED_PREFIXES = ("artifacts/", "attached_assets/")
RULES = {
    "provider-token": re.compile(rb"\b(?:sk-(?:proj-|ant-)?[A-Za-z0-9_-]{24,}|gh[pousr]_[A-Za-z0-9]{30,}|AIza[A-Za-z0-9_-]{30,})\b"),
    "private-key": re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "credential-url": re.compile(rb"(?:postgres(?:ql)?|mysql|mongodb(?:\+srv)?)://[^/\s:@]+:([^@\s/]+)@"),
    "literal-credential": re.compile(
        rb"""(?im)^\s*(?:[A-Z_]*API_KEY|[A-Z_]*SECRET|[A-Z_]*PASSWORD|[A-Z_]*ACCESS_TOKEN)\s*=\s*["']([^"'\n]{12,})["']"""),
}
PLACEHOLDERS = re.compile(
    rb"(?i)(replace|placeholder|example|your[_ -]|dummy|test|synthetic|change|db_password|secret.for|optional.free|fake)")


def files() -> list[Path]:
    # Never discover the Replit workspace's parent Git repository from an export.
    if not (ROOT / ".git").exists():
        excluded = {".git", "node_modules", ".venv", ".pythonlibs", "__pycache__"}
        return sorted(p for p in ROOT.rglob("*")
                      if p.is_file() and not p.is_symlink()
                      and not excluded.intersection(p.relative_to(ROOT).parts))
    output = subprocess.check_output(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"], cwd=ROOT)
    return sorted({ROOT / p.decode() for p in output.split(b"\0")
                   if p and (ROOT / p.decode()).is_file()})


def github_export_files() -> list[Path]:
    return [
        path for path in files()
        if not path.relative_to(ROOT).as_posix().startswith(
            GITHUB_EXPORT_EXCLUDED_PREFIXES
        )
    ]


def detect(data: bytes, path: str) -> list[dict]:
    if b"\0" in data[:8192]:
        return []
    findings = []
    for rule, pattern in RULES.items():
        for match in pattern.finditer(data):
            value = match.group(1) if match.lastindex else match.group()
            if PLACEHOLDERS.search(value):
                continue
            findings.append({"path": path, "line": data[:match.start()].count(b"\n") + 1,
                             "rule": rule, "value": "[REDACTED]"})
    return findings


def current_scan() -> dict:
    findings, oversized, private_files, pointers = [], [], [], []
    for path in files():
        relative = path.relative_to(ROOT).as_posix()
        if (path.name == ".env" or
                (path.name.startswith(".env.") and path.name != ".env.example") or
                path.suffix.lower() in {
                    ".zip", ".tar", ".safetensors", ".bin", ".pt", ".pth",
                    ".onnx", ".sqlite", ".sqlite3", ".db", ".pem", ".key",
                } or any(part in {"uploads", "resumes", "private", ".agents"}
                         for part in path.relative_to(ROOT).parts)):
            private_files.append(relative)
        if path.stat().st_size >= 100 * 1024 * 1024:
            oversized.append({"path": relative, "bytes": path.stat().st_size})
        if path.stat().st_size <= 64 * 1024 * 1024:
            data = path.read_bytes()
            if data.startswith(b"version https://git-lfs.github.com/spec/v1"):
                pointers.append(relative)
            findings.extend(detect(data, relative))
    return {"credential_candidates": findings, "oversized_files": oversized,
            "private_file_candidates": private_files, "lfs_pointers": pointers,
            "symlinks": [p.relative_to(ROOT).as_posix() for p in ROOT.rglob("*")
                         if p.is_symlink()],
            "scope": "This repository root only; standalone exports do not use parent Git history. Text patterns checked up to 64 MiB; binary contents are not exhaustively audited."}


def history_scan() -> dict:
    if not (ROOT / ".git").exists():
        return {"status": "not_applicable", "reason": "No Git metadata in this export; parent history is deliberately not inspected."}
    objects = subprocess.check_output(["git", "rev-list", "--objects", "--all"], cwd=ROOT).splitlines()
    mapping = {}
    for row in objects:
        parts = row.decode(errors="replace").split(" ", 1)
        if len(parts) == 2:
            mapping.setdefault(parts[0], parts[1])
    inventory = subprocess.run(
        ["git", "cat-file", "--batch-check=%(objectname) %(objecttype) %(objectsize)"],
        input=("\n".join(mapping) + "\n").encode(), capture_output=True, check=True, cwd=ROOT)
    findings, oversized, count = [], [], 0
    reader = subprocess.Popen(["git", "cat-file", "--batch"], stdin=subprocess.PIPE,
                              stdout=subprocess.PIPE, cwd=ROOT)
    try:
        for line in inventory.stdout.decode().splitlines():
            oid, kind, size = line.split()
            size = int(size)
            if kind != "blob":
                continue
            count += 1
            if size >= 100 * 1024 * 1024:
                oversized.append({"object": oid, "path": mapping[oid], "bytes": size})
            if size > 5 * 1024 * 1024:
                continue
            reader.stdin.write((oid + "\n").encode())
            reader.stdin.flush()
            header = reader.stdout.readline().split()
            actual_size = int(header[2])
            data = reader.stdout.read(actual_size)
            reader.stdout.read(1)
            for candidate in detect(data, mapping[oid]):
                candidate["object"] = oid
                findings.append(candidate)
    finally:
        reader.stdin.close()
        reader.wait()
    return {"blobs_checked": count, "credential_candidates": findings,
            "oversized_history": oversized,
            "limitations": "Pattern-based text scan <=5 MiB per blob; binary/archive contents not credential-audited."}


def overview(paths: list[Path] | None = None, output: Path | None = None) -> None:
    paths = files() if paths is None else paths
    sources = [p for p in paths if p.suffix in {".py", ".ts", ".tsx", ".js", ".mjs", ".cjs", ".sh", ".sql"}]
    py = {}
    for path in sources:
        if path.suffix == ".py":
            tree = ast.parse(path.read_text())
            imports = set()
            for n in ast.walk(tree):
                if isinstance(n, ast.Import):
                    imports.update(a.name.split(".")[0] for a in n.names)
                elif isinstance(n, ast.ImportFrom) and n.module:
                    imports.add(n.module.split(".")[0])
            py[path.stem] = (path, tree, imports)
    runtime, pending = set(), ["futuretwin_dashboard", "futuretwin_skill_api"]
    while pending:
        name = pending.pop()
        if name in runtime or name not in py:
            continue
        runtime.add(name)
        pending.extend(py[name][2])
    lines = [
        "# Codebase overview", "",
        "Generated by `python scripts/repository_safety.py --overview`; review alongside README and docs/final-review.md.", "",
        "## Architecture", "",
        "- Flask entry point: `futuretwin_embeddings/futuretwin_dashboard.py`; shared app/index in `futuretwin_skill_api.py`.",
        "- Pages are Python-held HTML, CSS and vanilla JavaScript. Replit artifact wrappers provide preview routing and separate API/design services; the GitHub source export omits those Replit-only files.",
        "- PostgreSQL stores encrypted cookie-owned profiles, benchmark/job history and SDG snapshots. SQL migrations and collectors are maintenance entry points.",
        "- Local MiniLM proposes ESCO identities; local DistilBERT classifies O*NET task wording. Neither means demonstrated competence or job-loss probability.",
        "- Resume/experience extraction is conservative local vocabulary/span matching, followed by local MiniLM and explicit user review.",
        "- Best Match uses skill compatibility, task exposure and compatible benchmark evidence only. Purpose preferences/SDG discovery are separate.",
        "- Profile ownership is browser-session based. There is no account login, registration, SSO or cross-device recovery.", "",
        "## Every retained source file", "",
        "Static runtime reachability is indicative, not proof that a file is disposable. CLI jobs, migrations, tests and optional design tooling are retained for maintenance.", "",
        "| File | Purpose | Use / decision | Local dependencies / entry points |",
        "|---|---|---|---|",
    ]
    def safe(s: str) -> str:
        return s.replace("|", "/").replace("\n", " ")[:850]
    for path in sources:
        rel = path.relative_to(ROOT).as_posix()
        text = path.read_text(errors="replace")
        if path.suffix == ".py":
            _, tree, imports = py[path.stem]
            purpose = {
                "ai_capability_tracker": "Collect free Artificial Analysis benchmark measurements into snapshots and PostgreSQL; scheduled job stage.",
                "ai_change_detector": "Compare stored benchmark snapshots and record measured capability changes; scheduled job stage.",
                "ai_impact_pipeline": "Scheduled semantic overlap mapping from measured advancement wording to ESCO skills/occupations; explicit --demo stays separate from real evidence.",
                "prepare_training_data": "Reproduce the ESCO embedding skill catalog and train/validation/test pair inputs; retained preprocessing, not run during cleanup.",
                "run_futuretwin": "Scheduled collector entry point; runs benchmark tracking, change detection and overlap pipeline in order.",
            }.get(path.stem) or (ast.get_docstring(tree) or "").split("\n")[0]
            functions = [n.name for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))]
            local = sorted(n for n in imports if n in py)
            if "/tests/" in rel:
                usage = "Regression test — KEEP"
                purpose = purpose or "Checks " + ", ".join(functions[:6])
            elif path.stem in runtime:
                usage = "Website runtime (static import path) — KEEP"
            else:
                usage = "Offline/maintenance entry point — KEEP; not a direct page dependency"
            purpose = purpose or "Maintenance logic: " + ", ".join(functions[:6])
            deps = ", ".join(local) or "Standard/third-party libraries; see import statements"
            if functions:
                deps += "; defines " + ", ".join(functions[:8])
        elif path.suffix == ".sql":
            purpose, usage, deps = "Explicit PostgreSQL schema migration; preserve existing records", "Maintenance — KEEP", "PostgreSQL; inspect before applying"
        elif path.suffix == ".sh":
            purpose, usage, deps = "Replit maintenance hook / shell entry point", "Maintenance — KEEP", "Commands in script; no automatic schema push"
        else:
            imports = re.findall(r"""(?:from\s+|require\()["']([^"']+)""", text)
            exports = re.findall(r"export\s+(?:async\s+)?(?:function|class|const)\s+(\w+)", text)
            purpose = ("Regression test: " if "/tests/" in rel else "Optional Replit workspace module: ") + path.stem
            if exports:
                purpose += "; exports " + ", ".join(exports[:6])
            usage = "Test/tooling — KEEP" if "/tests/" in rel else "Registered artifact / shared tooling — KEEP (not Flask runtime)"
            deps = ", ".join(sorted(set(imports))) or "See workspace dependency configuration"
        lines.append(f"| `{rel}` | {safe(purpose)} | {usage} | {safe(deps)} |")
    lines += ["", "## Every other retained repository file", "",
              "Data histories, model-provenance documents and migration inputs are retained even when not directly imported. Private assets/inputs excluded from Git remain on disk and in the protected backup.", "",
              "| Path | Bytes | Role / decision |", "|---|---:|---|"]
    for path in paths:
        if path in sources:
            continue
        rel = path.relative_to(ROOT).as_posix()
        if "/data/" in rel or path.suffix in {".csv", ".gz"}:
            role = "Runtime/source data, history or reproducibility input — KEEP"
        elif path.suffix in {".md", ".txt"}:
            role = "Documentation/provenance — KEEP"
        elif path.suffix in {".json", ".toml", ".yaml", ".yml"} or path.name.startswith("."):
            role = "Dependency/build/artifact configuration — KEEP"
        else:
            role = "Frontend/supporting source asset — KEEP"
        lines.append(f"| `{rel}` | {path.stat().st_size} | {role} |")
    (output or ROOT / "CODEBASE_OVERVIEW.md").write_text("\n".join(lines) + "\n")


def export(destination: Path) -> dict:
    report = current_scan()
    if (report["credential_candidates"] or report["oversized_files"]
            or report["private_file_candidates"] or report["lfs_pointers"]
            or report["symlinks"]):
        raise SystemExit("Export blocked: resolve redacted source-scan findings first.")
    if destination.exists():
        raise SystemExit("Destination exists; choose a new path rather than overwrite it.")
    destination.mkdir(parents=True)
    copied = 0
    export_paths = github_export_files()
    for path in export_paths:
        rel = path.relative_to(ROOT)
        target = destination / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
        copied += 1
    overview(paths=export_paths, output=destination / "CODEBASE_OVERVIEW.md")
    return {"export": str(destination.relative_to(ROOT)), "files": copied,
            "excluded": ["artifacts/", "attached_assets/"],
            "note": "Replit-only artifacts and user-uploaded assets remain in the workspace and are omitted from this GitHub source export. No .git directory, private inputs, user databases or checkpoint weights copied."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--history", action="store_true")
    parser.add_argument("--overview", action="store_true")
    parser.add_argument("--export", type=Path)
    args = parser.parse_args()
    if args.overview:
        overview()
    report = {"current": current_scan()}
    if args.history:
        report["history"] = history_scan()
    if args.export:
        report["export"] = export(args.export.resolve())
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
