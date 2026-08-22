"""CLI: ingest data/documents/*.txt and *.pdf into Neo4j (graph) and Qdrant (vectors).

Usage:
    python scripts/build_index.py            # ingest everything
    python scripts/build_index.py --dry-run  # show file/chunk counts only, no Groq calls

PDF support needs an extra dependency not in the main requirements.txt (see
requirements-ingestion.txt for why):
    pip install -r requirements-ingestion.txt
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

# Every chunk costs one Groq extraction call; large/many documents can add up
# fast against the free-tier's daily token budget. Not a hard stop — just a
# heads-up before an unattended run burns through it.
CHUNK_COUNT_WARNING_THRESHOLD = 40


def load_text(path: Path) -> str:
    if path.suffix.lower() == ".pdf":
        try:
            from src.ingestion.pdf_loader import extract_pdf_text
        except ImportError:
            print("PDF support needs pypdf: pip install -r requirements-ingestion.txt")
            sys.exit(1)
        return extract_pdf_text(path)
    return path.read_text(encoding="utf-8").strip()


def main() -> None:
    dry_run = "--dry-run" in sys.argv

    files = sorted(DATA_DIR.glob("*.txt")) + sorted(DATA_DIR.glob("*.pdf"))
    if not files:
        print(f"No .txt or .pdf files found in {DATA_DIR}.")
        return

    plan = []
    for path in files:
        text = load_text(path)
        if not text:
            continue
        chunks = chunk_text(text)
        plan.append((path, chunks))

    total_chunks = sum(len(chunks) for _, chunks in plan)
    print(f"{len(plan)} document(s), {total_chunks} chunk(s) total (1 Groq extraction call per chunk):")
    for path, chunks in plan:
        print(f"  {path.name}: {len(chunks)} chunk(s)")

    if total_chunks > CHUNK_COUNT_WARNING_THRESHOLD:
        print(
            f"\nWarning: {total_chunks} chunks is a lot of extraction calls — "
            "Groq's free tier caps total tokens per day as well as per minute; "
            "a run this size can hit that cap partway through."
        )

    if dry_run:
        print("\n--dry-run: stopping before any Groq calls.")
        return

    if not GROQ_API_KEY:
        print("\nGROQ_API_KEY is not set. Copy .env.example to .env and fill it in.")
        sys.exit(1)

    print()
    client = Groq(api_key=GROQ_API_KEY)
    ensure_constraints()
    qdrant_client = get_client()

    for path, chunks in plan:
        print(f"Processing {path.name} ({len(chunks)} chunk(s))...")
        index_chunks(qdrant_client, chunks, source=path.name)

        for i, chunk in enumerate(chunks, start=1):
            print(f"  extracting chunk {i}/{len(chunks)}...")
            extraction = extract_graph(client, chunk)
            add_extraction(extraction, source=path.name)

    close_driver()
    print("Done.")


if __name__ == "__main__":
    main()
