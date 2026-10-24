# Purpose & SDG MVP: evidence and limits

## Sources and review scope

The offline catalogue contains 17 goals and 169 target definitions retrieved
from the official UN Statistics Division SDG API V5. Malaysia observations retain
their observation years, selected dimensions, API URLs, release and retrieval
timestamp. They are snapshots, not a live feed or inferred 2026 values.

Six associations across five ESCO careers were assistant desk-reviewed against
explicit occupation descriptions, exact ESCO occupation–skill relationships and
official UN target text. The API marks these `assistant_desk_reviewed`. There
are **zero independent human approvals** and **zero measured occupational impact
outcomes**. Desk review means the quoted activities and target definitions were
checked, not that a worker caused an outcome.

Solar PV lifecycle/waste context is indirect and mixed, citing IRENA/IEA-PVPS
(June 2016). It concerns a technology, not evidence of an individual's harm,
and it is not a forecast of Malaysian waste. Unreviewed negative associations
are not invented; missing trade-off coverage is disclosed.

## Local MiniLM suggestions

The existing fine-tuned MiniLM encodes official target wording locally on CPU.
Its normalized target vectors are compared with the existing ESCO skill vectors.
The offline review queue contains 200 candidate links across 100 occupations,
200 distinct ESCO skills and all 17 goals. It covers nine ISCO major
occupation groups (1–9), with no more than 20 selected occupations from one
group. ISCO groups describe occupation families. Industry diversity also uses
the NACE 2.1 code URIs already supplied in the ESCO occupation CSV, grouped by
their two-digit divisions. All listed NACE codes are retained; the first listed
division is a deterministic diversity bucket, not an asserted primary industry.

Each candidate is based on an exact ESCO occupation–skill relation and a UN
target. The retrieval order combines target-to-skill cosine similarity (70%)
and target-to-occupation-description similarity (30%). This score is only for
review-queue ordering; it is not a probability, evidence of contribution, or
impact score. Candidate strength and direction remain unassessed until review.
Candidates never enter the purpose-ranking calculation. The existing model and
cached ESCO vectors are reused; there is no retraining or paid inference.

The candidate queue is separate from the six desk-reviewed associations: no
suggestion is promoted automatically. Currently, five of the 3,039 ESCO
occupations have at least one desk-reviewed link, and none has independent
human approval. The Purpose page reports these counts and keeps reviewed
connections separate from unreviewed suggestions; missing mappings are not
treated as zero contribution.

## Optional ranking

Best Match remains the default. Purpose Alignment uses the same candidate pool
already linked to the user's explicitly confirmed ESCO skill IDs.

* Skill component: the existing distinct listed-skill coverage fraction.
* Reviewed alignment: for each selected goal with reviewed evidence, choose the
  strongest signed relationship: direct 1, indirect 0.5, weak 0.25; positive +,
  negative −, mixed 0. Average across those evidenced selected goals.
* Ranking points: `skill_weight × coverage + purpose_weight × alignment`,
  with weights totalling 100. These are heuristic points, not percentages of
  competence, fit, social contribution or employment probability.
* Evidence coverage is displayed. With a nonzero purpose weight, unknown careers
  are excluded rather than scored zero. If none qualify, Best Match is shown
  with an explicit fallback notice. Existing Best Match order breaks ties.
* Demand weight is zero and unavailable. Employee counts, broad wages and
  collected ad samples are not a comparable verified exact-role vacancy series.

## Malaysia context, not a measured impact gap

Supported snapshots: UHC service coverage (2025 methodology), primary-level
reading proficiency (both sexes), safely managed drinking water (all areas),
and renewable share of total final energy consumption. Different dimensions
are filtered explicitly and never averaged together. Unsupported or ambiguous
series remain unavailable.

Charts juxtapose the chosen national indicator and DOSM broad-group median
monthly salaries. The wage scope is Malaysian-citizen employees, not exact
ESCO role pay. Broad group highlighting follows the existing ISCO major-group
label mapping and is contextual, not a verified detailed ESCO/MASCO crosswalk.
Observation dates and units remain separate. No common "unmet need" index,
need-to-wage ratio, causal impact/pay gap, underpayment claim or SDG target-gap
percentage is calculated.

## Persistence and existing systems

Purpose priorities live inside the existing AES-GCM-encrypted browser-owned
PostgreSQL profile; CSRF and owner checks are reused. Their field-scoped save
merges inside the same transaction/row lock. Legacy full-state clients cannot
erase these priorities. Profile deletion removes them with the profile.

Adding an exact linked skill to the learning plan uses the existing validated
My Future route. It does not add a confirmed qualification or assert mastery.
Neither DistilBERT checkpoint, prediction generation, exposure calculation,
MiniLM checkpoint, collector nor paid inference configuration is changed.

## Further evidence required

Independent human review of associations; broader reviewed positive and negative
activity/task links; outcome studies; verified detailed ESCO-to-national
occupation crosswalks; comparable role-specific vacancy/pay histories;
explicit national indicator targets and occupation-level contribution evidence.
Until then, purpose ranking is a limited opt-in heuristic and country comparisons
are context rather than quantified social-impact intelligence.
