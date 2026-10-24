# Career intelligence integration contract

This document describes the additive Flask API used by the career UI.
Existing routes, encrypted profiles, CSRF and session ownership are preserved.
No paid inference is needed for these read endpoints.

## Recommendations

`GET /api/my-future/recommendations?limit=12&sort=best_match`

Sort IDs: `best_match`, `lower_exposure`, `growing_jobs`.
The response keeps existing `recommendations`, `saved_occupations`, `limited`
and profile status fields and adds:

```text
ranking:
  requested: sort ID
  effective: sort ID (best_match when requested evidence is unavailable)
  fallback_reason: string or null
  options: [{id, label, available, reason}]
  evidence: {labels, tasks, vacancies}
```

Every recommendation keeps its current identifiers and matched skills.
`skill_coverage` adds `percentage`, plus `essential` and `optional`
objects with `matched_count`, `total_count`, `percentage`.
The numerator is distinct confirmed ESCO IDs, not semantic similarity.
Existing `task_exposure` contains stored class counts, source coverage and
mapping quality. `hiring_trend` contains `status`, `growth_pct` (nullable),
`reason` and provenance when available. Unknown is never zero.

Lower-exposure sorting is enabled for the 498 complete exact-linked careers
with approved v2 provenance, matching inference/source identity and no truncated
tasks. It filters the existing confirmed-skill candidate pool, then sorts ascending
by the exact `(E1+E2)/assessed` fraction; ties retain Best Match order. Filtering
and sorting happen before the display limit. Best Match remains the default.
Growing Jobs is unavailable without comparable, dated, occupation-level vacancy
observations. Unsupported states explain their missing evidence, not fabricate scores.
The optional Ranking evidence disclosure now reports the checkpoint-bound
training contract and its reproducibility limits.
It reports the imported DOSM historical **group-level** snapshot without
assigning those counts to precise ESCO careers. Per-card `ranking_eligibility`
identifies complete task inventories separately from full ranking eligibility.
See `DISTILBERT-V2.md` for active validation, E3 treatment and remaining evidence.

## Career detail

`GET /api/my-future/career?uri=<ESCO URI>` retains all existing fields and adds:

```text
intelligence:
  model_measure:
    status, label, combined_exposure_percentage (nullable), reason
    predicted_task_exposure:
      status, label, percentage (nullable), numerator, denominator,
      formula, weighting, e3_note, interpretation, reason
  advancement:
    status, series: [], reason, measured_task_count
  hiring:
    status, growth_pct (nullable), reason
  automation_potential:
    status, percentage (nullable), reason
  replacement_probability:
    status, percentage (nullable), reason
  methodology: [short factual method statements]
```

`advancement.series` entries, when evidence permits them:
`source`, `benchmark`, `version`, `task`, `unit`, `direction`, `protocol`,
`model`, `points: [{evaluation_date, score}]`, `absolute_change`,
`relative_change_pct` (nullable), `absolute_change_unit`,
`improvement_direction`. No collection/model-release dates are silently
substituted for evaluation dates; no incompatible metrics are pooled.

Continue to use `task_exposure` for the real class distribution, O*NET task
details, source inventory coverage and possible-only mappings.
Benchmark records in `ai_impact` are independent capability measurements,
but their MiniLM-to-ESCO task relationships are semantic candidates, not
verified occupational automation. Remove the old eight-segment
benchmark-link-count decoration as an exposure measure.

The UI uses AI Tasks | Skills | Jobs, with technical methods optional.
Class shares are unweighted task counts, not working hours or job-loss
probabilities. Preserve the package-reported held-out evaluation disclosure,
especially E1 F1; its arithmetic was checked, not independently re-evaluated.

## Compare

`GET /api/my-future/compare?uri=<URI1>&uri=<URI2>` accepts 2–4 distinct
ESCO occupations. Returns `careers` (normal career-detail objects) and
`comparability` with `class_distributions_comparable`, `reason`, and
`combined_exposure_allowed: false` (legacy ambiguous field).
The additive `predicted_task_exposure_shares_comparable` is true only when the
same source/method inventories also have eligible predicted task shares.
Do not label a career safer on the basis of missing data.

## Opportunity Radar

`GET /api/my-future/opportunities?limit=12`

```text
status, jobs: [], skills: [], coverage, categories, methodology
```

Job entries:
`uri`, `title`, `category`, `hiring_trend`, `matched_skills`,
`evidence: [{source, title, url, posted_date}]`.

Skill entries:
`uri`, `label`, `category`, `demand_change_pp` (nullable),
`sample_mentions`, `sample_postings`, `sample_share_pct` (nullable),
`related_careers: [{uri, title}]`, `evidence`.

Category `opportunity_candidate` is a real observed candidate, NOT a
demonstrated newly emerging or growing role. Those stronger categories require
comparable longitudinal observations. Counts from a limited collected ad
sample are not total market demand. The endpoint never fabricates empty-state
cards or uses AI in a title as proof of emergence. Source links must be safe
HTTP(S) URLs. Loading and unavailable states must be explicit.

Use existing Save, Set Goal and roadmap actions. A learning-plan addition
does not confirm mastery or add a skill to the confirmed Passport.

## Local extraction (supersedes the original hosted dependency)

Resume/experience extraction now uses conservative local ESCO vocabulary and
source-span activity rules, followed by local MiniLM candidate matching and
explicit user review. The hosted OpenAI dependency was removed during the
GitHub preparation audit. Consent remains required; private text is not sent
to an external inference service. This is not LLM extraction and can miss
paraphrases. DistilBERT never treats private resume text as occupation tasks.
