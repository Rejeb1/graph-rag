"""Write extracted entities/relations into Neo4j."""

import re

from neo4j import Driver, GraphDatabase

from src.config import NEO4J_PASSWORD, NEO4J_URI, NEO4J_USER

_driver: Driver | None = None


def get_driver() -> Driver:
    global _driver
    if _driver is None:
        _driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    return _driver


def close_driver() -> None:
    global _driver
    if _driver is not None:
        _driver.close()
        _driver = None


_SAFE = re.compile(r"[^A-Za-z0-9_]")


def sanitize_identifier(raw: str, default: str = "Entity") -> str:
    """Turn arbitrary LLM output into a safe Neo4j label / relationship type.

    Cypher does not support parameterizing labels or relationship types, so
    any value that gets interpolated into a query string must be restricted
    to [A-Za-z0-9_] first — otherwise extracted text could inject Cypher.
    """
    cleaned = _SAFE.sub("_", raw.strip()).strip("_")
    return cleaned or default


def ensure_constraints(driver: Driver | None = None) -> None:
    driver = driver or get_driver()
    with driver.session() as session:
        session.run("CREATE CONSTRAINT entity_name IF NOT EXISTS FOR (e:Entity) REQUIRE e.name IS UNIQUE")


def add_extraction(extraction: dict, source: str, driver: Driver | None = None) -> None:
    """Merge one chunk's extracted entities/relations into Neo4j.

    Every node gets the generic `:Entity` label (unique on `name`) plus its
    specific type label, so retrieval queries can match `:Entity` without
    knowing the type ahead of time.
    """
    driver = driver or get_driver()
    with driver.session() as session:
        for entity in extraction.get("entities", []):
            name = entity.get("name", "").strip()
            if not name:
                continue
            label = sanitize_identifier(entity.get("type", "Entity"))
            # MERGE matches only on the stable identity (:Entity + name) —
            # the uniqueness constraint is on that pair. Adding the
            # type-specific label is a separate SET so the same entity
            # extracted with a different `type` in another chunk (e.g. once
            # as "Concept", once as "Award") still resolves to one node
            # instead of violating the constraint trying to MERGE a second
            # node under a different label combination.
            session.run(
                f"MERGE (e:Entity {{name: $name}}) SET e.type = $type SET e:{label}",
                name=name,
                type=entity.get("type", "Entity"),
            )

        for relation in extraction.get("relations", []):
            src = relation.get("source", "").strip()
            tgt = relation.get("target", "").strip()
            if not src or not tgt:
                continue
            rel_type = sanitize_identifier(relation.get("relation", "RELATED_TO"), default="RELATED_TO")
            session.run(
                "MERGE (s:Entity {name: $src}) "
                "MERGE (t:Entity {name: $tgt}) "
                f"MERGE (s)-[r:{rel_type}]->(t) "
                "SET r.source = $source, r.label = $label",
                src=src,
                tgt=tgt,
                source=source,
                label=relation.get("relation", "related to"),
            )
