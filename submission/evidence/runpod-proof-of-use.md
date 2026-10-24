# RunPod proof-of-use status

**Status: preparation note, not provider-generated proof.**

## What the repository supports

- The project owner reports that RunPod was used to train MiniLM and
  DistilBERT.
- [`runpod/README.md`](../../runpod/README.md) records the MiniLM model-card
  settings and prepared-pair counts, plus the DistilBERT v2 package-manifest
  settings and package-reported evaluation results.
- `futuretwin_embeddings/prepare_training_data.py` prepares MiniLM data. It is
  not a trainer or RunPod launcher.
- The actual trainer scripts and RunPod job logs are not present. DistilBERT's
  referenced training CSV and exact split memberships are also absent.
- The website loads both models locally. No RunPod Serverless handler or
  inference endpoint is present or claimed.
- [`../SDC2026_LM10_Runpod_POU.pdf`](../SDC2026_LM10_Runpod_POU.pdf) is the
  user-supplied screenshot of the RunPod billing page. It shows a credit
  transaction and account spending totals, but does not identify a training
  job, hardware allocation, output checkpoint, or link that activity to
  FutureTwin's models.

The repository material is useful context, but it does not independently prove
which RunPod job produced a checkpoint, its hardware, or when it ran.

## Evidence needed from the project owner

If SDC requires RunPod proof, supply genuine, authorized records from the
project owner's RunPod account:

- completed job/pod activity page and its date or run identifier;
- actual launch command and relevant logs, if retained;
- hardware details only when shown by the record;
- output checkpoint or artifact identifier that can be matched to the supplied
  model package.

The supplied screenshot visibly contains credit and spending amounts. Review
or redact those financial details before public submission if they are not
required by SDC. Also redact API keys, access tokens, and unrelated personal
information. Do not create an endpoint or invent missing logs, scripts, GPU
models, or job identifiers.
