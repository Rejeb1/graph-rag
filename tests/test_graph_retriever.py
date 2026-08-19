from src.retrieval.graph_retriever import is_read_only


def test_read_only_match_return_is_allowed():
    assert is_read_only("MATCH (n:Entity) RETURN n LIMIT 10") is True


def test_empty_query_is_not_read_only():
    assert is_read_only("") is False
    assert is_read_only("   ") is False


def test_create_is_rejected():
    assert is_read_only("CREATE (n:Entity {name: 'x'}) RETURN n") is False


def test_merge_is_rejected():
    assert is_read_only("MERGE (n:Entity {name: 'x'}) RETURN n") is False


def test_delete_is_rejected():
    assert is_read_only("MATCH (n) DETACH DELETE n") is False


def test_set_is_rejected():
    assert is_read_only("MATCH (n:Entity {name: 'x'}) SET n.hacked = true RETURN n") is False


def test_case_insensitive_detection():
    assert is_read_only("match (n) create (m) return n") is False
