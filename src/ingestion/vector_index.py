"""Embed chunks and upsert them into Qdrant."""

import uuid

from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels

from src.config import EMBEDDING_DIM, QDRANT_API_KEY, QDRANT_COLLECTION, QDRANT_URL
from src.ingestion.embeddings import embed


def get_client() -> QdrantClient:
    return QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY or None)


def ensure_collection(client: QdrantClient) -> None:
    if client.collection_exists(QDRANT_COLLECTION):
        return
    client.create_collection(
        collection_name=QDRANT_COLLECTION,
        vectors_config=qmodels.VectorParams(size=EMBEDDING_DIM, distance=qmodels.Distance.COSINE),
    )


def index_chunks(client: QdrantClient, chunks: list[str], source: str) -> None:
    if not chunks:
        return
    ensure_collection(client)
    vectors = embed(chunks)
    points = [
        qmodels.PointStruct(id=str(uuid.uuid4()), vector=vector, payload={"text": chunk, "source": source})
        for chunk, vector in zip(chunks, vectors)
    ]
    client.upsert(collection_name=QDRANT_COLLECTION, points=points)
