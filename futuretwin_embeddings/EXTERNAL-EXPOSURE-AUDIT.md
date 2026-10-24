# External framework audit

Reviewed 2026-10-23. No external scores have been invented, imported into
DistilBERT labels, or used to rank careers.

## ILO 2025 refined GenAI index

Official paper:
https://www.ilo.org/publications/generative-ai-and-jobs-refined-global-index-occupational-exposure

Full working paper:
https://webapps.ilo.org/static/english/intserv/working-papers/wp140/index.html

The paper combines occupational task material from Poland, worker assessments,
expert review and model-assisted scoring, then reports an ISCO-08 occupational
framework with four increasing exposure gradients. Its scope is specifically
generative AI, not all AI, robotics or machine vision. Exposure gradients and
global employment shares are not individual job-displacement probabilities.

The published ISCO-08 four-digit appendix could support **group-level context**
through ESCO's published ISCO group identifiers. It would not establish a precise
score for each of the more detailed ESCO occupations. A machine-readable export,
versioned code validation and the specific data redistribution license still
need to be cleared before bundling a numerical adapter. Public access to a report
alone is not evidence of unrestricted dataset reuse. No numerical adapter is
silently enabled.

## OECD 2026 AI exposure measure

Official publication:
https://www.oecd.org/en/publications/2026/05/the-oecd-ai-exposure-measure_489cfd42.html

DOI/document:
https://www.oecd.org/content/dam/oecd/en/publications/reports/2026/05/the-oecd-ai-exposure-measure_489cfd42/f3da0f0a-en.pdf

The measure maps nine cognitive, social and physical AI capability domains to
occupational requirements and constructs an **AI Capability Gap** index. Lower
gaps indicate closer AI-to-occupation capability profiles, not lower exposure.
Adoption, regulation and organisational change condition real employment effects.
This index is neither a probability of job loss nor interchangeable with
FutureTwin E0/E1/E2 or the ILO gradients.

The public publication was verified. The exact reusable machine-readable
occupation release, applicable redistribution terms and a validated code-level
crosswalk need verification before occupation values are displayed in FutureTwin.
Do not infer detailed ESCO values from broad published groups.

## Current data limitations

The later ranking-source audit found downloadable DOSM JMI historical workbooks.
Their normalized major-group history is now available separately; it does not
resolve exact-career growth or the single-day ad sample limitation below.
See `RANKING-EVIDENCE-AUDIT.md` for URLs, source-quality checks and mapping limits.

The stored vacancy sample currently has 99 canonical Remote OK ads and 10
Remotive ads. Successful collections span one calendar day; source collection
history/completeness does not validate comparable occupation-level periods.
Posting dates are not collection coverage. Growing Jobs, hiring-growth rates
and skill-demand change therefore remain unavailable. The Opportunity Radar
uses explicitly named terms in real stored ads as **candidates**, not proof of
new or growing occupations.

Current benchmark records include sources without actual evaluation dates and
without recorded comparable evaluation protocols. The career advancement
adapter rejects collection-date migrations and incompatible/missing protocols.
Measured benchmark scores remain inspectable separately from semantic career
links; missing a valid advancement series does not mean AI made no progress.

The original audit did not change the then-hosted resume extractor. The later
GitHub preparation cleanup removed that dependency: resume and experience
extraction now use local vocabulary/span rules and local MiniLM suggestions,
with explicit consent, source validation and user confirmation.
Agent/hosting usage is separate; no promise of zero platform cost is made.
