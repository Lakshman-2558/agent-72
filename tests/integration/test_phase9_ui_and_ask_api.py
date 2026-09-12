"""Integration tests for Phase 9 UI and Grounded Strategic Inquiry API."""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def test_institution(client: TestClient):
    """Creates a test institution for Phase 9 integration tests."""
    payload = {
        "code": "TEST-PHASE9-INST",
        "name": "Phase 9 Test Institute of Strategy",
        "institution_type": "UNIVERSITY",
        "jurisdiction": "Regional",
    }
    res = client.post("/api/v1/organizations/institutions", json=payload)
    assert res.status_code in (200, 201)
    return res.json()


def test_ask_agent_72_underperformance_query(client: TestClient, test_institution):
    """Verifies that asking about underperformance returns real evidence and leadership disclaimer."""
    inst_id = test_institution["id"]
    payload = {
        "institution_id": inst_id,
        "query": "Where are we currently underperforming?",
        "analysis_period": "2024-2025",
    }
    response = client.post("/api/v1/analysis/ask", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert len(data["answer"]) > 0
    assert "confidence" in data
    assert "leadership_disclaimer" in data
    assert "decision-support" in data["leadership_disclaimer"].lower()
    assert "suggested_questions" in data
    assert len(data["suggested_questions"]) > 0


def test_ask_agent_72_risks_query(client: TestClient, test_institution):
    """Verifies that asking about strategic risks returns grounded intelligence."""
    inst_id = test_institution["id"]
    payload = {
        "institution_id": inst_id,
        "query": "What strategic risks should leadership focus on?",
    }
    response = client.post("/api/v1/analysis/ask", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert len(data["answer"]) > 0
    assert data["confidence"] > 0.0


def test_get_latest_plan_review_endpoint_not_found(client: TestClient, test_institution):
    """Verifies 404 behavior when plan has no reviews recorded."""
    # Create a plan with no reviews
    plan_payload = {
        "institution_id": test_institution["id"],
        "institution_name": test_institution["name"],
        "title": "Phase 9 Initial Plan",
        "horizon_start_year": 2026,
        "horizon_end_year": 2030,
    }
    create_res = client.post("/api/v1/plans", json=plan_payload)
    assert create_res.status_code == 201

    plan_id = create_res.json()["id"]

    review_res = client.get(f"/api/v1/plans/{plan_id}/review/latest")
    assert review_res.status_code == 404
    assert "No execution reviews have been recorded" in review_res.json()["detail"]


def test_ui_endpoint_serves_html(client: TestClient):
    """Verifies that /ui serves the React SPA index.html with Agent 72 title."""
    res = client.get("/ui")
    assert res.status_code == 200
    assert "Agent 72" in res.text
    assert "<div id=\"root\"></div>" in res.text

