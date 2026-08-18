#!/usr/bin/env bash
# Expose the locally running API via a free Cloudflare quick tunnel — no
# account, no card, no signup. Good for a live demo (e.g. during an
# interview); NOT a stable link, since the URL changes every run and only
# works while this machine and this script keep running. For a persistent
# link, use Render.com instead (see the chat instructions / project notes).
#
# Prerequisite: the API must already be running and reachable at the given
# local port — e.g. `docker compose up` (see docker-compose.yml) or
# `uvicorn src.api.main:app --port 8000` in another terminal.
#
# Usage: bash scripts/quick_tunnel.sh [port]

set -euo pipefail

PORT="${1:-8000}"

if ! command -v cloudflared >/dev/null 2>&1; then
  echo "cloudflared not found. Install it first:"
  echo "  - Windows (winget): winget install --id Cloudflare.cloudflared"
  echo "  - macOS (brew):     brew install cloudflared"
  echo "  - Linux:            see https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/"
  exit 1
fi

if ! curl -sf "http://localhost:${PORT}/health" >/dev/null; then
  echo "Nothing answering at http://localhost:${PORT}/health — start the API first"
  echo "(docker compose up, or: uvicorn src.api.main:app --port ${PORT})"
  exit 1
fi

echo "Starting quick tunnel for http://localhost:${PORT} ..."
echo "Watch the output below for the public https://*.trycloudflare.com URL."
cloudflared tunnel --url "http://localhost:${PORT}"
