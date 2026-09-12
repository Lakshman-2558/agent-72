"""Integration tests for Organization and Unit endpoints."""

from fastapi.testclient import TestClient


def test_create_and_list_institutions(client: TestClient):
    payload = {
        "code": "APEX-UNIV",
        "name": "Apex University of Science and Technology",
        "institution_type": "UNIVERSITY",
        "status": "ACTIVE",
    }
    create_res = client.post("/api/v1/organizations/institutions", json=payload)
    assert create_res.status_code == 201
    data = create_res.json()
    inst_id = data["id"]
    assert data["code"] == "APEX-UNIV"
    assert data["name"] == "Apex University of Science and Technology"

    # List institutions
    list_res = client.get("/api/v1/organizations/institutions")
    assert list_res.status_code == 200
    list_data = list_res.json()
    assert list_data["total"] >= 1
    assert any(i["id"] == inst_id for i in list_data["items"])

    # Duplicate code should fail with 422/409
    dup_res = client.post("/api/v1/organizations/institutions", json=payload)
    assert dup_res.status_code == 422


def test_create_and_list_units_under_institution(client: TestClient):
    # 1. Create institution
    inst_payload = {
        "code": "TECH-INST",
        "name": "National Technical Institute",
        "institution_type": "UNIVERSITY",
    }
    inst_res = client.post("/api/v1/organizations/institutions", json=inst_payload)
    assert inst_res.status_code == 201
    inst_id = inst_res.json()["id"]

    # 2. Create department
    unit_payload = {
        "institution_id": inst_id,
        "code": "CSE",
        "name": "Computer Science and Engineering",
        "unit_type": "DEPARTMENT",
        "status": "ACTIVE",
    }
    unit_res = client.post("/api/v1/organizations/units", json=unit_payload)
    assert unit_res.status_code == 201
    unit_data = unit_res.json()
    assert unit_data["code"] == "CSE"
    assert unit_data["institution_id"] == inst_id

    # 3. List units for institution
    list_units_res = client.get(f"/api/v1/organizations/institutions/{inst_id}/units")
    assert list_units_res.status_code == 200
    units_list = list_units_res.json()
    assert units_list["total"] >= 1
    assert units_list["items"][0]["code"] == "CSE"
