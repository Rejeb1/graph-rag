from src.retrieval.fusion import format_graph_facts, format_vector_chunks, fuse


def test_format_graph_facts_empty():
    assert format_graph_facts([]) == "(no graph facts retrieved)"


def test_format_graph_facts_formats_triples():
    rows = [{"source": "Marie Curie", "relation": "MARRIED_TO", "target": "Pierre Curie"}]
    text = format_graph_facts(rows)
    assert "Marie Curie" in text
    assert "MARRIED_TO" in text
    assert "Pierre Curie" in text


def test_format_graph_facts_falls_back_for_non_triple_rows():
    rows = [{"o.name": "University of Paris"}]
    text = format_graph_facts(rows)
    assert "University of Paris" in text


def test_format_vector_chunks_empty():
    assert format_vector_chunks([]) == "(no matching document passages retrieved)"


def test_format_vector_chunks_includes_source():
    chunks = [{"text": "Marie Curie discovered radium.", "source": "sample.txt"}]
    text = format_vector_chunks(chunks)
    assert "sample.txt" in text
    assert "Marie Curie discovered radium." in text


def test_fuse_includes_both_sections():
    graph_rows = [{"source": "A", "relation": "REL", "target": "B"}]
    vector_chunks = [{"text": "some passage", "source": "doc.txt"}]
    context = fuse(graph_rows, vector_chunks)
    assert "Knowledge graph facts" in context
    assert "Retrieved document passages" in context
    assert "A --[REL]--> B" in context
    assert "some passage" in context
