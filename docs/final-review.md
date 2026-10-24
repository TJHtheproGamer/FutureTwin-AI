# Final SDC repository review

Reviewed 2026-10-24. Repository root: `generated-artifacts/github-source/`
in the original workspace, **not the entire Replit workspace**.

## Verdict

**Technically prepared and independently tested with provisioned assets, but
not ready for public release or a complete SDC submission.** The outstanding
licensing, official forms, links, and team details below must be resolved.
Nothing was pushed or published and no paid service was activated.

## Repository and template checks

| Item | Result |
|---|---|
| README structure | Contains every section in the team's supplied section list. Exact organizer-template compliance cannot be certified without the original official template/naming sheet. |
| Application structure | Real Flask entry point preserved; no artificial `src/main.py` restructuring. |
| `docs/`, `submission/`, `runpod/` | Present. Evidence-status notes are not completed official proof documents. |
| `.env.example` | Variable names and placeholders only. Environment variables are not automatically loaded from this file. |
| `.gitignore` | Excludes credentials, checkpoints, archives, databases, user uploads, generated output, and Replit-only artifact/upload folders. |
| `LICENSE` | **Missing.** An owner-approved project-code license has not been supplied; no license grant was invented. |
| Third-party data | **Release blocked:** Artificial Analysis redistribution permission remains unresolved; SDG V5 endpoint terms and crosswalk-specific terms require confirmation. See [licensing](data-licensing.md). |
| Git history / LFS | No `.git` directory, old object database, private LFS objects, or LFS pointer files in the export. No new Git repository was initialized. |
| File sizes | Largest file is `futuretwin_embeddings/data/embedding_training/train_pairs.csv`: 37,321,016 bytes, about 35.6 MiB. Every file is below 50 MiB and GitHub's 100 MiB hard limit. Use Git CLI; this CSV exceeds the 25 MiB browser-upload limit. |

GitHub's limits were checked against its
[official large-file documentation](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github).

## Security and privacy

- The export-local pattern scan found **zero credential candidates**, private
  archive/database/checkpoint candidates, oversized files, symlinks, or LFS
  pointers. It checks this directory, not the parent workspace's Git index.
- The Replit dependency, static-analysis, and privacy scanners also reported
  no findings. Those scans are workspace-level, not proof of exhaustive
  export-specific coverage.
- Two email-like strings were reviewed: both are synthetic test fixtures
  (`example.test` / `example.com`), not real contact details.
- The three supplied screenshots were visually reviewed. They show product
  UI and public job listings, not resumes, account billing, credentials, or
  identifiable private user profiles. They are development-preview screenshots,
  not evidence of production publication.
- No secret values were accessed or printed. Automated pattern scans and
  visual review are not a guarantee that every possible secret or confidential
  detail has been detected; archive/binary contents are not exhaustively scanned.

Re-run before committing:

```bash
python3 scripts/repository_safety.py --history
```

The script deliberately reports history as not applicable when this export has
no `.git`, rather than inspecting the parent repository.

## Independent application verification

Testing used a separate copy under `/tmp`, outside the workspace, with no
`artifacts/`, uploads, parent Git repository, or development database connection.
Private models were copied **only into that temporary test copy**, never into
this source export.

| Check | Result |
|---|---|
| Unprovisioned source clone | 238 Python tests ran: 4 failures, 2 errors, 7 skipped. Model/inventory-backed functionality requires the documented private assets. |
| Provisioned source clone | All **238 Python tests passed**, with no skips reported. |
| Voice lifecycle suite | All **8 Node tests passed**. |
| Asset integrity | All **21 runtime files** matched `runtime-assets.json`. |
| Local models | MiniLM returned 3 ESCO candidates; DistilBERT produced a task prediction, with offline mode enabled. No RunPod or paid inference endpoint was used. |
| Standalone Gunicorn | Home, Career, Passport, My Future, Trends, Job Market, and SDG Map HTML routes returned HTTP 200 without Replit artifact wrappers. |
| Database dependency | Without PostgreSQL, SDG-map and job APIs returned 503, not fabricated results. |
| Fresh database setup | New, disposable PostgreSQL **17.5**, Unix-socket only. Both migrations and public-table schema initialization succeeded. No development records were copied. |
| Fresh database APIs | Profile, job-listing, benchmark-overview, and SDG-map APIs returned HTTP 200 after initialization. Job/benchmark history was empty, not copied or invented. |
| SDG snapshot | Generated locally and saved into the new test DB: **103 occupations + 204 skills = 307 nodes, across 17 goals**. |

The temporary database/server were stopped after testing. Existing development
records and trained checkpoints were not modified. Python dependencies were
reused from the existing installation; a fully clean dependency install and
PostgreSQL 16 specifically were not tested. Browser interaction on a published
production site was not tested because no production deployment exists.

Follow the [README](../README.md) in order: install dependencies, configure
environment variables, migrate a new database, initialize empty public tables,
provision authorized model files, then build the missing SDG snapshot.

## Accurate usage and URL status

- Replit: verified development workspace/preview use. The original workspace
  now has a Flask/Gunicorn production service definition; that is **preparation,
  not publication**. The exported `.replit` retains legacy collector metadata.
- RunPod: training is owner-reported. Available model-card/manifest settings
  and package-reported evaluation summaries are documented. Actual trainer
  scripts, provider logs, and a matching RunPod job record are absent.
- Inference: custom MiniLM and DistilBERT checkpoints load locally. There is
  no RunPod Serverless inference endpoint.
- The GitHub URL, stable Replit project/live-demo URL, RunPod job record, slide
  URL, and video URL remain **pending**. The supplied `.replit.dev` URL is
  labelled as a temporary development preview, not a live production demo.
- Best Match has **three** configured score factors: skill compatibility,
  AI task exposure, and AI benchmark evidence. Purpose/SDG alignment is not
  included in the score.

## Required owner/organizer input

- [ ] Approve a project-code license and add the genuine `LICENSE`.
- [ ] Resolve dataset redistribution rights or approve a revised public-data
      export. Existing source/workspace data was not deleted to hide this issue.
- [ ] Provide the official SDC template and PDF naming sheet to verify exact
      compliance, assigned domain, SDG track, and all mandatory forms.
- [ ] Provide authentic Replit and RunPod proof-of-use records and generate
      the required PDFs from those records using the organizer's exact names.
      **No PDFs are currently present under `submission/`.**
- [ ] Supply team members/roles and verified repository, demo, slides, and video
      links.
- [ ] Arrange an authorized, access-controlled runtime asset handoff for judges;
      do not upload checkpoints or the workspace backup to GitHub.
- [ ] Review public-demo authentication/privacy before exposing this exported
      browser-cookie-owned profile implementation to real users.

See [submission status](../submission/README.md) and
[new GitHub repository steps](push-to-github.md). Do not push publicly until
the release gates above are cleared.
