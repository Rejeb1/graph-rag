from src.ingestion.graph_index import sanitize_identifier


def test_sanitize_identifier_passes_through_safe_names():
    assert sanitize_identifier("Person") == "Person"
    assert sanitize_identifier("WORKS_AT") == "WORKS_AT"


def test_sanitize_identifier_replaces_unsafe_characters():
    assert sanitize_identifier("Nobel Prize") == "Nobel_Prize"
    assert sanitize_identifier("married-to") == "married_to"


def test_sanitize_identifier_strips_leading_trailing_underscores():
    assert sanitize_identifier("  Concept  ") == "Concept"


def test_sanitize_identifier_falls_back_to_default_for_empty_or_all_unsafe():
    assert sanitize_identifier("", default="Entity") == "Entity"
    assert sanitize_identifier("!!!", default="RELATED_TO") == "RELATED_TO"


def test_sanitize_identifier_blocks_cypher_injection_characters():
    malicious = "Entity}) DETACH DELETE (n) //"
    cleaned = sanitize_identifier(malicious)
    for char in ("}", ")", "(", " ", "/"):
        assert char not in cleaned
