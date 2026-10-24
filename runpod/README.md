# RunPod training notes and actual inference architecture

## Summary

The project owner reports that RunPod was used to train MiniLM and DistilBERT.
The repository contains MiniLM data-preparation code, prepared train/validation/
test pairs and model-card training metadata, plus a DistilBERT v2 training
manifest and evaluation report. The actual trainer scripts and RunPod activity
logs are not included. For DistilBERT v2, the manifest's referenced labelled
training CSV and exact split memberships are also absent.

There is no active RunPod Serverless inference endpoint. `runpod/handler.py` is
not included in this source export, and no application code
calls a RunPod endpoint. FutureTwin loads MiniLM and DistilBERT locally. The
DistilBERT loader uses CPU and `local_files_only=True`; the website does not need
RunPod to serve predictions.

## MiniLM / ESCO skill retrieval

### Source and preparation available in this repository

[`futuretwin_embeddings/prepare_training_data.py`](../futuretwin_embeddings/prepare_training_data.py)
is the available MiniLM **data-preparation script**, not a model trainer or
RunPod launcher. It reads the ESCO occupation, skill and occupation-skill
relation CSVs, keeps essential relations, forms occupation-description
(`anchor`) and skill-description (`positive`) pairs, deduplicates them, and
splits by occupation using NumPy seed `42` and nominal 80/10/10 proportions.
The checked-in prepared files contain 53,700 train pairs, 6,992 validation
pairs and 6,908 test pairs (excluding each CSV header).

From the repository root, the available preparation command is:

```bash
python3 futuretwin_embeddings/prepare_training_data.py
```

It writes into `futuretwin_embeddings/data/embedding_training/` and can
overwrite the existing pair/catalog CSVs. Back them up or run the script in a
separate copy if preserving the current prepared data matters. It does not train
a model, launch RunPod, select a checkpoint or produce an evaluation report.

### Training details recorded by the model card

The local model card at
`futuretwin_embeddings/models/futuretwin_minilm/README.md` (inside the
checkpoint directory excluded from the GitHub export) records:

- Base: `sentence-transformers/all-MiniLM-L6-v2`, revision
  `1110a243fdf4706b3f48f1d95db1a4f5529b4d41`.
- 53,700 anchor-positive training samples; `MultipleNegativesRankingLoss`
  with cosine similarity, scale `20.0`, query-to-document direction and no
  cross-device gathering.
- Per-device batch size `16`, `2` epochs, learning rate `2e-5`, linear schedule,
  warmup value `0.1`, `no_duplicates` batch sampler, fused AdamW and weight
  decay `0.0`.
- Model output: 384-dimensional embeddings, mean pooling and normalization;
  maximum sequence length `256`.
- Reported framework versions include Sentence Transformers `6.1.0`,
  Transformers `5.20.2`, PyTorch `2.8.0+cu128` and Accelerate `1.15.0`.
  The model card reports `8.7` minutes of training and includes stepwise
  training-loss values.

These are **model-card-reported** details, not RunPod logs. The CUDA-enabled
PyTorch build string does not prove that a GPU was used or identify a GPU.
The repository does not include a MiniLM training script or a separate,
independently verified retrieval evaluation metric.

## DistilBERT task classifier

### v2 training configuration recorded in the supplied package

The local, ignored model package's
`models/distilbert_v2/training_manifest.json` records the following metadata.
The checkpoint package and machine-readable manifest are not included in the
GitHub export; the tracked
[`DISTILBERT-V2.md`](../futuretwin_embeddings/DISTILBERT-V2.md) documents the
checked summary:

| Setting | Recorded value |
|---|---|
| Base model | `distilbert/distilbert-base-uncased` |
| Dataset / provenance paths | `data/labelled_tasks.csv` / `data/label_provenance.json` |
| Epochs / batch size | `3` / `16` |
| Learning rate / seed | `2e-5` / `42` |
| Maximum token length | `160` |
| Validation split seeds | train `42`; validation `1042` |
| Selected checkpoint | `checkpoint-2376` |
| Selection criterion | validation macro-F1 |
| Prepared dataset SHA-256 | `4258e83328d5165881733cd21fad3b4f93f1633b7a578af4d665b88d38b29ff0` |

The manifest timestamp is `2026-10-23T14:42:10.102239+00:00`. This package
metadata does not identify RunPod, its hardware or the actual job execution.
The referenced training CSV, exact split memberships and trainer script are
not included, so the run is not reproducible from this repository alone.

### Results included with the package

The local package's `models/distilbert_v2/evaluation.json` reports a test set
of 2,746 samples. This results summary is retained here and in
[`DISTILBERT-V2.md`](../futuretwin_embeddings/DISTILBERT-V2.md):

| Measure | Package-reported result |
|---|---:|
| Accuracy | 84.12% |
| Macro F1 | 81.58% |
| E0 F1 (1,207 samples) | 88.78% |
| E1 F1 (387 samples) | 73.22% |
| E2 F1 (1,152 samples) | 82.73% |

The confusion-matrix arithmetic was checked, but the test rows and training
run were not independently reproduced. These are reported
historical rubric-classification results, not workplace outcome validation,
calibrated probabilities or job-replacement accuracy.

For the earlier DistilBERT checkpoint, `DISTILBERT.md` records a
user-reported 160-token setting and legacy accuracy `0.7260`, macro F1
`0.6400`, and E1 F1 `0.4348`. The note explicitly says those figures were not
revalidated; they are not v2 results.

## What can be reproduced, and what is missing

- MiniLM ESCO pair preparation can be rerun with the command above. The actual
  MiniLM fine-tuning command/script and RunPod launch configuration are absent.
- DistilBERT v2 configuration and packaged evaluation results can be inspected.
  The trainer script, referenced training data and exact split files needed to
  reproduce that run are absent. No RunPod command should be inferred from the
  manifest.
- Website inference remains local. See the root README for secure model-file
  provisioning and Flask startup instructions. Do not use the model-card
  download example as the FutureTwin runtime path.

## Evidence needed for an SDC proof-of-use claim

The repository supports a cautious description of reported RunPod training,
not proof that a particular RunPod job produced these checkpoints. If the
submission requires proof, use authorized records from the project owner's
RunPod account: the completed job/pod page, actual command and logs, timestamps,
hardware details if shown, and an artifact/checkpoint identifier that matches
the supplied model. Do not fabricate missing commands or hardware details.
Training evidence does not prove a deployed inference endpoint.

No RunPod account was accessed, no service was activated, and no checkpoint,
website code or user data was changed for this documentation update.
