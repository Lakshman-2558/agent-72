"""Integration tests for Health and API Documentation endpoints."""

from fastapi.testclient import TestClient


def test_health_readiness_probe(client: TestClient):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "dependencies" in data
    assert data["dependencies"]["database"]["status"] == "healthy"
    assert data["dependencies"]["ai_provider"]["status"] == "healthy"


def test_health_liveness_probe(client: TestClient):
    response = client.get("/api/v1/health/live")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "alive"
    assert "uptime_seconds" in data


def test_openapi_schema_endpoint(client: TestClient):
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert schema["info"]["title"] == "Agent 72: Strategic Planning Agent"
    assert "/api/v1/health" in schema["paths"]
    assert "/api/v1/plans" in schema["paths"]


def test_swagger_docs_endpoint(client: TestClient):
    response = client.get("/docs")
    assert response.status_code == 200
    assert "swagger-ui" in response.text.lower()


def test_root_endpoint(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert data["docs"] == "/docs"
