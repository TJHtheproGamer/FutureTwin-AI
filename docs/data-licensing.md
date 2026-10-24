# Third-party data and code licensing review

**Reviewed:** 2026-10-24  
**Scope:** data files in the prepared GitHub source export and their cited
publisher terms. This is a technical provenance check, not legal advice.

## Findings

| Included source or derived data | Official terms found | Public-release status |
|---|---|---|
| O*NET 31.0 task statements (`onet_task_statements_31_0.csv.gz`, `tasks.csv`, and task-label provenance) | O*NET 31.0 database content is CC BY 4.0. Credit the database and USDOL/ETA, link the license, indicate changes, and do not imply endorsement. | Reusable with the attribution already recorded in `futuretwin_embeddings/data/ONET-ESCO-SOURCES.md`. Keep the required notice with any redistribution; distinguish source wording from FutureTwin labels. |
| ESCO classification references, ESCO–O*NET crosswalk, and derived MiniLM pairs | The European Commission says ESCO may be reused for any purpose free of charge under Decision 2011/833/EU, with the prescribed attribution; identify modified/adapted ESCO content. | Reusable with attribution and change notices. The crosswalk source and version are documented in `ONET-ESCO-SOURCES.md`; preserve that provenance and check the crosswalk-specific source page before redistributing the crosswalk file. |
| DOSM Job Market Insights Q3 2024 snapshot (`dosm_jmi_group_vacancies.csv`) | DOSM's portal terms authorize copying, distribution, adaptation, and commercial/non-commercial use under Government Open Data Terms of Use 1.0. They require “Data source: Department of Statistics Malaysia,” lawful use, and no presentation that implies DOSM association or endorsement. | Reusable with the stated source credit, disclaimer, and historic-data caveat. The adjacent metadata file records the source and retrieval details. |
| UN Statistics Division SDG API V5 target and Malaysia observation snapshots, plus derived candidate links | The UNSD API catalogue says its public SDG API is governed by UNdata terms. UNdata terms allow free copying and redistribution of its data/metadata when cited. The repository's snapshots identify the newer V5 endpoint; confirm that the catalogue's terms apply to that exact V5 endpoint before relying on them for these files. | **Conditional.** Retain attribution and source/version dates. Confirm the V5 terms before publicly redistributing the snapshot files. |
| Artificial Analysis API snapshots and derived capability/change CSVs (`ai_snapshot_*.json`, `capabilities_*.csv`, `ai_capabilities.csv`, `ai_capability_changes.csv`, `detected_ai_advancements.csv`) | Artificial Analysis requires attribution when API data is displayed or shared. Its API documentation directs users to contact the provider for redistribution rights or bespoke terms; no permission for this repository's raw snapshot files was found. | **Not cleared.** Do not publish these data files as-is until written redistribution permission or terms covering this use are confirmed. An alternative is to omit them from a public export; do not remove workspace data without review. No paid license was obtained. |
| Job-board response caches and local model/database assets | The job-board response caches are ignored and absent from the clean export. Fine-tuned checkpoints, the precomputed task-exposure database, PostgreSQL records, and attached uploads are also absent from the clean export. | Not part of the public export. Do not add them without source-term, privacy, and size review. |

## Project-code license

There is no root `LICENSE` file. The repository does not currently grant a
project-wide open-source license for its own code. The owner must choose and
approve a code license before describing the project as open source; none has
been invented or added.

## Official references

- [O*NET 31.0 Database Content License](https://www.onetcenter.org/license_db.html)
- [ESCO reuse FAQ](https://esco.ec.europa.eu/en/about-esco/faq)
- [ESCO–O*NET crosswalk source](https://esco.ec.europa.eu/en/use-esco/other-crosswalks)
- [DOSM terms of use](https://www.dosm.gov.my/portal-main/article/term-of-use)
- [UNSD API catalogue](https://unstats.un.org/unsd/api)
- [UNdata conditions of use](https://data.un.org/Host.aspx?Content=UNdataUse)
- [UNSD SDG API V5](https://unstats.un.org/sdgs/UNSDGAPIV5/swagger/)
- [Artificial Analysis API documentation](https://artificialanalysis.ai/data-api/docs)

## Release gate

The prepared export passed credential/privacy scans, but it still contains
Artificial Analysis result snapshots and the SDG API V5 terms need endpoint-
specific confirmation. **Do not publicly redistribute the export until those
rights are resolved or the affected data files are excluded from the public
copy.** Preserve required attribution for O*NET, ESCO, and DOSM. Do not publish
private model archives, database records, secrets, or user uploads.
