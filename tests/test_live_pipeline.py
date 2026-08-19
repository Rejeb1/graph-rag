"""End-to-end tests against the real Groq/Neo4j Aura/Qdrant Cloud services.

Skipped automatically unless a real .env is present (CI has none by
default). Run locally with: pytest -m live
"""

import pytest
from groq import Groq

from src.config import GROQ_API_KEY, NEO4J_URI
from src.generation.generator import generate_answer
from src.retrieval.pipeline import retrieve
from src.routing.router import route

pytestmark = [
    pytest.mark.live,
    pytest.mark.skipif(
        not GROQ_API_KEY or GROQ_API_KEY == "test-dummy-key" or "localhost" in NEO4J_URI,
        reason="requires a real GROQ_API_KEY and a populated Aura/Qdrant Cloud instance (see .env.example)",
    ),
]


@pytest.fixture(scope="module")
def client() -> Groq:
    return Groq(api_key=GROQ_API_KEY)


def test_simple_question_routes_small_and_answers_correctly(client):
    question = "Where did Marie Curie study?"
    decision = route(question)
    assert decision.tier == "small"

    retrieval = retrieve(client, question)
    result = generate_answer(client, decision, question, retrieval["context"])
    assert "Paris" in result.answer


def test_complex_question_routes_large_and_answers_correctly(client):
    question = "Who did Marie Curie marry, and what did they win together?"
    decision = route(question)
    assert decision.tier == "large"

    retrieval = retrieve(client, question)
    result = generate_answer(client, decision, question, retrieval["context"])
    assert "Pierre" in result.answer


def test_cross_document_multihop_question_is_answered(client):
    question = "How is Frederic Joliot-Curie related to Marie Curie?"
    decision = route(question)

    retrieval = retrieve(client, question)
    assert retrieval["graph_rows"], "expected the graph fallback to find at least one fact"

    result = generate_answer(client, decision, question, retrieval["context"])
    assert "Irene" in result.answer or "daughter" in result.answer.lower()
