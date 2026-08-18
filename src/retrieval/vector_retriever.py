"""Vector similarity retrieval over Qdrant."""

from src.config import QDRANT_COLLECTION, VECTOR_TOP_K
from src.ingestion.embeddings import embed_one
from src.ingestion.vector_index import get_client


def search(query: str, top_k: int = VECTOR_TOP_K) -> list[dict]:
    client = get_client()
    if not client.collection_exists(QDRANT_COLLECTION):
        return []
    vector = embed_one(query)
    hits = client.query_points(collection_name=QDRANT_COLLECTION, query=vector, limit=top_k).points
    return [{"text": h.payload["text"], "source": h.payload.get("source"), "score": h.score} for h in hits]
