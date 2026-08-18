Hybrid Graph-RAG: Neo4j + Qdrant retrieval fusion, NL-to-Cypher translation,
complexity-based model routing (Groq), and Ragas/LLM-as-judge evaluation.
Runs entirely on free tiers — no paid API, no credit card anywhere in the
stack. See `.env.example` for required config and `scripts/` for
ingestion, benchmarking, and deployment helpers.

Interactive API docs at `/docs` once running (`uvicorn src.api.main:app`).
