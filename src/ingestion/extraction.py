"""Entity/relation extraction from a text chunk, via Groq structured outputs."""

import json

from groq import Groq

from src.config import LARGE_MODEL

EXTRACTION_SCHEMA = {
    "type": "object",
    "properties": {
        "entities": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "type": {
                        "type": "string",
                        "description": "e.g. Person, Organization, Place, Concept, Event. Used as the Neo4j label.",
                    },
                },
                "required": ["name", "type"],
                "additionalProperties": False,
            },
        },
        "relations": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "source": {"type": "string", "description": "Must match an entity name from `entities`."},
                    "relation": {
                        "type": "string",
                        "description": "Short UPPER_SNAKE_CASE relationship type, e.g. WORKS_AT, LOCATED_IN.",
                    },
                    "target": {"type": "string", "description": "Must match an entity name from `entities`."},
                },
                "required": ["source", "relation", "target"],
                "additionalProperties": False,
            },
        },
    },
    "required": ["entities", "relations"],
    "additionalProperties": False,
}

SYSTEM_PROMPT = (
    "Extract entities and the relations between them from the given text, for "
    "loading into a Neo4j knowledge graph. Use concise, canonical entity names "
    "so the same real-world entity is named identically across separate calls "
    "(e.g. always 'Marie Curie', not sometimes 'Curie' or 'Madame Curie'). "
    "Entity `type` becomes a Neo4j node label — use PascalCase. Relation names "
    "become Neo4j relationship types — use UPPER_SNAKE_CASE verb phrases (e.g. "
    "WORKS_AT, LOCATED_IN, MARRIED_TO). Every relation's source and target must "
    "exactly match a name in `entities`."
)


def extract_graph(client: Groq, text: str) -> dict:
    """Return {"entities": [...], "relations": [...]} extracted from `text`."""
    response = client.chat.completions.create(
        model=LARGE_MODEL,
        max_tokens=4096,
        response_format={
            "type": "json_schema",
            "json_schema": {"name": "graph_extraction", "strict": True, "schema": EXTRACTION_SCHEMA},
        },
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": text},
        ],
    )
    return json.loads(response.choices[0].message.content)
