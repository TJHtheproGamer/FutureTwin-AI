# FutureTwin AI

FutureTwin AI monitors AI model benchmarks (Artificial Analysis API), detects capability changes between snapshots, and maps them to affected skills and occupations. It runs as a scheduled Python background job, not a website.

## Run & Operate

- `python3 futuretwin_embeddings/run_futuretwin.py` — run one full monitoring cycle: `ai_capability_tracker.py` (fetch latest benchmarks) → `ai_change_detector.py` (compare latest two snapshots in PostgreSQL) → `ai_impact_pipeline.py` (semantic skill/occupation matching with sentence-transformers)
- `python3 futuretwin_embeddings/futuretwin_impact_engine.py --compare | --demo Coding | --report Coding` — AI Advancement → Skill → Occupation impact engine (fine-tuned MiniLM + PostgreSQL + ESCO relations); `--demo` is a clearly-marked simulated scenario, `--report` only emits impact when a real comparable advancement exists
- `python3 futuretwin_embeddings/run_benchmark_collection.py` — multi-source benchmark collection (Artificial Analysis, SWE-bench, LiveBench; METR/OSWorld are local-only) into `benchmark_results` + frontier detection into `frontier_advancements`; per-source outcomes logged to `benchmark_collection_log`. AA free tier is 100 requests/day (daily reset) — collectors reuse same-day cache in `data/cache/`, degrade to stale copies on 429, and `collected_at` is always the true retrieval time (cache mtime), never stale-as-fresh
- `python3 futuretwin_embeddings/run_jobmarket_collection.py` — Phase 2 job-market collection (OpenDOSM Malaysia statistics + Remotive/Remote OK job ads) into `job_postings`/`job_posting_skills`/`jobmarket_stats`, with dedup by content hash and per-run coverage logging. Flags: `--source`, `--skip-skills`, `--skill-limit`. Also runs as guarded step 5 of `run_futuretwin.py` (all five steps are failure-isolated; a 429 or outage in one source never aborts the cycle). `.replit` sets `deploymentTarget = "scheduled"` running `run_futuretwin.py`, but no cron schedule is chosen and the project is not published — daily execution is NOT active until the user publishes with a schedule
- `pnpm --filter @workspace/api-server run dev` — run the API server (port 5000)
- `pnpm run typecheck` — full typecheck across all packages
- `pnpm --filter @workspace/api-spec run codegen` — regenerate API hooks and Zod schemas from the OpenAPI spec
- Required env: `DATABASE_URL` — Postgres connection string; `AA_API_KEY` — Artificial Analysis API key
- Python deps are managed with uv via root `pyproject.toml` (`uv sync` after changes)

## Deployment

- Deployment target: **scheduled** (`.replit` `[deployment]`, run = `python3 futuretwin_embeddings/run_futuretwin.py`)
- `artifacts/futuretwin` (kind `web`, preview path `/`) is the publishable application surface. In **development** its service runs the Flask Job Intelligence Dashboard (`futuretwin_embeddings/futuretwin_dashboard.py`, port 5000); in **production** it statically serves the single status page built from the React scaffold. The Publishing gate requires at least one deployable artifact kind (`web`); `api` and `design` kinds do not count, and artifact `kind` cannot be changed after creation
- The dashboard's frontend calls Flask routes registered on the futuretwin artifact's service `paths` (`/`, `/advancements`, `/benchmarks`, `/jobmarket`, `/api/advancements`, `/api/advancements/impact`, `/api/benchmarks/{sources,overview,results,frontier,skills}`, `/api/jobmarket/{overview,skill-trends,malaysia,ai-links}`) so the proxy routes them to Flask instead of the api-server's `/api` prefix (most-specific match wins). New dashboard pages or endpoints under `/api/` must be added to that `paths` array too
- AI Advancements page: `/advancements` (impact engine v1) — benchmark comparison table (observed) + capability selector + impact report (hypotheses). Live impact is refused when no comparable advancement exists; demo mode is always marked simulated
- Benchmark Intelligence page: `/benchmarks` (multi-source v1) — source connectors status, progress by domain, benchmark explorer with running-frontier chart, frontier advancements feed, benchmark-task → ESCO skill mapping (hypothesis). Frontier detection only compares dated results on the same benchmark version; unchanged snapshots are never treated as evidence of no progress
- Job Market page: `/jobmarket` (Phase 2) — source coverage/dedup tracking, rising/declining ESCO skill demand (absolute counts and ad-share kept separate), OpenDOSM Malaysia labour indicators, and AI frontier events juxtaposed with an explicit "co-occurrence is not causation" label. Job boards only expose their current listing window; ad history accumulates per collection run. No forecasting model until coverage is assessed as adequate
- `artifacts/api-server` production run also points at the Python pipeline as a fallback
- The cron schedule and timezone are chosen in the Publishing tool, not in config files
- Deployment secrets must include `AA_API_KEY`; production `DATABASE_URL` points to the production database provisioned from the dev database

## Stack

- pnpm workspaces, Node.js 24, TypeScript 5.9
- API: Express 5
- DB: PostgreSQL + Drizzle ORM
- Validation: Zod (`zod/v4`), `drizzle-zod`
- API codegen: Orval (from OpenAPI spec)
- Build: esbuild (CJS bundle)

## Where things live

_Populate as you build — short repo map plus pointers to the source-of-truth file for DB schema, API contracts, theme files, etc._

## Architecture decisions

_Populate as you build — non-obvious choices a reader couldn't infer from the code (3-5 bullets)._

## Product

_Describe the high-level user-facing capabilities of this app once they exist._

## User preferences

_Populate as you build — explicit user instructions worth remembering across sessions._

## Gotchas

_Populate as you build — sharp edges, "always run X before Y" rules._

## Pointers

- See the `pnpm-workspace` skill for workspace structure, TypeScript setup, and package details
