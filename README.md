# Graph-RAG

Hybrid retrieval-augmented generation: a **knowledge graph** (Neo4j) fused with
**vector similarity search** (Qdrant), **complexity-based model routing**
(cheap/fast vs. capable/slow), and **automatic evaluation** (Ragas +
LLM-as-judge) comparing whether the graph and the routing actually help.

Runs entirely on free tiers — Groq, Neo4j AuraDB, Qdrant Cloud, Render — no
paid API, no credit card anywhere in the stack.

**Live API:** https://graph-rag-kn2i.onrender.com/docs
**Overview PDF:** see `Graph-RAG_Overview.pdf` if present, or ask for one.

## How it works

```
Documents --Groq extraction--> Neo4j (graph) + Qdrant (vectors)

Question --> NL-to-Cypher + vector search --> Fusion --> Router --> Groq --> Answer
```

1. **Ingestion** (`scripts/build_index.py`): an LLM extracts entities/relations
   from each document into Neo4j, while the same chunks are embedded into
   Qdrant.
2. **Retrieval** (`src/retrieval/`): each question is translated to a Cypher
   query by an LLM (falling back to a keyword-seeded graph walk if that
   fails), run against Neo4j; in parallel the question is embedded and
   matched against Qdrant. Both results are fused into one context block.
3. **Routing** (`src/routing/`): a free heuristic scores question complexity
   and picks a small/fast Groq model or a larger one — no LLM call spent
   just to decide.
4. **Generation** (`src/generation/`): the routed model answers from the
   fused context.
5. **Evaluation** (`src/evaluation/`, `scripts/run_benchmark.py`): runs a
   small Q&A set through 4 configurations (graph on/off × routing on/off),
   scoring each with Ragas (faithfulness, context precision) and a separate
   LLM-as-judge (correctness, relevance, groundedness).
6. **API** (`src/api/main.py`): FastAPI app exposing `POST /ask`, with
   structured logging, an in-memory `/stats` endpoint, and a per-IP rate
   limiter protecting the free-tier quotas.

## Setup

```bash
cp .env.example .env   # fill in your Groq/Neo4j/Qdrant credentials
python -m venv .venv && source .venv/Scripts/activate  # or .venv/bin/activate on macOS/Linux
pip install -r requirements.txt
pip install -r requirements-dev.txt   # for running tests

python scripts/build_index.py         # ingest data/documents/*.txt
uvicorn src.api.main:app --reload     # http://localhost:8000/docs
```

Credentials (all free, no card required):
- **Groq**: [console.groq.com](https://console.groq.com)
- **Neo4j AuraDB Free**: [console.neo4j.io](https://console.neo4j.io) — note the
  URI, username (newer Aura instances use the instance ID as the username,
  not `neo4j` — check the downloaded credentials file), and password.
- **Qdrant Cloud Free**: [cloud.qdrant.io](https://cloud.qdrant.io)

## Testing

```bash
pytest                  # unit tests only (default) — no external services needed
pytest -m live          # + integration tests against real Groq/Aura/Qdrant (needs .env)
```

CI (`.github/workflows/ci.yml`) runs the unit tests on every push; the
`live`-marked tests are skipped there since GitHub Actions has no real
credentials by default.

## Evaluation benchmark

```bash
pip install -r requirements-eval.txt
pip install --no-deps -r requirements-ragas.txt   # see that file for why --no-deps
python scripts/run_benchmark.py
```

Compares 4 pipeline configurations and writes a CSV/JSON table to `runs/`.
Note: Groq's free tier has both a per-minute and a per-day token budget —
`benchmark.py` paces requests to stay under the per-minute limit, but a very
active day can still hit the daily cap.

## Deployment

- **Render** (recommended, no card): `render.yaml` documents the service
  config; connect the GitHub repo in the Render dashboard, set the env vars
  from `.env` under Environment, deploy.
- **Cloud Run / AWS** (optional, requires a card for GCP/AWS billing):
  `scripts/deploy_cloud_run.sh` + `deploy/cloud-run.env.yaml.example`.
- **Local demo, zero setup**: `docker compose up` then
  `bash scripts/quick_tunnel.sh` for an instant public URL (Cloudflare quick
  tunnel, no account needed — temporary, for live demos only).

## Known limitations

- **No auth on `/ask`** — intentional, this is a public demo meant to be
  tried without a key. A per-IP rate limiter guards the free-tier quotas
  instead (`src/api/rate_limit.py`).
- **Corpus** (`data/documents/`): 8 original documents (~700 words each)
  summarizing the Model Context Protocol — architecture, primitives,
  transports, deprecations, ecosystem — chosen because it's directly
  relevant to the agentic-RAG space this project itself demonstrates. Large
  enough per document to exercise multi-chunk splitting (`chunking.py`) and
  cross-document multi-hop questions in the eval set.
- **Entity resolution across documents isn't perfect** — the same real-world
  entity can occasionally get extracted under slightly different names in
  separate LLM calls. The keyword-seeded graph fallback and vector search
  both help paper over this, but a dedicated entity-linking step would fix
  it properly.

## Tech stack

Groq · Neo4j AuraDB · Qdrant Cloud · FastAPI · Docker · Render ·
sentence-transformers (local embeddings) · Ragas · pytest
