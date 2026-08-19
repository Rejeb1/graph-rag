from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)


def test_health_returns_ok():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ask_requires_a_question_field():
    response = client.post("/ask", json={})
    assert response.status_code == 422


def test_ask_rejects_wrong_types():
    response = client.post("/ask", json={"question": 123})
    assert response.status_code == 422


def test_docs_are_served():
    response = client.get("/docs")
    assert response.status_code == 200


def test_stats_endpoint_returns_expected_shape():
    response = client.get("/stats")
    assert response.status_code == 200
    body = response.json()
    assert "total_requests" in body
    assert "tier_counts" in body
    assert "avg_latency_seconds" in body
