"""Paragraph-based chunking with a soft character limit."""


def chunk_text(text: str, max_chars: int = 1500) -> list[str]:
    """Split `text` into chunks along paragraph breaks, each up to `max_chars`.

    A single paragraph longer than `max_chars` is kept whole rather than cut
    mid-sentence — entity/relation extraction and embeddings both tolerate a
    chunk somewhat over the target size better than a chunk cut mid-thought.
    """
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks: list[str] = []
    current = ""

    for paragraph in paragraphs:
        if current and len(current) + len(paragraph) + 2 > max_chars:
            chunks.append(current)
            current = paragraph
        else:
            current = f"{current}\n\n{paragraph}" if current else paragraph

    if current:
        chunks.append(current)

    return chunks
