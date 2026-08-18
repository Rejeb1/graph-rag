"""CLI: ingest data/documents/*.txt into Neo4j (graph) and Qdrant (vectors).

Usage: python scripts/build_index.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from groq import Groq

from src.config import DATA_DIR, GROQ_API_KEY
from src.ingestion.chunking import chunk_text
from src.ingestion.extraction import extract_graph
from src.ingestion.graph_index import add_extraction, close_driver, ensure_constraints
from src.ingestion.vector_index import get_client, index_chunks


def main() -> None:
    if not GROQ_API_KEY:
        print("GROQ_API_KEY is not set. Copy .env.example to .env and fill it in.")
        sys.exit(1)

    files = sorted(DATA_DIR.glob("*.txt"))
    if not files:
        print(f"No .txt files found in {DATA_DIR}.")
        return

    client = Groq(api_key=GROQ_API_KEY)
    ensure_constraints()
    qdrant_client = get_client()

    for path in files:
        text = path.read_text(encoding="utf-8").strip()
        if not text:
            continue
        print(f"Processing {path.name}...")

        chunks = chunk_text(text)
        index_chunks(qdrant_client, chunks, source=path.name)

        for chunk in chunks:
            extraction = extract_graph(client, chunk)
            add_extraction(extraction, source=path.name)

    close_driver()
    print("Done.")


if __name__ == "__main__":
    main()
