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
    question = "What is the MCP Inspector used for?"
    decision = route(question)
    assert decision.tier == "small"

    retrieval = retrieve(client, question)
    result = generate_answer(client, decision, question, retrieval["context"])
    assert "inspector" in result.answer.lower() or "debugg" in result.answer.lower() or "test" in result.answer.lower()


def test_complex_question_routes_large_and_answers_correctly(client):
    question = (
        "Which client-side features were deprecated in protocol version 2026-07-28, "
        "and what should replace each of them?"
    )
    decision = route(question)
    assert decision.tier == "large"

    retrieval = retrieve(client, question)
    result = generate_answer(client, decision, question, retrieval["context"])
    lowered = result.answer.lower()
    assert "roots" in lowered or "sampling" in lowered


def test_cross_document_multihop_question_is_answered(client):
    question = "How does a client find out when a server's tool list changes, and what does it do next?"
    decision = route(question)

    retrieval = retrieve(client, question)
    assert retrieval["graph_rows"] or retrieval["vector_chunks"], "expected some retrieved context"

    result = generate_answer(client, decision, question, retrieval["context"])
    assert "list" in result.answer.lower()
