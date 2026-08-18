"""Translate a natural-language question into a read-only Cypher query.

This is the NL-to-QL layer — the piece Graph-RAG demos usually skip and that
ChapsVision's agentic-RAG framing calls out explicitly.
"""

from groq import Groq

from src.config import LARGE_MODEL
from src.retrieval.graph_retriever import get_schema_summary, is_read_only

SYSTEM_PROMPT = (
    "You translate natural-language questions into a single read-only Cypher "
    "query against a Neo4j knowledge graph. Every node carries the generic "
    "label :Entity plus a specific type label, and a `name` property. "
    "Relationships carry a `label` property with the human-readable relation "
    "text (their Cypher type is an UPPER_SNAKE_CASE version of the same "
    "text). Only ever write MATCH / WHERE / WITH / RETURN / ORDER BY / LIMIT "
    "clauses — never CREATE, MERGE, DELETE, SET, REMOVE, or DROP. Always "
    "include a LIMIT. Return ONLY the Cypher query — no explanation, no "
    "markdown fences."
)


def question_to_cypher(client: Groq, question: str) -> str | None:
    schema = get_schema_summary()
    response = client.chat.completions.create(
        model=LARGE_MODEL,
        max_tokens=512,
        messages=[
            {"role": "system", "content": f"{SYSTEM_PROMPT}\n\nGraph schema:\n{schema}"},
            {"role": "user", "content": question},
        ],
    )
    cypher = response.choices[0].message.content.strip()
    cypher = cypher.removeprefix("```cypher").removeprefix("```").removesuffix("```").strip()
    if not is_read_only(cypher):
        return None
    return cypher
