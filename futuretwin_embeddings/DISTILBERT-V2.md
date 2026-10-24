# DistilBERT v2 validation and activation

## Artifacts and preservation

The user-supplied `futuretwin_distilbert_v2.zip` was extracted separately into
`models/distilbert_v2`. Active weights and tokenizer are in its `final_model`.
The original ZIP, `models/distilbert/final_model`, previous prediction generations,
MiniLM assets and PostgreSQL/user records were not deleted or replaced.
No pickle training artifact was executed.

- V2 ZIP SHA-256: `2a7c7c673f18840b07f3767be152ed27fa6cc53115d88a80a83e6696d5f85b82`
- V2 safetensors SHA-256: `8ad6ff6c9e0cba8379dd702d38338b8953efdeb67e70bd05264dbb9a2555475f`
- Checkpoint fingerprint: `66f259fb8947dc06b779334a6cbf7d8e9cad8302260fe94427966bb668cbb5de`
- Prediction fingerprint: `98bde4cbe429620e19c8d46a82e1f4fa95f758e9b431c4847ce5168f4cb6a5be`

The checkpoint fingerprint covers configuration, weights and tokenizer.
Prediction identity additionally covers the inference method and library versions.
`futuretwin_exposure_contract.py` binds semantic approval to this checkpoint and
the exact provenance, manifest and evaluation document hashes. Missing or changed
documents disable the semantic contract and ranking, not substitute another model.

## Label contract and limits of verification

The package records:

- Research data: OpenAI `GPTs-are-GPTs/data/full_labelset.tsv`.
- Source SHA-256:
  `094378905e1f3349e50a9a83dc69643a2ef227954d611c8316a46da08cb3d8de`,
  matching the published file inspected during the prior research audit.
- Task column: `Task`; target: **`gpt4_exposure`**, not the human or alternate-rubric column.
- Class indices: `0 → E0`, `1 → E1`, `2 → E2`.
- Raw source counts: E0 8,561; E1 2,702; E2 8,002.
- Conflict policy: drop 52 conflicting unique task texts / 375 rows.
- Subsequent duplicate rows removed: 950. Prepared rows: 17,940.
- Prepared label counts: E0 8,123; E1 2,463; E2 7,354.
- Prepared dataset SHA-256:
  `4258e83328d5165881733cd21fad3b4f93f1633b7a578af4d665b88d38b29ff0`,
  matching the training manifest's dataset hash.
- The manifest records a 160-token maximum and checkpoint selection by validation
  macro F1, not held-out test accuracy.

E0 denotes no qualifying LLM-related reduction under the historical rubric.
E1 denotes potential reduction of at least 50% using an LLM alone at comparable
quality; E2 denotes such potential using complementary LLM-powered software.
E2 is **not** a higher danger/severity level than E1.

### E3

The preparation policy is explicitly **drop E3**. The selected `gpt4_exposure`
column contains **zero explicit E3 rows**, so zero were dropped. Do not describe
this as filtering vision work out of the occupation inventories. This classifier
has no E3 output and cannot identify or exclude unseen E3/vision tasks.
The paper's separate E3-to-E2 analytical treatment is not an additional
transformation applied by this integration. The displayed share is conditional
on this three-class annotation target, not a complete image-capability measure.

### What has not been independently verified

The package documents lineage; it is not a reproducible training bundle.
The training/prepared CSV, test rows, exact split memberships, conflict-audit CSV
and training script were not supplied. Source checksum, manifest consistency,
approved file identity and confusion-matrix arithmetic were checked.
Training execution, absence of all leakage and held-out accuracy were **not**
independently reproduced.

## Local validation

CPU-only, `local_files_only=True`, `trust_remote_code=False`, safetensors,
evaluation mode, `torch.inference_mode()`, float32, batches of four, max length 160.
Strict loading found no missing, unexpected or mismatched parameters.

- 25 real O*NET tasks across five occupations: valid finite outputs; exact
  deterministic repeat; six labels changed relative to previous stored outputs.
- Full precomputation: **17,579 unique task texts → 18,838 source task records**.
  Every result matched its task-text checksum. No task was truncated.
- Full-inventory comparison: **5,884 labels changed**. This is model drift,
  **not** a measured accuracy improvement.
- Previous class counts: E0 9,731; E1 2,572; E2 6,535.
- V2 class counts: E0 8,166; E1 2,571; E2 8,101.
- **78 application/unit regression checks passed against a separate staged
  database before the active path or active prediction generation was changed.**

| Actual O*NET task | Previous | V2 |
|---|---|---|
| 15-1252.00 / 21661: Analyze information to plan installation/modification of a system | E2 | E1 |
| 15-1221.00 / 14623: Analyze problems to develop hardware/software solutions | E1 | E1 |
| 29-1141.00 / 1839: Maintain accurate, detailed reports and records | E2 | E1 |
| 47-2031.00 / 23430: Follow safety rules and maintain a safe, clean environment | E0 | E0 |
| 13-2011.00 / 21505: Prepare detailed reports on audit findings | E1 | E1 |

The exact task text, all softmax outputs and full run details are retained in
`generated-artifacts/distilbert-v2-staged-validation.json`.
Softmax outputs are not calibrated confidence.

### Supplied evaluation, internally checked

Accuracy 0.8412236; macro F1 0.8157724; E0 F1 0.8877847;
E1 F1 0.7322404; E2 F1 0.8272921; test support 2,746.
The supplied confusion matrix exactly supports these metrics.
Historical research-label accuracy is not workplace outcome validation.

## Share and ranking algorithm

For eligible exact-linked inventories:

```text
predicted task-exposure share = 100 × (count(E1) + count(E2)) / assessed task records
```

No E1/E2 severity weights, task-duration estimates, adoption probabilities,
employment predictions or replacement probabilities are calculated.
No denominator adjustment is made for E3: zero explicit E3 rows were excluded
from the selected training target, and the model cannot identify E3 at inference.

Eligibility requires approved label provenance; the official EC `exactMatch`
occupation link; tasks for every exact-linked O*NET source occupation; 100% valid
text-matching, untruncated predictions; one O*NET release and inference fingerprint.
**All 498 of the previously complete exact-linked careers qualify.**
Other 2,541 careers remain unranked/unknown under this mode. Computer Vision
Engineer remains a possible-only `closeMatch`, not an exact distribution.

Best Match remains the default and retains its previous algorithm.
On explicit Lower AI Exposure selection, first obtain the existing confirmed-ESCO-
skill candidate pool and career-area filters; exclude ineligible candidates;
then sort ascending by the exact `(E1+E2)/assessed` fraction. Stable ties retain
the existing Best Match order. Apply the display limit **after** filtering/sorting.
No arbitrary blended exposure/fit score is introduced. Empty eligible pools are
explicit and provide a Best Match alternative.

`predicted_task_exposure` is additive to existing API output. The legacy
`combined_exposure_percentage` stays null to avoid reinterpreting an ambiguous
field. New source/contract/share details appear in the existing dashboard,
recommendation cards, comparisons and optional method disclosures.

The active-generation marker and fingerprinted caches select v2 only.
Previous generations remain preserved but cannot be reused as v2. Browsing reads
precomputed tasks without loading DistilBERT. No paid inference, new service,
model training or publication occurred.
