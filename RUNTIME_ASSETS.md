# Private runtime assets and restoration

Model weights and local SQLite files remain on the working server, but are not
part of the public source export. **Do not delete them or rotate SESSION_SECRET.**

## Required assets

`runtime-assets.json` records every required file's path, size and SHA-256:

| Path | Role |
|---|---|
| `futuretwin_embeddings/models/futuretwin_minilm/` | Active fine-tuned local MiniLM, tokenizer, pooling and normalization configuration |
| `futuretwin_embeddings/models/distilbert_v2/` | Active DistilBERT V2 checkpoint plus package/training/evaluation provenance; these provenance documents are not disposable experiments |
| `generated-artifacts/onet_task_exposure.sqlite3` | Precomputed public O*NET/ESCO task inventory and checkpoint-bound predictions; **not** a private profile database |

The ESCO source CSVs, compressed O*NET source/mapping files, embedding skill
catalog, label-provenance contract and SQL migrations remain in source control.
The separate `generated-artifacts/distilbert_predictions.sqlite3` cache can be
rebuilt by inference; do not confuse it with the required occupation inventory.

## Where the current copies are stored

The active files are at the exact workspace-relative paths above. A protected
pre-cleanup snapshot is stored **locally**, outside the source export, at:

`generated-artifacts/github-preparation-backup/workspace-before-cleanup.tar`

This backup contains other local application files and is **not a public download
or a public model distribution**. Do not upload the entire backup to GitHub.
The local generated-artifacts directory was excluded from that snapshot; the
O*NET inventory is preserved separately at its active path. The cleanup does not
modify it. The maintainer must separately back it up with the asset package below.
No public URL for the custom fine-tuned checkpoints is assumed or invented.

## Create a model-only transfer package

Run from the original working checkout, after verifying the manifest:

```bash
python scripts/check_runtime_assets.py
tar -cf generated-artifacts/futuretwin-runtime-assets.tar \
  futuretwin_embeddings/models/futuretwin_minilm \
  futuretwin_embeddings/models/distilbert_v2 \
  generated-artifacts/onet_task_exposure.sqlite3
sha256sum generated-artifacts/futuretwin-runtime-assets.tar
```

Keep this archive in access-controlled storage, not Git. On a fresh checkout,
obtain it directly from the project maintainer, verify its transfer checksum
through a trusted channel, then restore **only that trusted package**:

```bash
tar -tf /secure/path/futuretwin-runtime-assets.tar
tar -xf /secure/path/futuretwin-runtime-assets.tar -C /path/to/futuretwin
cd /path/to/futuretwin
python scripts/check_runtime_assets.py
```

Do not extract untrusted archives or replace/check off mismatched files.
Do not run `--write-manifest` merely to bypass a failed check.

## Runtime and deployment notes

- Local inference explicitly uses CPU. The existing torch build is pinned
  because the task-inventory provenance includes its exact version. A CPU-only
  wheel with a different version suffix is **not** silently interchangeable.
  A future change needs an explicit inference-parity/provenance migration.
- MiniLM and DistilBERT fail closed if their checkpoint is missing; no paid
  service or unrelated base model is a fallback.
- Speech recognition uses self-hosted faster-whisper. With the default `small`
  model, public weights may be downloaded on first use. For an offline server,
  provision a complete faster-whisper checkpoint first and set
  `FUTURETWIN_WHISPER_MODEL` to its local directory. This is a free weight
  download, not hosted inference.
- Deployment must provision these files **before** starting Gunicorn.
  `.replitignore` deliberately includes active checkpoint directories and the
  one required O*NET SQLite inventory while excluding other generated output.
- PostgreSQL records are not in the source export or this model-only archive.
  Back up/restore PostgreSQL privately using the database operator's procedure;
  preserve the original `SESSION_SECRET` to retain access to encrypted profiles.
