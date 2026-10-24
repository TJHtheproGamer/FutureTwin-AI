# SDC Hackathon 2026 submission preparation

**Registered team name supplied by the user:** `LM10`

This folder records readiness and evidence gaps. It does not contain official
SDC forms, completed declarations, signatures, or fabricated provider proof.
The requested README headings were supplied, but the official PDF template was
not. The user-provided Replit and RunPod screenshots are included as
`SDC2026_LM10_Replit_POU.pdf` and `SDC2026_LM10_Runpod_POU.pdf`. They show a
development preview and account billing activity; they do not establish a
published deployment or tie a specific RunPod job to a model checkpoint.

## Included preparation documents

- [`../README.md`](../README.md) — judge-facing project README in the requested
  SDC structure.
- [`evidence/replit-proof-of-use.md`](evidence/replit-proof-of-use.md) —
  verified workspace facts and the genuine Replit evidence still needed.
- [`SDC2026_LM10_Replit_POU.pdf`](SDC2026_LM10_Replit_POU.pdf) — the supplied
  Replit workspace screenshot, preserved as a one-page landscape PDF.
- [`SDC2026_LM10_Runpod_POU.pdf`](SDC2026_LM10_Runpod_POU.pdf) — the supplied
  RunPod billing screenshot, preserved as a one-page landscape PDF.
- [`evidence/runpod-proof-of-use.md`](evidence/runpod-proof-of-use.md) —
  repository-supported training notes and the RunPod provider records still
  needed.
- [`../docs/architecture.md`](../docs/architecture.md) — actual app and
  Replit configuration boundaries.
- [`../docs/data-licensing.md`](../docs/data-licensing.md) — source-by-source
  licensing review and public-release gate.
- [`../docs/screenshots/README.md`](../docs/screenshots/README.md) — development
  preview screenshots, not published-site proof.

## Submission checklist

- [x] Independent export-copy verification: 238 Python tests and 8 Node tests
      passed after private runtime provisioning; fresh temporary database
      initialization was also tested. See [final review](../docs/final-review.md).
- [x] Preserve the existing Flask application structure and regression tests;
      no example `src/main.py` structure was introduced.
- [x] Root README includes all requested SDC sections and marks unknown facts
      and URLs as pending.
- [x] Replit and RunPod evidence status documents use available evidence only;
      they do not claim account ownership, provider logs, signatures, or a
      RunPod endpoint.
- [x] The user-supplied Replit workspace screenshot is included as a PDF and is
      labeled as development-preview evidence, not proof of a published site.
- [x] The user-supplied RunPod billing screenshot is included as a PDF and is
      not described as proof of a specific training run.
- [ ] Other official forms, declarations, signatures, slide deck, and demo
      video were not supplied.
- [x] Current preview routes and regression suites were verified in the
      existing workspace.
- [x] Credential/privacy scanners reported no findings; a separate
      pattern-based current-source and Git-history scan found no credential
      candidates.
- [x] Private model archives, PostgreSQL records, and attached uploads are not
      present in the clean GitHub source export.
- [x] The 21 active runtime files in the current workspace pass the manifest
      SHA-256 check; none are copied into the clean export.
- [ ] Official assigned domain and SDG track: organizer confirmation needed.
- [ ] Team member names and roles: team confirmation needed.
- [ ] Verified GitHub repository URL, stable Replit project/deployment URL,
      RunPod training-record URL, slide URL, and video URL: still pending.
- [ ] Official PDF filenames/templates and any required signatures: organizer
      files needed; no forms have been created.
- [ ] Artificial Analysis snapshot redistribution rights and SDG API V5 terms:
      resolve, and confirm the crosswalk-specific terms, before public
      redistribution. The export is not license-cleared as-is; see
      `../docs/data-licensing.md`.
- [ ] Project-code license: owner decision needed; no root `LICENSE` is present.
- [ ] Private model files and a PostgreSQL database must be provisioned for a
      complete judge demonstration.

## Evidence submission safety

Only attach records the team is authorized to disclose. Redact secrets,
credentials, profile data, payment information, and unrelated personal
information. Never present the temporary development preview as a published
production deployment.
