from src.ingestion.chunking import chunk_text


def test_empty_text_yields_no_chunks():
    assert chunk_text("") == []
    assert chunk_text("   \n\n  ") == []


def test_short_text_is_a_single_chunk():
    text = "Marie Curie was a physicist and chemist."
    assert chunk_text(text, max_chars=1500) == [text]


def test_paragraphs_within_limit_are_merged_into_one_chunk():
    text = "Paragraph one.\n\nParagraph two.\n\nParagraph three."
    chunks = chunk_text(text, max_chars=1500)
    assert len(chunks) == 1
    assert "Paragraph one." in chunks[0]
    assert "Paragraph three." in chunks[0]


def test_splits_into_multiple_chunks_once_over_the_limit():
    paragraphs = [f"Paragraph {i} " + ("x" * 40) for i in range(10)]
    text = "\n\n".join(paragraphs)
    chunks = chunk_text(text, max_chars=100)
    assert len(chunks) > 1
    # every paragraph's content survives somewhere in the output
    joined = "\n\n".join(chunks)
    for p in paragraphs:
        assert p in joined


def test_oversized_single_paragraph_is_kept_whole_not_cut_mid_sentence():
    huge_paragraph = "word " * 500  # far over any reasonable max_chars
    chunks = chunk_text(huge_paragraph, max_chars=100)
    assert len(chunks) == 1
    assert chunks[0].strip() == huge_paragraph.strip()
