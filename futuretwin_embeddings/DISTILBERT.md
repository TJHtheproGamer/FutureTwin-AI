# Local trained task classifier

The active `futuretwin_distilbert_v2.zip` was extracted separately to
`models/distilbert_v2/final_model`. The original `futuretwin_distilbert.zip`
and `models/distilbert/final_model` remain untouched.
See [the v2 validation and promotion report](DISTILBERT-V2.md).
Inference uses its actual safetensors classifier
and tokenizer, not a base checkpoint. `training_args.bin` is not needed or loaded
(it is a pickle-based training artifact).

All model/tokenizer loading uses `local_files_only=True` and
`trust_remote_code=False`. The loader requires a complete matching classification
head. Inference uses CPU, evaluation mode, `torch.inference_mode()`, batches of four
and a 160-token ceiling, matching the user's reported RunPod training setting.
The original saved config/tokenizer are not rewritten. Responses report truncation.
There is no remote inference,
download, retraining, quantization, fallback classifier or paid-service integration.

## Evidence boundaries

- Config mapping: `0 → E0`, `1 → E1`, `2 → E2`.
- Active v2's hash-bound provenance documents the checksum-matched GPTs are GPTs
  `gpt4_exposure` annotation target, label indices and E3-drop preparation policy.
  The selected source column contains zero explicit E3 rows. This is not an
  independently reproduced training or held-out evaluation.
- Legacy `combined_exposure_percentage` stays `null`. The additive
  `predicted_task_exposure` object explicitly labels the unweighted
  `100 × (E1 + E2) / assessed task records` share, where evidence is sufficient.
- Per-class sample share = `100 × predicted-class count / classified sample size`.
  These are equally weighted sample-task counts, not employment, time-use,
  automation or replacement probabilities. Softmax outputs are not calibrated.
- Occupation exposure now uses the **official O*NET 31.0 Task Statements** source:
  18,838 task records across 923 O*NET occupations. The older 37-row `data/tasks.csv`
  remains as a demonstration asset and is not used for occupation exposure.
- O*NET-SOC codes are linked to ESCO URIs through the published European Commission
  crosswalk, not title matching. Original mapping types and versions are preserved.
- Only the crosswalk's `exactMatch` relations contribute to primary occupation
  distributions. `broadMatch`, `narrowMatch` and `closeMatch` task sets remain
  inspectable, separately labelled possibilities. `exactISCO` is not silently
  expanded into every ESCO occupation in an ISCO group.
- Computer vision engineer has a published `closeMatch` to O*NET Data Scientists,
  not an exact task inventory. The system shows the relationship and source-task
  predictions without claiming a verified Computer Vision Engineer distribution.
- Existing MiniLM/ESCO matching, confirmed-skill fit ranking, benchmark task
  evidence, user profiles and database records are unchanged. Recommendations
  carry a separate `task_exposure` context field. Best Match remains unchanged
  and the default. Explicit Lower AI Exposure sorting filters to eligible
  exact-linked inventories, then sorts their predicted E1+E2 task shares.

## APIs

`GET /api/occupations/exposure?uri=<actual ESCO occupation URI>` returns the sample
tasks, actual class predictions, separate E0/E1/E2 distributions, source provenance,
trained-artifact fingerprint and limitations. Unknown occupations return 404;
model failures return 503, not fabricated predictions.

`POST /api/occupations/classify-tasks`

```json
{"tasks": ["Locate and debug errors in software applications."]}
```

Supply the existing browser session cookie and `X-CSRF-Token` from
`GET /api/profile`. This does not create or save a profile. Limits: 16 texts per
request, 8,000 characters per text, 64 KB body, 10 requests/minute/session, one
concurrent local inference batch per process. Busy requests return 429.

Outputs contain the original input, predicted `label`, all three uncalibrated
`probabilities`, token lengths, `truncated` and a task identifier. An optional
`task_ids` list supplies caller-owned IDs; otherwise IDs are request positions,
not claims of verified O*NET provenance. API responses use `Cache-Control: no-store`.

## Precompute and cache

From `futuretwin_embeddings/`:

```sh
python3 futuretwin_task_exposure.py
```

This imports the bundled official source snapshots, then classifies all distinct
O*NET task texts locally with one model load and CPU minibatches of four. The
results are stored per original O*NET-SOC code and Task ID. A repeat run with the
same source assets, trained checkpoint and inference method reuses the database
without inference.
Normal career browsing only reads precomputed results and never loads DistilBERT.

The occupation database is `generated-artifacts/onet_task_exposure.sqlite3`.
It contains public source tasks, full crosswalk edges, source-version metadata,
checksums and model-fingerprinted predictions. This is separate from the existing
application PostgreSQL database; no existing user tables or records are changed.

The bounded ad-hoc SQLite **prediction cache** remains
`generated-artifacts/distilbert_predictions.sqlite3`.
Keys combine a prediction fingerprint (unchanged trained asset fingerprint,
token ceiling, batching/padding/dtype/device and library versions) with the exact
input-text hash. Raw submitted text is not stored. Memory cache is
bounded to 512 results; disk cache to 5,000. These bounds do not truncate the
separate complete O*NET database. Changing the checkpoint or inference method
requires precomputation, never reuse under a stale version. Old corpus
generations remain stored separately. `precompute_database(activate=False)` can
stage a new generation without disrupting the active generation; activate the
validated generation with the app update.

The model/tokenizer are lazily loaded once per server worker and retained for
uncached batches under the existing exclusive inference lock. Ordinary career
browsing does not load them. A worker therefore needs memory for MiniLM plus
DistilBERT if both have been used.

The original checkpoint's historical accuracy 0.7260, macro F1 0.6400 and E1 F1
0.4348 are retained as legacy user-reported results, not active v2 metrics.
V2 package-reported accuracy is 0.8412, macro F1 0.8158 and E1 F1 0.7322 on 2,746
test samples. The confusion-matrix arithmetic was checked; the held-out rows
were not included for independent evaluation. Real-world calibration is unknown.
Actual 160-token CPU validation, deterministic repeats, cache consistency,
latency and peak process RSS are recorded in the ignored
`generated-artifacts/career-intelligence-validation.json`.

### Coverage and uncertainty

Task coverage means classified records / records in the exact-mapped O*NET
inventory. It is not the share of every task performed in an ESCO job. Core and
supplemental tasks are both retained and equally counted; no invented time weights
are used. Source dates, task type, incumbents responding and domain source remain
inspectable.

The E1/E2 near-tie display flag means the two largest raw softmax outputs are E1
and E2 and differ by at most **5 percentage points**. This transparent display
heuristic is not calibrated uncertainty. Raw outputs and the top-two gap are
available for inspection. No confidence score or competence score is calculated.

Source licenses, attribution and exact snapshot hashes are documented in
[`data/ONET-ESCO-SOURCES.md`](data/ONET-ESCO-SOURCES.md).

The ZIP, extracted weights and generated cache are excluded from Git/deployment
outputs. They remain local workspace assets. No publishing/storage service was
enabled. A future approved deployment needs an explicit local-model packaging
plan rather than assuming ignored weights will ship automatically.

Initial five-task results and the weights SHA-256 are recorded in the ignored
`generated-artifacts/distilbert-verification.json`.
