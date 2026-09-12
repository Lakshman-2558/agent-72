"""Integration tests for Evidence Ingestion and Time-Series Retrieval."""

from fastapi.testclient import TestClient


def test_metric_definition_registration(client: TestClient):
    payload = {
        "metric_key": "research.publications.q1",
        "name": "Scopus Quartile 1 Publications",
        "domain": "RESEARCH_PRODUCTIVITY",
        "default_unit": "count",
        "description": "Number of faculty peer-reviewed articles published in Scopus Q1 indexed journals.",
    }
    res = client.post("/api/v1/evidence/metrics", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert data["metric_key"] == "research.publications.q1"
    assert data["domain"] == "RESEARCH_PRODUCTIVITY"

    # List metric definitions
    list_res = client.get("/api/v1/evidence/metrics?domain=RESEARCH_PRODUCTIVITY")
    assert list_res.status_code == 200
    list_data = list_res.json()
    assert list_data["total"] >= 1
    assert any(m["metric_key"] == "research.publications.q1" for m in list_data["items"])


def test_single_evidence_ingestion_and_provenance(client: TestClient):
    inst_res = client.post(
        "/api/v1/organizations/institutions",
        json={"code": "APEX-U", "name": "Apex University"},
    )
    inst_id = inst_res.json()["id"]

    client.post(
        "/api/v1/evidence/metrics",
        json={
            "metric_key": "admissions.intake_fill_rate",
            "name": "Intake Fill Rate",
            "domain": "ADMISSIONS_MARKET",
            "default_unit": "percent",
        },
    )

    payload = {
        "institution_id": inst_id,
        "metric_key": "admissions.intake_fill_rate",
        "domain": "ADMISSIONS_MARKET",
        "numeric_value": 94.5,
        "unit": "percent",
        "period": "2024-2025",
        "source_type": "AGENT",
        "source_name": "Agent 38",
        "source_reference": "run-batch-2024-09",
        "confidence_score": 0.98,
        "quality_tier": "VERIFIED",
    }
    ingest_res = client.post("/api/v1/evidence/ingest", json=payload)
    assert ingest_res.status_code == 201
    ev_data = ingest_res.json()
    assert ev_data["id"] is not None
    assert ev_data["metric_key"] == "admissions.intake.fill.rate"
    assert ev_data["numeric_value"] == 94.5
    assert ev_data["period"] == "2024-2025"
    assert ev_data["source_name"] == "Agent 38"
    assert ev_data["confidence_score"] == 0.98
    assert ev_data["quality_tier"] == "VERIFIED"


def test_batch_evidence_ingestion_and_time_series_query(client: TestClient):
    inst_res = client.post(
        "/api/v1/organizations/institutions",
        json={"code": "TS-UNIV", "name": "Time Series University"},
    )
    inst_id = inst_res.json()["id"]

    client.post(
        "/api/v1/evidence/metrics",
        json={
            "metric_key": "research.citations",
            "name": "Scopus Citations",
            "domain": "RESEARCH_PRODUCTIVITY",
            "default_unit": "count",
        },
    )

    # Ingest 3 historical years of research citations
    batch_payload = {
        "items": [
            {
                "institution_id": inst_id,
                "metric_key": "research.citations",
                "domain": "RESEARCH_PRODUCTIVITY",
                "numeric_value": 1500.0,
                "unit": "count",
                "period": "2022-2023",
                "source_type": "AGENT",
                "source_name": "Agent 20",
                "confidence_score": 0.95,
            },
            {
                "institution_id": inst_id,
                "metric_key": "research.citations",
                "domain": "RESEARCH_PRODUCTIVITY",
                "numeric_value": 1850.0,
                "unit": "count",
                "period": "2023-2024",
                "source_type": "AGENT",
                "source_name": "Agent 20",
                "confidence_score": 0.95,
            },
            {
                "institution_id": inst_id,
                "metric_key": "research.citations",
                "domain": "RESEARCH_PRODUCTIVITY",
                "numeric_value": 2400.0,
                "unit": "count",
                "period": "2024-2025",
                "source_type": "AGENT",
                "source_name": "Agent 20",
                "confidence_score": 0.97,
            },
        ]
    }

    batch_res = client.post("/api/v1/evidence/ingest/batch", json=batch_payload)
    assert batch_res.status_code == 201
    batch_data = batch_res.json()
    assert batch_data["total"] == 3

    # Query time-series for institution
    query_res = client.get(f"/api/v1/evidence?institution_id={inst_id}&metric_key=research.citations")
    assert query_res.status_code == 200
    query_data = query_res.json()
    assert query_data["total"] == 3

    periods = [item["period"] for item in query_data["items"]]
    assert "2024-2025" in periods
    assert "2023-2024" in periods
    assert "2022-2023" in periods


def test_invalid_period_ingestion_fails(client: TestClient):
    inst_res = client.post(
        "/api/v1/organizations/institutions",
        json={"code": "INV-UNIV", "name": "Invalid Period University"},
    )
    inst_id = inst_res.json()["id"]

    client.post(
        "/api/v1/evidence/metrics",
        json={
            "metric_key": "finance.operating_margin",
            "name": "Operating Margin",
            "domain": "FINANCE_RESOURCES",
            "default_unit": "percent",
        },
    )

    payload = {
        "institution_id": inst_id,
        "metric_key": "finance.operating_margin",
        "domain": "FINANCE_RESOURCES",
        "numeric_value": 12.5,
        "unit": "percent",
        "period": "bad_period_format",
        "source_name": "Manual Entry",
    }
    res = client.post("/api/v1/evidence/ingest", json=payload)
    assert res.status_code == 422
    err = res.json()
    assert "error" in err
