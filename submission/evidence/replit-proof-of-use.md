# Replit proof-of-use status

**Status: preparation note, not an official proof document.**

## Evidence verified in this workspace

- The root `.replit` file requests Python 3.11 and PostgreSQL 16 and configures
  the scheduled collector command:
  `python3 futuretwin_embeddings/run_futuretwin.py`.
- The original Replit workspace has a separate `artifacts/futuretwin: web`
  workflow. Its artifact manifest starts
  `python3 -u ../../futuretwin_embeddings/futuretwin_dashboard.py` from the
  `artifacts/futuretwin` working directory.
- On 2026-10-24, the current development preview returned HTTP 200 for `/`,
  `/career`, `/my-future`, and `/sdg-map`.
- The development preview is not evidence of a published production website.
  The root `.replit` contains legacy scheduled-collector metadata. The original
  workspace's FutureTwin artifact was subsequently prepared for Flask/Gunicorn
  production serving, replacing the static React/Vite definition. No published
  deployment was found during the final review.

These facts can support a truthful description of the workspace configuration
and a running development preview. They do not prove who owns the account or
that a production site was deployed.

## Still needed from the project owner

The supplied screenshot is included as
[`../SDC2026_LM10_Replit_POU.pdf`](../SDC2026_LM10_Replit_POU.pdf). It shows the
FutureTwin project in a Replit development preview, but not a published
deployment or account ownership. If SDC requires proof of a running workflow or
account identity, provide a separate, authentic current capture that shows only
the necessary information. Do not expose secrets, profile data, recovery
details, or unrelated account information.

The PDF is a conversion of the supplied image; no account or deployment claims
were added. The product screenshots under `docs/screenshots/` show website UI,
not a published production deployment.

## Public link status

The current `.replit.dev` preview URL is temporary. No stable public production
URL was verified. See the project-links table in the root README.
