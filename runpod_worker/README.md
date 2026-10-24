# FutureTwin MiniLM — RunPod Serverless worker

Independent RunPod Serverless inference worker for the existing private
`futuretwin_embeddings/models/futuretwin_minilm` checkpoint. It accepts
`{"input":{"operation":"embed","texts":["text one","text two"]}}` and returns
normalized 384-dimensional vectors. It strips surrounding whitespace and uses
the checkpoint's saved tokenizer, pooling and normalization modules, matching
the local skill API. It requires the mounted fine-tuned checkpoint and never
downloads or substitutes the public base model.

## Docker build

Build from the GitHub repository root (not from this folder):

```bash
docker build -f runpod_worker/Dockerfile -t futuretwin-minilm-worker .
```

Python is pinned to 3.11.14 and Torch 2.14.1 is fetched from the official
CUDA 13.0 wheel index to match the existing runtime build. Sentence
Transformers 6.1.0, Transformers 5.20.2 and RunPod SDK 1.8.1 are pinned in
`requirements.txt`. Only the worker code and dependencies enter the image.

## Provision the private model

1. Create a private RunPod Network Volume in the same region/datacenter as the
   Serverless endpoint.
2. Start a temporary Pod attached to that volume and enable SSH access. From a
   trusted machine with the private checkpoint, transfer only its files using
   the authenticated connection shown in the RunPod Pod **Connect** UI:

   ```bash
   rsync -av --progress -e "ssh -i $RUNPOD_SSH_KEY -p $RUNPOD_SSH_PORT" \
     futuretwin_embeddings/models/futuretwin_minilm/ \
     "$RUNPOD_SSH_USER@$RUNPOD_SSH_HOST:/workspace/futuretwin_minilm/"
   ```

   Keep the SSH key and connection values outside Git and use the actual mount
   path shown by RunPod if different. Do not transfer user profiles, resumes or
   databases.
3. Verify the mounted directory has `modules.json`, `model.safetensors`,
   tokenizer/config files, `1_Pooling/` and `2_Normalize/`. Compare SHA-256
   checksums with the trusted source before removing the temporary Pod.
4. Build and push the image to a private registry. Configure registry access
   through RunPod's credential UI, not in source code.
5. Create a Serverless endpoint from that image and attach the same Network
   Volume. Set `FUTURETWIN_MODEL_PATH` to the actual mounted checkpoint path
   (the example above uses `/workspace/futuretwin_minilm`). The handler checks
   that the files exist and that output dimension is 384.
6. Send a test job to the authenticated endpoint `/run` with
   `{"input":{"operation":"embed","texts":["test text"]}}`; verify the vector
   dimension and unit norm. Keep endpoint URL and auth token in secret
   management. This repository does not create or deploy the endpoint.

Confirm RunPod's current volume mount, region compatibility, SSH and registry
steps in its UI/docs before provisioning; the provider can change those
controls. Storage and compute may incur charges.

## Local verification

With Python 3.11 and the pinned dependencies installed, run:

```bash
python -m unittest discover -s runpod_worker -p 'test_*.py' -v
FUTURETWIN_MODEL_PATH="$PWD/futuretwin_embeddings/models/futuretwin_minilm" \
  HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 \
  python -m unittest discover -s runpod_worker -p 'test_*.py' -v
```

The first runs validation and vector-shape tests with a stub. The second also
loads the private checkpoint locally. The model files remain excluded from
GitHub and must be provisioned separately in private mounted storage.
