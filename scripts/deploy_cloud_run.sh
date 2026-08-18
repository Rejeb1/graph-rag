#!/usr/bin/env bash
# Deploy the FastAPI app (src/api/main.py) to Google Cloud Run.
#
# Prerequisites (see the chat instructions for the manual signup steps):
#   1. A Neo4j AuraDB free-tier instance and a Qdrant Cloud free-tier cluster.
#   2. deploy/cloud-run.env.yaml filled in from deploy/cloud-run.env.yaml.example.
#   3. gcloud CLI installed and authenticated (`gcloud auth login`), or run
#      this from Google Cloud Shell, which has gcloud pre-installed and
#      pre-authenticated — no local install needed.
#   4. A GCP project with billing enabled (Cloud Run's free tier does not
#      require a paid plan to be *used*, but a billing account must be
#      linked to the project to enable the Cloud Run API).
#
# This script only builds and deploys — it does not create any accounts,
# projects, or database instances. Those are manual steps in each console.

set -euo pipefail

SERVICE_NAME="graph-rag-api"
REGION="us-central1"   # Cloud Run free tier applies in us-central1, us-east1, us-west1
ENV_FILE="deploy/cloud-run.env.yaml"

cd "$(dirname "$0")/.."

if [ ! -f "$ENV_FILE" ]; then
  echo "Missing $ENV_FILE — copy deploy/cloud-run.env.yaml.example and fill in your values first."
  exit 1
fi

if ! command -v gcloud >/dev/null 2>&1; then
  echo "gcloud CLI not found. Install it, or run this script from Google Cloud Shell instead."
  exit 1
fi

PROJECT="$(gcloud config get-value project 2>/dev/null)"
if [ -z "$PROJECT" ] || [ "$PROJECT" = "(unset)" ]; then
  echo "No active gcloud project. Run: gcloud config set project YOUR_PROJECT_ID"
  exit 1
fi

echo "Deploying $SERVICE_NAME to project $PROJECT in $REGION..."

gcloud run deploy "$SERVICE_NAME" \
  --source . \
  --region "$REGION" \
  --allow-unauthenticated \
  --env-vars-file "$ENV_FILE" \
  --memory 1Gi \
  --timeout 120

echo "Done. Swagger docs: run 'gcloud run services describe $SERVICE_NAME --region $REGION --format=\"value(status.url)\"' then open <url>/docs"
