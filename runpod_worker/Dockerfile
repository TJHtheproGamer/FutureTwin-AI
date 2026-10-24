FROM python:3.11.14-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HF_HUB_OFFLINE=1 \
    TRANSFORMERS_OFFLINE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# The build context is the repository root; do not COPY the Flask app,
# development databases, or private model files into this image.
COPY runpod_worker/requirements.txt /app/requirements.txt

# Match the existing runtime's torch 2.14.1+cu130 build. Runtime model files
# are mounted separately; no checkpoint or credentials are baked into the image.
RUN pip install --index-url https://download.pytorch.org/whl/cu130 \
      torch==2.14.1 && \
    pip install --index-url https://pypi.org/simple \
      -r /app/requirements.txt

COPY runpod_worker/handler.py /app/handler.py

CMD ["python", "-u", "/app/handler.py"]
