import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data" / "documents"

# --- LLM provider ---
# Everything runs on Groq: free, no card required, generous rate limits.
# (Claude/OpenAI were deliberately dropped from the running pipeline — both
# are pay-per-token with no perpetual free tier. Ragas's evaluator LLM is
# also routed through Groq, via litellm, in src/evaluation/ragas_eval.py.)
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

LARGE_MODEL = "openai/gpt-oss-120b"  # supports strict JSON-schema outputs: extraction, NL->Cypher, judging, complex answers
SMALL_MODEL = "openai/gpt-oss-20b"  # fast/cheap tier for simple, routine answers (llama-3.1-8b-instant was retired by Groq)

# --- Neo4j (knowledge graph) ---
NEO4J_URI = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.environ.get("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "password")

# --- Qdrant (vector store) ---
QDRANT_URL = os.environ.get("QDRANT_URL", "http://localhost:6333")
QDRANT_API_KEY = os.environ.get("QDRANT_API_KEY")  # unset for local/self-hosted Qdrant
QDRANT_COLLECTION = os.environ.get("QDRANT_COLLECTION", "graph_rag_chunks")

# Local, free sentence-transformers model — no embedding API key required.
EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
EMBEDDING_DIM = 384  # matches all-MiniLM-L6-v2

# --- Routing ---
# Below this complexity score (0-1), route to SMALL_MODEL; at or above, route to LARGE_MODEL.
ROUTING_THRESHOLD = float(os.environ.get("ROUTING_THRESHOLD", "0.5"))

# --- Retrieval ---
VECTOR_TOP_K = 5
GRAPH_HOPS = 2
