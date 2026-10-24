# FutureTwin AI — SDC Hackathon 2026

## Project name and description

**FutureTwin AI** is a career-exploration and planning website. It helps people
review skills, explore occupations, compare evidence about AI-related task
exposure, browse job postings, and discover possible connections between skills,
careers, and the UN Sustainable Development Goals (SDGs). It is not a job-loss
probability or a professional assessment.

> **Public-release hold:** Do not push the prepared export yet. Redistribution
> rights for the included Artificial Analysis snapshots are unresolved, the
> exact SDG API V5 and crosswalk-specific terms still need confirmation, and
> this repository has no project-wide code license. See
> [the licensing review](docs/data-licensing.md).

## Team information and assigned domain

| Item | Status |
|---|---|
| Registered team name | **LM10** |
| Official assigned domain | **Pending organizer confirmation** |

The application is about career and workforce exploration. That description is
not a substitute for the event's official domain assignment.

## SDG track

**Official SDC SDG-track assignment: pending organizer confirmation.** The
product's SDG Map currently covers all 17 UN goals. Its latest reviewed map
snapshot contained 103 occupation nodes and 204 skill nodes; these are
snapshot-specific counts, not the event's assigned SDG track.

## Project links

| Destination | Verified link or status |
|---|---|
| GitHub repository | **Pending** — no public GitHub repository URL is configured or verified in this checkout. |
| Replit development preview | [Open the current preview](https://359f65d7-70f8-4fd4-85c3-0260a9179025-00-wqe0xe7y3wkj.sisko.replit.dev/) — temporary workspace preview, not a published production website. |
| Replit project page / stable deployment | **Pending** — provide the stable project or deployment URL if the organizer requires one. |
| RunPod training record | **Pending** — no RunPod job URL or account activity record is in the repository. |
| RunPod inference endpoint | **None** — website inference is local; no endpoint is claimed. |
| Slide deck | **Pending** — no deck or verified URL was supplied. |
| Demo video | **Pending** — no video or verified URL was supplied. |

The development preview returned HTTP 200 for `/`, `/career`, `/my-future`, and
`/sdg-map` during this preparation. A temporary preview URL may expire or
change.

## Problem and solution

Career decisions are difficult when skills evidence, occupation information,
job listings, and AI-related research are separated or presented as confident
forecasts. FutureTwin brings those sources into one exploratory workflow. It
shows which evidence supports a match, where data is missing, and which
connections are suggestions rather than reviewed findings.

## Key features

- **Skills Passport:** review and confirm ESCO-linked skills from manual entry
  or local resume/experience text extraction.
- **Career exploration and My Future:** occupation details, skill compatibility,
  learning plans, saved careers, and explainable Best Match ordering.
- **Experience practice:** locally authored illustrative activities with
  feedback. They are not competence grades and do not confirm Passport skills.
- **AI evidence:** local DistilBERT task labels, source-bound provenance, and
  benchmark history. Task counts are not job-loss probabilities.
- **Job evidence:** source-attributed public postings and broad labour-market
  context. Listings are an incomplete sample, not total hiring demand.
- **SDG Map:** explore goal, occupation, and skill associations while keeping
  unreviewed suggestions distinct from desk-reviewed and independently approved
  links.

## Technology stack

- Python 3.11, Flask, HTML, CSS, and vanilla JavaScript for the website.
- PostgreSQL 16 for encrypted browser-owned profiles and collected history.
- `uv` and `uv.lock` for Python dependency management.
- PyTorch, Transformers, and Sentence Transformers for local MiniLM and
  DistilBERT inference. DistilBERT task inference is CPU-only.
- pypdf and python-docx for supported document extraction; optional local
  faster-whisper for speech transcription.
- Replit workspace tooling also includes pnpm/TypeScript scaffolding. That
  scaffold is not the Flask website.

No paid inference API was added. The optional `AA_API_KEY` is for the existing
Artificial Analysis measurement feed used by the scheduled collector, not for
website inference.

## Actual project structure

```text
.
├── futuretwin_embeddings/
│   ├── futuretwin_dashboard.py   # Flask application entry point
│   ├── data/                     # source data, provenance, and research snapshots
│   ├── migrations/               # PostgreSQL schema migrations
│   ├── tests/                    # Python and browser-lifecycle regression tests
│   ├── prepare_training_data.py  # MiniLM pair preparation, not model training
│   └── run_futuretwin.py         # scheduled monitoring/collection cycle
├── docs/                         # architecture, screenshots, licensing notes
├── runpod/                       # RunPod training evidence limits; no endpoint code
├── scripts/                      # repository checks and runtime-asset validation
├── submission/                   # SDC status and proof-of-use preparation
├── lib/                          # optional pnpm workspace packages
├── .env.example                  # placeholders only
├── .replit                       # scheduled collector configuration
├── Procfile                      # Gunicorn command; not a Replit deployment
├── pyproject.toml
└── uv.lock
```

The original Replit workspace also has `artifacts/`; it is intentionally omitted
from the clean GitHub source export. Private model files and the required
precomputed task inventory remain in the workspace but are not in the export.
No `src/main.py` replacement was made; the real Flask entry point is retained.

## System architecture

The Flask app serves pages and APIs, reads/writes PostgreSQL-backed records, and
loads MiniLM and DistilBERT from locally provisioned files. ESCO, O*NET, DOSM,
and SDG source data support separate product areas. Benchmark and job-market
collection run as data-refresh work, not as a RunPod inference service.

See [the architecture and data-flow notes](docs/architecture.md) for the
Replit-specific service definitions and evidence limits.

## How to run on Replit and locally

### Replit development preview

In the original Replit workspace, use the existing **`artifacts/futuretwin:
web`** workflow. Its working directory is `artifacts/futuretwin`; its command is:

```bash
python3 -u ../../futuretwin_embeddings/futuretwin_dashboard.py
```

It serves the Flask preview on port `5000`. The workspace uses Python 3.11 and
PostgreSQL 16. Set `DATABASE_URL` and `SESSION_SECRET` through Replit Secrets,
and provision the private runtime assets described below before using
model-backed features.

Important: the exported `.replit` retains legacy **scheduled collector**
metadata; it is not a web startup command. The original workspace's FutureTwin
artifact has since been prepared to run Flask/Gunicorn in production, rather
than static React. Artifact files are intentionally absent from this export.
Use the standalone commands below. Select Autoscale in Replit's Publishing
settings only if publishing is approved. No production website is verified
or published by this preparation.

### Local installation

Requirements: Python 3.11, `uv`, and PostgreSQL 16. `antiword` is only needed
for legacy `.doc` files. Node.js/pnpm are optional workspace tooling and are not
required to run the Flask website.

Install `uv` using its
[official installation guide](https://docs.astral.sh/uv/getting-started/installation/).
Replace the pending GitHub URL only after the project owner supplies the
verified repository address:

```bash
git clone "<GITHUB_REPOSITORY_URL>" futuretwin
cd futuretwin
uv sync --frozen
```

`uv.lock` pins the current dependency set. Do not silently replace the pinned
PyTorch build: stored task predictions are tied to that runtime provenance.

### Environment variables

Use Replit Secrets in Replit. Locally, copy `.env.example` to `.env`, replace
the placeholders, then source it in the shell. The application does not
automatically load `.env`.

| Variable | Placeholder | Use |
|---|---|---|
| `DATABASE_URL` | `postgresql://DB_USER:DB_PASSWORD@DB_HOST:5432/DB_NAME` | PostgreSQL connection. |
| `SESSION_SECRET` | `REPLACE_WITH_A_SECURE_RANDOM_VALUE` | Required for encrypted profile operations and session ownership. Keep the original value for existing encrypted profiles. |
| `PORT` | `5000` | Optional local web port; defaults to 5000. |
| `AA_API_KEY` | `OPTIONAL_FREE_FEED_KEY` | Optional for the web UI; used by the scheduled Artificial Analysis tracker. |
| `FUTURETWIN_WHISPER_MODEL` | `small` | Optional local faster-whisper model name or path. |
| `REPLIT_DEPLOYMENT_ID` | `SET_BY_REPLIT` | Replit-provided setting; do not set manually. |

Never put real credentials in this README or commit `.env`.

For a local shell, create the ignored `.env`, edit its placeholders privately,
then load it for the current shell:

```bash
cp .env.example .env
# Edit .env locally; keep the real values out of Git and chat.
set -a
. ./.env
set +a
```

For a new profile store, generate a `SESSION_SECRET` once and save it in the
local secret store. Do not replace the key for an existing encrypted database:

```bash
python3 -c 'import secrets; print(secrets.token_urlsafe(48))'
```

### PostgreSQL setup

Create a PostgreSQL 16 database and a least-privilege role. These commands ask
for the password interactively:

```bash
createuser --pwprompt futuretwin_app
createdb --owner=futuretwin_app futuretwin
```

Set `DATABASE_URL` to the new database, then apply the checked-in migrations:

```bash
psql "$DATABASE_URL" -v ON_ERROR_STOP=1 \
  -f futuretwin_embeddings/migrations/001_career_profiles.sql
psql "$DATABASE_URL" -v ON_ERROR_STOP=1 \
  -f futuretwin_embeddings/migrations/002_sdg_map_snapshots.sql
```

These create profile and SDG snapshot tables; they do not seed private records.
Initialize empty public-data tables without contacting feeds:

```bash
(cd futuretwin_embeddings && uv run --frozen python - <<'PY'
import os
import psycopg
import benchmark_store
import jobmarket_store
with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
    benchmark_store.ensure_schema(conn)
    jobmarket_store.ensure_schema(conn)
    conn.commit()
PY
)
```

These tables initially contain no job or benchmark history. The source export
does not contain a PostgreSQL backup. Collectors can populate the public tables
when intentionally run. Run collectors
only when you intend to make external requests and write new history. Do not
drop or reset an existing database, and do not run the unrelated scaffold's
`pnpm --filter db push`.

### Provision private model files

MiniLM and DistilBERT inference run locally. The custom checkpoints and the
precomputed O*NET/ESCO task inventory are excluded from GitHub. Obtain the
authorized model-only archive and its SHA-256 checksum from the maintainer
through an access-controlled channel; verify the checksum through a separate
trusted channel before extraction:

```bash
sha256sum /secure/path/futuretwin-runtime-assets.tar
tar -tf /secure/path/futuretwin-runtime-assets.tar
tar -xf /secure/path/futuretwin-runtime-assets.tar -C /path/to/futuretwin
cd /path/to/futuretwin
python scripts/check_runtime_assets.py
```

See [runtime asset requirements](RUNTIME_ASSETS.md) for exact paths and
provenance. There is no public model download URL. Without those private assets,
a clean clone cannot run all model-backed features. Do not commit weights,
archives, databases, or real profiles.

### Initialize the SDG Map snapshot

After migrations and model provisioning, generate the map into the **new demo
database**. The table migration alone does not populate it. This command skips
an existing snapshot rather than replacing it:

```bash
(cd futuretwin_embeddings && uv run --frozen python - <<'PY'
from futuretwin_sdg_map import build_map_snapshot, read_map_snapshot, save_map_snapshot
if read_map_snapshot() is None:
    save_map_snapshot(build_map_snapshot())
else:
    print("Existing SDG snapshot preserved.")
PY
)
```

No external inference service is called. In the independent export test this
produced 307 nodes: 103 occupations and 204 skills across 17 goals.

### Start the website and run regression tests

From the repository root, after environment setup, migrations, and asset
provisioning:

```bash
uv run python -u futuretwin_embeddings/futuretwin_dashboard.py
```

Open `http://127.0.0.1:5000/`. The Flask app uses `PORT` if set. The exact Python
regression command is:

```bash
(cd futuretwin_embeddings && uv run --frozen python -m unittest discover -s tests -v)
```

The separate voice-recording lifecycle tests are:

```bash
node --test futuretwin_embeddings/tests/test_voice_recording.cjs
```

For production-style local serving, run from the repository root:

```bash
uv run --frozen gunicorn --chdir futuretwin_embeddings \
  --bind "0.0.0.0:${PORT:-5000}" --workers 1 --threads 4 \
  --timeout 180 futuretwin_dashboard:app
```

On 2026-10-24, an independent temporary copy of **this export**, outside the
Replit workspace and without `artifacts/`, passed **238 Python tests** and
**8 Node tests** after the 21 private runtime files were provisioned and
checksum-verified. Without those files, the Python suite did not pass
(4 failures, 2 errors, 7 skipped); this is not a self-contained clone.
Dependencies were reused from the current Python installation, not installed
on a clean operating system. Fresh-database integration passed using an
isolated local PostgreSQL **17.5** test instance; the requested PostgreSQL 16
version was not separately tested. No development records were copied.
See [the final review](docs/final-review.md).

There is no account authentication in this exported version. Browser-cookie
ownership is not a login system. Do not expose private profile editing publicly
without a separately reviewed authentication or read-only demo configuration.

## How we use Replit

Replit is the development workspace for the Flask preview and PostgreSQL-backed
application data. The root configuration contains legacy scheduled-collector
metadata; it does not prove an active schedule. The original workspace's
FutureTwin artifact is now prepared for Flask/Gunicorn production serving, but
publishing and production database setup remain unverified and unapproved.
See [submission evidence status](submission/evidence/replit-proof-of-use.md);
repository configuration and a working preview do not prove account ownership
or a published site.

## How we use RunPod

The project owner reports using RunPod to train MiniLM and DistilBERT. The
repository includes MiniLM pair preparation and model-card-reported settings,
plus DistilBERT v2 manifest settings and evaluation summaries. The actual
training scripts and provider job logs are absent, so the provider activity,
hardware, and results cannot be independently verified from this checkout.

The available records report:

- **MiniLM:** base `all-MiniLM-L6-v2`; 53,700 ESCO-derived training pairs;
  model-card settings of 2 epochs, batch size 16, and learning rate `2e-5`.
  The model card reports 8.7 minutes, but no trainer script or RunPod log
  verifies that duration or hardware.
- **DistilBERT v2:** base `distilbert-base-uncased`; package manifest records
  3 epochs, batch size 16, learning rate `2e-5`, seed 42, and max length 160.
  Its packaged evaluation summary reports 84.12% accuracy and 81.58% macro F1
  on 2,746 test examples; the test rows and RunPod job are not independently
  available here.

FutureTwin does **not** use a RunPod Serverless handler or inference endpoint.
Both models load locally; DistilBERT task inference is CPU-only. See
[`runpod/README.md`](runpod/README.md) and
[RunPod proof status](submission/evidence/runpod-proof-of-use.md).

## Challenges and learnings

- Keep task-label counts distinct from work hours, automation feasibility, or
  job-loss probabilities.
- Preserve model, data, and evaluation provenance; a model card is not a
  provider log or a reproducible training script.
- Keep candidate SDG links separate from desk review and independent human
  approval; candidate similarity is not measured social impact.
- Job-board samples and broad national statistics cannot be presented as
  complete, exact-occupation hiring demand.
- Local model files keep inference on-device/server-side, but secure provisioning
  and compatible runtime assets are required for a fresh demo environment.

## Future improvements

- Add reproducible trainer scripts, exact dataset splits, and authorized
  RunPod job logs for both model families.
- Resolve third-party redistribution terms for the included benchmark snapshots
  and confirm the SDG API V5 reuse terms before public release.
- Add independent review and broader evidence for SDG occupation/skill links.
- Provide a privacy-safe, authorized demonstration asset bundle and a stable
  judge-facing Replit URL only after deployment configuration is approved.
- Confirm the official SDC domain, SDG track, required PDFs, and team roster.

## Team members

**Team:** LM10

**Member names and roles:** pending confirmation from the team. No names or
roles have been inferred.

## Submission checklist

The section structure matches the list supplied by the team. Exact official
template/PDF compliance is still pending the organizer's original files.

- [x] README follows the supplied SDC section list and uses verified
      FutureTwin architecture and commands.
- [x] Existing Flask structure and regression tests preserved.
- [x] Current Replit preview routes and existing regression suites verified.
- [x] Credential and privacy scans completed; no findings were reported.
- [x] 21 current runtime files verified against the private asset SHA-256
      manifest; those files are not included in the clean export.
- [x] Private model archives, profiles, and uploaded assets are excluded from the
      clean GitHub source export.
- [x] Replit and RunPod evidence-status documents prepared without fabricated
      screenshots, logs, signatures, or endpoints.
- [ ] Confirm the official assigned domain, SDG track, team member names, and
      roles.
- [ ] Supply and verify the public GitHub URL, stable Replit project/deployment
      URL, RunPod training record, slide link, and video link.
- [ ] Supply official PDF names/templates and complete only genuine required
      forms. No official PDFs or signatures were supplied or created.
- [ ] Resolve the public redistribution status of the included Artificial
      Analysis snapshots, confirm SDG API V5 and crosswalk-specific terms, and
      choose a project code license before public release. See
      [data licensing review](docs/data-licensing.md).
- [ ] Provision private checkpoints and database for a judge's full live demo.

## Third-party data and code licensing

See [the source-by-source licensing review](docs/data-licensing.md). The current
clean export is security-scanned, but it is **not cleared for public
redistribution** until the listed dataset and project-code licensing items are
resolved. No files were deleted and no paid license or service was obtained.
