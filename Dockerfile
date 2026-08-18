FROM python:3.12-slim

WORKDIR /app

# Fixed, world-readable cache location — avoids depending on $HOME, which
# differs between the build user (root) and the UID a given platform runs
# the container as at runtime (Hugging Face Spaces always uses UID 1000,
# regardless of any USER directive).
ENV HF_HOME=/app/.cache/huggingface

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download and cache the embedding model at build time, not at container
# start — Cloud Run and HF Spaces both run ephemeral containers, so a
# runtime download would repeat on every cold start. Keep this model name in
# sync with EMBEDDING_MODEL in src/config.py.
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"

COPY . .

# Make sure every file is readable regardless of which UID actually runs the
# container (root here at build time; UID 1000 on Hugging Face Spaces).
RUN chmod -R a+rX /app

EXPOSE 8000

# $PORT is set by Cloud Run / App Runner and defaults to 8000 otherwise.
# Hugging Face Spaces has no such var — its default port is 7860, pinned to
# 8000 instead via app_port in README.md to match this default.
CMD ["sh", "-c", "uvicorn src.api.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
