"""Integration tests for Strategic Plans API."""

from fastapi.testclient import TestClient


def test_create_and_retrieve_strategic_plan(client: TestClient):
    payload = {
        "title": "Institutional Vision 2030",
        "institution_name": "Apex University",
        "horizon_start_year": 2026,
        "horizon_end_year": 2030,
        "vision_statement": "To become a premier research and innovation institution.",
        "mission_statement": "Deliver transformative education with industrial synergy.",
        "objectives": [
            {
                "title": "NIRF Top 50 Engineering Rank",
                "description": "Achieve milestone ranking in National Institutional Ranking Framework",
                "target_metric": "NIRF Rank Score",
                "baseline_value": 78.5,
                "target_value": 45.0,
                "weight": 2.5,
                "owner": "Dean of Academic Quality",
            }
        ],
        "strategic_options": [
            {
                "title": "Establish Advanced AI Research Center",
                "rationale": "High employer demand and multidisciplinary grant opportunities",
                "resource_intensity": "HIGH",
                "estimated_cost": 5000000.0,
                "risk_level": "MEDIUM",
            }
        ],
        "scenarios": [
            {
                "name": "Base Scenario",
                "description": "Continued steady state growth with existing budget allocations",
                "assumptions": "Admission demand remains stable at 94% seat intake",
                "projected_outcome": "Steady incremental improvement across key indicators",
            }
        ],
    }

    # 1. Create plan
    response = client.post("/api/v1/plans", json=payload)
    assert response.status_code == 201, response.text
    created = response.json()
    plan_id = created["id"]
    assert plan_id is not None
    assert created["title"] == "Institutional Vision 2030"
    assert created["institution_name"] == "Apex University"
    assert len(created["objectives"]) == 1
    assert created["objectives"][0]["target_metric"] == "NIRF Rank Score"
    assert len(created["strategic_options"]) == 1
    assert len(created["scenarios"]) == 1

    # 2. Get plan by ID
    get_res = client.get(f"/api/v1/plans/{plan_id}")
    assert get_res.status_code == 200
    plan_data = get_res.json()
    assert plan_data["id"] == plan_id
    assert plan_data["title"] == "Institutional Vision 2030"

    # 3. List plans
    list_res = client.get("/api/v1/plans")
    assert list_res.status_code == 200
    list_data = list_res.json()
    assert list_data["total"] >= 1
    assert any(p["id"] == plan_id for p in list_data["items"])

    # 4. Update plan
    update_res = client.put(
        f"/api/v1/plans/{plan_id}",
        json={"title": "Updated Vision 2030 Title", "status": "APPROVED"},
    )
    assert update_res.status_code == 200
    updated_data = update_res.json()
    assert updated_data["title"] == "Updated Vision 2030 Title"
    assert updated_data["status"] == "APPROVED"

    # 5. Delete plan
    del_res = client.delete(f"/api/v1/plans/{plan_id}")
    assert del_res.status_code == 204

    # 6. Verify plan is gone
    gone_res = client.get(f"/api/v1/plans/{plan_id}")
    assert gone_res.status_code == 404
    error_data = gone_res.json()
    assert error_data["error"]["code"] == "EntityNotFoundException"


def test_create_plan_invalid_horizon(client: TestClient):
    payload = {
        "title": "Invalid Year Plan",
        "institution_name": "Apex University",
        "horizon_start_year": 2030,
        "horizon_end_year": 2025,
    }
    response = client.post("/api/v1/plans", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert "error" in data


def test_get_nonexistent_plan(client: TestClient):
    response = client.get("/api/v1/plans/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404
    data = response.json()
    assert data["error"]["code"] == "EntityNotFoundException"
