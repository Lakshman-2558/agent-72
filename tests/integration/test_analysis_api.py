"""Integration tests for Phase 4 Current Institutional Position Analysis API."""

from fastapi.testclient import TestClient


def setup_institution_and_metrics(client: TestClient) -> str:
    """Helper creating an institution and canonical metrics with directions."""
    inst_res = client.post(
        "/api/v1/organizations/institutions",
        json={"code": "ANALYSIS-UNIV", "name": "Strategic Analysis University"},
    )
    inst_id = inst_res.json()["id"]

    # Metric 1: Placement Rate (HIGHER_IS_BETTER)
    client.post(
        "/api/v1/evidence/metrics",
        json={
            "metric_key": "placement.rate",
            "name": "Placement Rate",
            "domain": "PLACEMENT_EMPLOYER_DEMAND",
            "direction": "HIGHER_IS_BETTER",
            "default_unit": "percent",
        },
    )

    # Metric 2: Dropout Rate (LOWER_IS_BETTER)
    client.post(
        "/api/v1/evidence/metrics",
        json={
            "metric_key": "academic.dropout_rate",
            "name": "Student Dropout Rate",
            "domain": "ACADEMIC_PERFORMANCE",
            "direction": "LOWER_IS_BETTER",
            "default_unit": "percent",
        },
    )

    # Metric 3: Research Citations (HIGHER_IS_BETTER)
    client.post(
        "/api/v1/evidence/metrics",
        json={
            "metric_key": "research.citations",
            "name": "Annual Citations",
            "domain": "RESEARCH_PRODUCTIVITY",
            "direction": "HIGHER_IS_BETTER",
            "default_unit": "count",
        },
    )

    # Metric 4: Faculty Capability (no evidence ingested - test data gap isolation)
    client.post(
        "/api/v1/evidence/metrics",
        json={
            "metric_key": "faculty.capability",
            "name": "Faculty Capability Index",
            "domain": "FACULTY_CAPABILITY",
            "direction": "HIGHER_IS_BETTER",
            "default_unit": "index",
        },
    )

    return inst_id


def test_generate_current_position_analysis_full_pipeline(client: TestClient):
    inst_id = setup_institution_and_metrics(client)

    # Ingest 2 years of evidence
    batch_payload = {
        "items": [
            # 2023-2024
            {
                "institution_id": inst_id,
                "metric_key": "placement.rate",
                "domain": "PLACEMENT_EMPLOYER_DEMAND",
                "numeric_value": 76.0,
                "unit": "percent",
                "period": "2023-2024",
                "source_name": "Agent 71",
                "source_type": "AGENT",
            },
            {
                "institution_id": inst_id,
                "metric_key": "academic.dropout_rate",
                "domain": "ACADEMIC_PERFORMANCE",
                "numeric_value": 8.5,
                "unit": "percent",
                "period": "2023-2024",
                "source_name": "Agent 71",
                "source_type": "AGENT",
            },
            {
                "institution_id": inst_id,
                "metric_key": "research.citations",
                "domain": "RESEARCH_PRODUCTIVITY",
                "numeric_value": 2850.0,
                "unit": "count",
                "period": "2023-2024",
                "source_name": "Agent 20",
                "source_type": "AGENT",
            },
            # 2024-2025
            {
                "institution_id": inst_id,
                "metric_key": "placement.rate",
                "domain": "PLACEMENT_EMPLOYER_DEMAND",
                "numeric_value": 81.0,
                "unit": "percent",
                "period": "2024-2025",
                "source_name": "Agent 71",
                "source_type": "AGENT",
            },
            {
                "institution_id": inst_id,
                "metric_key": "academic.dropout_rate",
                "domain": "ACADEMIC_PERFORMANCE",
                "numeric_value": 7.2,
                "unit": "percent",
                "period": "2024-2025",
                "source_name": "Agent 71",
                "source_type": "AGENT",
            },
            {
                "institution_id": inst_id,
                "metric_key": "research.citations",
                "domain": "RESEARCH_PRODUCTIVITY",
                "numeric_value": 3420.0,
                "unit": "count",
                "period": "2024-2025",
                "source_name": "Agent 20",
                "source_type": "AGENT",
            },
        ]
    }
    client.post("/api/v1/evidence/ingest/batch", json=batch_payload)

    # Generate current position analysis with configured target
    analysis_payload = {
        "institution_id": inst_id,
        "analysis_period": "2024-2025",
        "configured_baselines": {
            "placement.rate": 85.0,  # Target is 85% (current is 81%, so target gap exists)
        },
    }

    res = client.post("/api/v1/analysis/current-position", json=analysis_payload)
    assert res.status_code == 201
    data = res.json()

    # Verify top-level structure
    assert data["id"] is not None
    assert data["institution_id"] == inst_id
    assert data["analysis_period"] == "2024-2025"
    assert data["status"] == "FINALIZED"
    assert len(data["assumptions"]) >= 1

    # Verify key metrics
    metrics = {m["metric_key"]: m for m in data["key_metrics"]}
    assert "placement.rate" in metrics
    assert "academic.dropout.rate" in metrics
    assert "research.citations" in metrics
    assert "faculty.capability" in metrics

    # Placement rate verification
    p_metric = metrics["placement.rate"]
    assert p_metric["latest_value"] == 81.0
    assert p_metric["previous_value"] == 76.0
    assert p_metric["target_value"] == 85.0
    assert p_metric["target_variance"] == -4.0
    assert p_metric["performance_status"] == "BELOW_TARGET"

    # Dropout rate verification (LOWER_IS_BETTER)
    d_metric = metrics["academic.dropout.rate"]
    assert d_metric["latest_value"] == 7.2
    assert d_metric["previous_value"] == 8.5
    assert d_metric["change_direction"] == "↓"
    assert d_metric["performance_status"] == "POSITIVE_PERFORMANCE"

    # Research citations verification (2850 -> 3420, +20.0%)
    c_metric = metrics["research.citations"]
    assert c_metric["latest_value"] == 3420.0
    assert c_metric["previous_value"] == 2850.0
    assert c_metric["percent_change"] == 20.0
    assert c_metric["performance_status"] == "POSITIVE_PERFORMANCE"

    # Strengths check (dropout rate improved, citations improved)
    assert len(data["strengths"]) >= 1
    assert any("Dropout Rate improved" in s["title"] for s in data["strengths"])
    assert any("Citations improved" in s["title"] for s in data["strengths"])

    # Gaps check (placement rate is below target)
    assert len(data["gaps"]) >= 1
    assert any("Placement Rate below strategic target" in g["title"] for g in data["gaps"])

    # Opportunities check (citations grew by +20% -> momentum opportunity)
    assert len(data["opportunities"]) >= 1
    assert any("Citations" in o["title"] for o in data["opportunities"])

    # Data gaps check (faculty capability had no evidence -> isolated in data_gaps, NOT weakness)
    assert len(data["data_gaps"]) >= 1
    assert any("faculty.capability" in dg["metric_key"] for dg in data["data_gaps"] if dg.get("metric_key"))
    assert len(data["weaknesses"]) == 0

    # Confidence check
    assert data["overall_confidence"]["level"] in ("HIGH", "MEDIUM")
    assert data["overall_confidence"]["score"] >= 0.70
    assert "factors" in data["overall_confidence"]

    # Evidence references check
    assert len(data["evidence_references"]) >= 3


def test_get_analysis_by_id_and_immutability(client: TestClient):
    inst_id = setup_institution_and_metrics(client)

    # Ingest 1 observation
    client.post(
        "/api/v1/evidence/ingest",
        json={
            "institution_id": inst_id,
            "metric_key": "placement.rate",
            "domain": "PLACEMENT_EMPLOYER_DEMAND",
            "numeric_value": 78.5,
            "unit": "percent",
            "period": "2024-2025",
            "source_name": "Agent 71",
        },
    )

    create_res = client.post(
        "/api/v1/analysis/current-position",
        json={"institution_id": inst_id, "analysis_period": "2024-2025"},
    )
    analysis_id = create_res.json()["id"]

    # Retrieve by ID
    get_res = client.get(f"/api/v1/analysis/current-position/{analysis_id}")
    assert get_res.status_code == 200
    snapshot = get_res.json()
    assert snapshot["id"] == analysis_id
    assert snapshot["analysis_period"] == "2024-2025"
    assert snapshot["status"] == "FINALIZED"


def test_list_analyses_with_filters_and_pagination(client: TestClient):
    inst_id = setup_institution_and_metrics(client)

    # Ingest 1 observation
    client.post(
        "/api/v1/evidence/ingest",
        json={
            "institution_id": inst_id,
            "metric_key": "placement.rate",
            "domain": "PLACEMENT_EMPLOYER_DEMAND",
            "numeric_value": 80.0,
            "unit": "percent",
            "period": "2024-2025",
            "source_name": "Agent 71",
        },
    )

    # Generate analysis
    client.post(
        "/api/v1/analysis/current-position",
        json={"institution_id": inst_id, "analysis_period": "2024-2025"},
    )

    # List with filter
    list_res = client.get(f"/api/v1/analysis/current-position?institution_id={inst_id}&analysis_period=2024-2025")
    assert list_res.status_code == 200
    data = list_res.json()
    assert data["total"] >= 1
    assert data["items"][0]["institution_id"] == inst_id


def test_scoped_organizational_unit_analysis(client: TestClient):
    inst_id = setup_institution_and_metrics(client)

    # Create department unit
    unit_res = client.post(
        "/api/v1/organizations/units",
        json={
            "institution_id": inst_id,
            "code": "CS-DEPT",
            "name": "Department of Computer Science",
        },
    )
    unit_id = unit_res.json()["id"]

    # Ingest evidence specifically for CS unit
    client.post(
        "/api/v1/evidence/ingest",
        json={
            "institution_id": inst_id,
            "unit_id": unit_id,
            "metric_key": "research.citations",
            "domain": "RESEARCH_PRODUCTIVITY",
            "numeric_value": 1200.0,
            "unit": "count",
            "period": "2024-2025",
            "source_name": "Agent 20",
        },
    )

    # Generate analysis scoped to unit
    res = client.post(
        "/api/v1/analysis/current-position",
        json={
            "institution_id": inst_id,
            "organizational_unit_id": unit_id,
            "analysis_period": "2024-2025",
        },
    )
    assert res.status_code == 201
    data = res.json()
    assert data["organizational_unit_id"] == unit_id


def test_nonexistent_institution_analysis_fails(client: TestClient):
    res = client.post(
        "/api/v1/analysis/current-position",
        json={"institution_id": "nonexistent-uuid-1234", "analysis_period": "2024-2025"},
    )
    assert res.status_code == 404
