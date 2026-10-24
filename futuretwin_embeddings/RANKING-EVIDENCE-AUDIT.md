# Ranking evidence audit

**Historical audit of the original checkpoint.** Active v2 subsequently supplied
checkpoint-bound label provenance and passed staged validation. All 498 complete
exact-linked careers now qualify for Lower AI Exposure; Best Match remains the
default. Growing Jobs remains unavailable.
See [DISTILBERT-V2.md](DISTILBERT-V2.md) for the current contract and formula.

Reviewed 2026-10-23. No paid inference, model retraining, checkpoint changes,
new services or publication. Best Match is unchanged and remains the default.

## Current result

| Ranking | Eligible ESCO occupations now | Reason |
|---|---:|---|
| Lower AI Exposure | 0 / 3,039 | Original checkpoint training-label lineage is unverified. |
| Growing Jobs | 0 / 3,039 | No verified exact-occupation vacancy time series and crosswalk. |

Of the current ESCO catalog, **498** have complete exact-linked source task
inventories. These meet the task-inventory prerequisite only, not the full
exposure-ranking requirements. **1,973** have possible-only links with source
tasks, **136** have published links whose source occupations have no task records
in the bundled release, and **432** have no published ESCO link. Unknown is not
lower exposure. Per-occupation results can be exported with
`futuretwin_ranking_evidence.export_eligibility(path)`.

## A. What is verified about E0/E1/E2

Original paper: https://arxiv.org/abs/2303.10130

Reviewed rubric: https://arxiv.org/html/2303.10130v2 (section 3.3 and appendix A).

Original repository: https://github.com/openai/GPTs-are-GPTs

The paper defines exposure against a threshold of at least 50% task-completion
time reduction while maintaining quality:

- E0: no/minimal qualifying reduction, or reduced quality.
- E1: LLM alone can meet the threshold.
- E2: complementary LLM-powered software is needed to meet the threshold.

E2 is not “more dangerous” than E1. The annotation rubric also used a separate
image-related E3 category, combined with E2 for analysis.

At the reviewed repository revision recorded in
`data/distilbert_label_provenance.json`, `data/full_labelset.tsv` has **19,265**
rows and several **distinct targets**: `human_exposure_agg`, `gpt4_exposure`,
`gpt4_exposure_alt_rubric`, and `human_labels`. For example, human E0/E1/E2 counts
are 10,256/2,862/6,147, whereas GPT-4 counts are 8,561/2,702/8,002. Class names do
not identify which annotation target, if any, trained this checkpoint.

The uploaded ZIP has configuration, weights, tokenizer and `training_args.bin`.
Neither that ZIP nor the inspected local project has the classifier's labelled
training dataset, generation script, notebook or model card establishing its
lineage. Existing anchor/positive pairs are MiniLM training material, not an
E0/E1/E2 training set. The pickle training artifact was not executed/unpickled.

**Therefore no verified model label contract has been asserted.** The JSON
records a verified *research reference* and an explicitly unverified *training
binding*. Statistical agreement or similar label counts would not prove lineage.

To resolve this, supply the original training dataset/version and notebook/script,
chosen target column, label-to-index transformation, E3 handling, and any
synthetic/relabelled-example generation.

Only if that provenance supports it, the requested unweighted broad share would
be `100 × (n_E1 + n_E2) / n_all_classified_source_tasks`. This conditional formula
is documented, **not computed/displayed or used to sort now**. It is not a
job-loss, replacement or calibrated probability measure.

## B. Genuine tasks, cache and mapping

The current app already uses O*NET 31.0 Task Statements: **18,838** task records
for **923** O*NET occupations, not the older 37 demonstration tasks. The stored
160-token local predictions were reused; no corpus re-inference was necessary.
The eligibility audit verifies active prediction-method identity, text hashes and
complete exact-linked inventories without loading DistilBERT into inference.

See `data/ONET-ESCO-SOURCES.md` for official source URLs, CC BY 4.0 attribution,
crosswalk provenance and mapping-type limits. Exact equivalence, source release,
complete source-task coverage and the same trained model/inference method are
prerequisites. Broad/narrow/close relations are not silently promoted.

## C. DOSM historical vacancy data

Verified official pages:

- [Q2 2024 release](https://www.dosm.gov.my/portal-main/release-content/big-data-analytics-job-market-insights-and-my-job-profile-q224)
- [Q3 2024 release](https://www.dosm.gov.my/portal-main/release-content/big-data-analytics-job-market-insights-and-my-job-profile-q324)
- [DOSM reuse terms](https://www.dosm.gov.my/portal-main/article/term-of-use)

The two public XLSX downloads work. Older Q4 2023 and Q1 2024 download redirects
returned 404 during this audit, but their history is present in the later sheets.
The linked `/bda-jmi` page returned a no-longer-exists notice; My Job Profile
could not be retrieved reliably (TLS failure). No access control was bypassed and
no speculative scraper was enabled.

`import_dosm_vacancies.py` imports the pinned Q3 workbook and checks it against
the pinned Q2 workbook, using Python's ZIP/XML stdlib; no package or API required.
The committed normalized CSV contains **168 observations**, **8 broad groups**,
**2019-Q3 through 2024-Q3**, geography Malaysia. **160 overlapping observations**
agree between releases. Each imported quarter equals its three published monthly
cells. Source URLs, hashes, retrieval time, worksheet/cell identifiers, measure,
period start/end and source-group identities are preserved.

Important source-quality issues:

- Future quarter/month template zeros are not observations and are excluded.
- The Q3 workbook's occupation total `AB34` is zero despite nonzero group cells.
  This total is not imported or converted into a market collapse.
- The Q3 release webpage repeats Q2 group descriptions. Extraction uses the
  worksheet cells validated against monthly values, not that stale prose.
- The workbook provides neither official occupation codes nor classification
  version. `dosm-jmi:*` IDs are explicit **FutureTwin source-row identifiers**,
  not guessed MASCO/ISCO codes.
- These old data are a historical snapshot, not current vacancy levels.
- The eight published major groups are not detailed careers, and do not establish
  a consistent recruitment-site sampling frame.

MASCO being based on ISCO-08 does not establish detailed equivalence to individual
ESCO occupations. ESCO itself places many distinct occupations in the same ISCO
unit group. No authoritative exact MASCO–ESCO vacancy crosswalk was verified.
Thus no group totals are allocated to ESCO occupations and no career hiring
growth is computed from them.

An eligible future series needs official occupation codes/version, verified
equivalence to the target ESCO career, the same measure/geography/source and
documented comparable observation coverage, full equal-frequency periods, at
least two real observations and a positive baseline. Only then is
`100 × (current - previous) / previous` meaningful as observed posting growth.
Zero/absent baseline remains undefined, not zero growth.

Data source: Department of Statistics Malaysia. FutureTwin's extraction and
analysis are not endorsed by DOSM. DOSM permits data reuse under the Government
Open Data Terms of Use 1.0 with attribution and accurate presentation.

## D. API and minimal UI

Existing `/api/my-future/recommendations` keeps all three sort IDs and the
existing Best Match behavior. Its `ranking.evidence` includes the research audit,
actual task-inventory counts and historical-source coverage. Career cards also
carry `ranking_eligibility`, distinguishing ready task inventories from missing
label provenance. No new service, route, profile migration or paid collector.

Both Explore Careers and My Future expose this information under optional
**Ranking evidence** details. Warning text now identifies the precise remaining
issues instead of implying that no DOSM historical information exists.
