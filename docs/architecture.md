# FutureTwin AI architecture

## Runtime at a glance

FutureTwin's career and workforce-intelligence pages are served by a Python
**Flask** application. The Replit `artifacts/futuretwin: web` development
workflow starts `futuretwin_embeddings/futuretwin_dashboard.py`, which
registers the page and API modules on one shared Flask application. Most of the
Flask preview's HTML, CSS and browser JavaScript is assembled by Python page
modules.

```text
Browser
  └── Flask pages and JSON APIs
        ├── PostgreSQL: encrypted browser-owned career profiles,
        │   benchmark history, job sample records and SDG-map snapshots
        ├── Local ESCO / O*NET catalogues and reviewed source data
        ├── Local MiniLM: semantic candidate retrieval
        ├── Local DistilBERT V2: task-label inference (CPU)
        ├── Local SQLite: task-prediction cache and O*NET task inventory
        └── Public feeds: scheduled benchmark/job collection or an explicit
            manual refresh

Replit development preview (`artifacts/futuretwin`)
  └── Flask dashboard on port 5000

Legacy root Replit configuration (`.replit`, target = scheduled)
  └── run_futuretwin.py → benchmark/job collection, change detection and
      historical semantic-overlap pipeline; not a website server

Original workspace artifact's prepared production service (not exported)
  └── uv sync → Gunicorn → Flask; not yet published

Optional manual Flask process
  └── Procfile → Gunicorn → futuretwin_dashboard:app
```

The exported `.replit` retains legacy scheduled-collector metadata and does not
start a website. This does not prove an active schedule. In the original Replit
workspace, the FutureTwin artifact now has a validated production build
(`uv sync --frozen --no-dev`) and a Gunicorn process command; the former static
React/Vite production definition was replaced during publishing preparation.
The user must select Autoscale in Publishing if publication is later approved.
No published deployment exists at this review.

The `artifacts/` manifests are intentionally absent from this GitHub export.
The export's Flask application imports and runs independently of them, using
the README commands or root `Procfile`. This export is a separately reviewed
source snapshot, not an automatic mirror of every subsequent workspace edit.
Do not assume that unpublished workspace-only demo/authentication changes
are present here. Its profile ownership is still browser-cookie based.

The workspace also defines separate `artifacts/api-server` and
`artifacts/mockup-sandbox` workflows. They are workspace services and are not
part of the FutureTwin Flask request path. The Vite artifact scaffold is
retained for Replit tooling; the development preview's career pages and APIs
come from Flask.

## Website and application flows

- `futuretwin_dashboard.py`, `futuretwin_site_ui.py` and `futuretwin_pages.py`
  provide Home, Career, My Profile, My Future, Purpose, SDG Map, Trends and
  benchmark-advancement pages.
- `futuretwin_skill_api.py`, `futuretwin_resume_api.py` and
  `futuretwin_experience_api.py` process user-selected ESCO skills, consented
  resume input and experience evidence. Resume/experience extraction is local,
  conservative and review-first; confirmed skills are never inferred silently.
- `futuretwin_my_future.py` and its page modules load saved preferences,
  explain career matches, build learning plans and show practice activities.
  Best Match has three configured score components, not four: skill
  compatibility, AI task exposure and AI benchmark evidence. Purpose alignment
  is not a component and saved SDG priorities do not affect the score.
- `futuretwin_sdg.py`, `futuretwin_sdg_api.py` and
  `futuretwin_sdg_map_page.py` expose separately sourced SDG-to-career/skill
  candidate and reviewed links. A link is not proof of occupational impact.

Profile ownership is tied to the browser cookie; there is no user-account
login, registration or cross-device recovery in this codebase.

## Best Match score implementation

`futuretwin_embeddings/data/best_match_config.json` configures the three score
components at 65% skill compatibility, 25% AI task exposure and 10% AI
benchmark evidence. The same file marks benchmark scoring disabled and calls
these initial, not empirically validated design weights. The ranking code
reports benchmark evidence as unavailable, so it currently adds no points.
When skill and task-exposure evidence are both available, their configured
weights are renormalized over those two components; if one is unavailable, only
supported components contribute. Comparisons remain within groups with the
same scored components.

Within skill compatibility, essential and optional ESCO-list coverage are
weighted 70% and 30% when both lists are available. After the component score,
ordering uses tie-breakers such as essential matches, total confirmed matches,
interest-text matches, listed-skill coverage, title and occupation URI. These
are not additional weighted score components. Purpose preferences are ignored
by the Best Match score.

## Models and career evidence

### MiniLM

The custom sentence-transformer checkpoint under
`futuretwin_embeddings/models/futuretwin_minilm/` runs locally and retrieves
semantic ESCO candidates. `futuretwin_embeddings/futuretwin_local_extraction.py`
extracts literal skill mentions and activity spans from consented text; MiniLM
helps map suggestions to ESCO labels. Similarity is not proof that a person
holds a skill. The checkpoint and its checksum are listed in
`runtime-assets.json`, not in the public GitHub export.

### DistilBERT V2 and O*NET

`futuretwin_embeddings/futuretwin_distilbert.py` loads the custom DistilBERT
checkpoint locally with CPU inference and strict checkpoint/provenance checks.
`futuretwin_embeddings/futuretwin_task_exposure.py` maps O*NET task records and
reports E0/E1/E2 results. It is not a serverless endpoint. The private checkpoint
and precomputed task inventory are provisioned separately using
`RUNTIME_ASSETS.md` and `scripts/check_runtime_assets.py`.

### RunPod

The project owner reports that RunPod was used to train MiniLM and DistilBERT.
The repository documents available model-card and package settings, but does
not include the model-training scripts or RunPod job logs needed to
independently verify those runs. No RunPod Serverless handler or inference
endpoint is used; website inference is local. See
[RunPod training notes](../runpod/README.md) for recorded settings, results and
evidence limits.

### ESCO

ESCO provides the occupation/skill catalogue and exact relations used for
matching. Career compatibility and evidence labels are distinct from hiring
outcomes and professional competency assessments. Source versions and
attribution must remain visible.

## AI-capability benchmark history

`benchmark_collectors.py`, `benchmark_registry.py` and `benchmark_store.py`
fetch and preserve source-attributed public benchmark observations when their
collection command is run. `ai_capability_tracker.py` aggregates measurements;
`ai_change_detector.py` compares observations. These are benchmark records,
not measurements of FutureTwin's own model or predictions of occupation loss.
`ai_impact_pipeline.py` is a separate historical semantic-overlap analysis.
Its overlap counts do not verify an advancement's real-world impact.

## Job postings

`jobmarket_registry.py`, the provider adapters, `jobmarket_store.py` and the
My Future APIs combine public job-posting samples with locally stored retrieval
and filtering. Availability is source- and time-dependent. Broad labor-market
statistics are not exact-occupation vacancy counts or guaranteed hiring demand.
Respect each provider's terms, rate limits, links and attribution.

## SDG map

SDG data separates goal/indicator sources, catalogue associations, AI-suggested
candidate links and their review status. PostgreSQL stores refreshable map
snapshots; local source files and explicit migrations document how to rebuild
them. A country indicator or skill association alone does not prove that a
specific job creates measured SDG impact.

## Data and security boundaries

- PostgreSQL connection strings and the stable `SESSION_SECRET` are provided
  through the hosting secret store. The public source export has no database
  dump, `.env` file, checkpoint weights, or user profile data.
- The exact private runtime assets and checksums are documented in
  `RUNTIME_ASSETS.md`. Restore them only from an authorized source. Do not upload
  model archives or credentials to a public repository.
- Model inference is local. Optional benchmark/job-source collection makes
  outbound requests only when an operator starts those collection workflows.
- SQL migrations are under `futuretwin_embeddings/migrations/`. The unrelated
  Drizzle workspace schema is not the Flask app's database schema.

For exact file purposes and local imports, see
[`CODEBASE_OVERVIEW.md`](../CODEBASE_OVERVIEW.md).
