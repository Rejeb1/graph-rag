"""Execute Cypher against Neo4j, plus a keyword-seeded k-hop fallback."""

from neo4j import Driver

from src.config import GRAPH_HOPS
from src.ingestion.graph_index import get_driver

_FORBIDDEN = ("CREATE", "MERGE", "DELETE", "SET ", "REMOVE", "DROP", "CALL APOC", "LOAD CSV")


def is_read_only(cypher: str) -> bool:
    upper = cypher.upper()
    return bool(cypher.strip()) and not any(keyword in upper for keyword in _FORBIDDEN)


def get_schema_summary(driver: Driver | None = None) -> str:
    driver = driver or get_driver()
    with driver.session() as session:
        labels = [r["label"] for r in session.run("CALL db.labels() YIELD label RETURN label")]
        rel_types = [
            r["relationshipType"]
            for r in session.run("CALL db.relationshipTypes() YIELD relationshipType RETURN relationshipType")
        ]
    return f"Node labels: {', '.join(labels) or '(none yet)'}\nRelationship types: {', '.join(rel_types) or '(none yet)'}"


def run_cypher(cypher: str, driver: Driver | None = None, limit: int = 25) -> list[dict]:
    """Execute a read-only Cypher query. Raises ValueError if it looks like a write."""
    if not is_read_only(cypher):
        raise ValueError("Generated Cypher looks like a write query; refusing to execute it.")
    driver = driver or get_driver()
    with driver.session() as session:
        result = session.run(cypher)
        return [record.data() for record in result][:limit]


def keyword_seed_triples(
    query: str, driver: Driver | None = None, hops: int = GRAPH_HOPS, limit: int = 25
) -> list[dict]:
    """Fallback used when NL->Cypher fails or returns nothing: find entities
    whose name appears in the query text, then expand `hops` hops around them.
    """
    driver = driver or get_driver()
    with driver.session() as session:
        names = [r["name"] for r in session.run("MATCH (e:Entity) RETURN e.name AS name")]
    seeds = [n for n in names if n and n.lower() in query.lower()]
    if not seeds:
        return []

    with driver.session() as session:
        result = session.run(
            f"MATCH (s:Entity)-[rels*1..{hops}]-(:Entity) WHERE s.name IN $seeds "
            "UNWIND rels AS rel "
            "RETURN DISTINCT startNode(rel).name AS source, coalesce(rel.label, type(rel)) AS relation, "
            "endNode(rel).name AS target "
            "LIMIT $limit",
            seeds=seeds,
            limit=limit,
        )
        return [record.data() for record in result]
