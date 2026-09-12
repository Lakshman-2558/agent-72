"""Integration tests for Evidence Ingestion Pipeline: Normalization, Idempotency, Batch Processing, and Auditability."""

from fastapi.testclient import TestClient


def setup_test_institution_and_metric(client: TestClient) -> str:
    """Helper registering an institution and canonical metric definition."""
    inst_res = client.post(
        "/api/v1/organizations/institutions",
        json={"code": "INGEST-UNIV", "name": "Ingestion Testing University"},
    )
    inst_id = inst_res.json()["id"]

    client.post(
        "/api/v1/evidence/metrics",
        json={
            "metric_key": "research.citations",
            "name": "Annual Citations",
            "domain": "RESEARCH_PRODUCTIVITY",
            "default_unit": "count",
        },
    )
    return inst_id


def test_single_ingestion_normalization_and_idempotency(client: TestClient):
    inst_id = setup_test_institution_and_metric(client)

    # 1. Ingest evidence with raw unnormalized inputs (whitespace, uppercase domain, shorthand period)
    payload = {
        "institution_id": inst_id,
        "metric_key": "  RESEARCH.citations  ",
        "domain": "research",
        "numeric_value": 350.0,
        "unit": "cnt",
        "period": "2024-25",
        "as_of_date": "2024-12-31",
        "source_type": "AGENT",
        "source_name": "Agent 20",
        "external_record_id": "rec-agent20-001",
    }

    res1 = client.post("/api/v1/evidence/ingest", json=payload)
    assert res1.status_code == 201
    data1 = res1.json()
    record_id = data1["id"]

    # Verify normalization
    assert data1["metric_key"] == "research.citations"
    assert data1["domain"] == "RESEARCH_PRODUCTIVITY"
    assert data1["unit"] == "count"
    assert data1["period"] == "2024-2025"
    assert data1["external_record_id"] == "rec-agent20-001"
    assert data1["freshness"] is not None
    assert "status" in data1["freshness"]

    # 2. Resubmit the exact same record with identical external_record_id
    res2 = client.post("/api/v1/evidence/ingest", json=payload)
    assert res2.status_code == 201
    data2 = res2.json()

    # Must return the identical existing record (idempotency)
    assert data2["id"] == record_id

    # 3. Check evidence count: exactly 1 record in database
    list_res = client.get(f"/api/v1/evidence?institution_id={inst_id}&metric_key=research.citations")
    assert list_res.status_code == 200
    assert list_res.json()["total"] == 1


def test_batch_ingestion_partial_failure_and_audit_log(client: TestClient):
    inst_id = setup_test_institution_and_metric(client)

    # Pre-populate 1 record
    client.post(
        "/api/v1/evidence/ingest",
        json={
            "institution_id": inst_id,
            "metric_key": "research.citations",
            "domain": "RESEARCH_PRODUCTIVITY",
            "numeric_value": 400.0,
            "unit": "count",
            "period": "2023-2024",
            "source_name": "Agent 20",
            "external_record_id": "rec-duplicate-target",
        },
    )

    batch_payload = {
        "batch_id": "test-batch-uuid-001",
        "auto_register_metrics": False,
        "items": [
            # Item 0: Valid new record
            {
                "institution_id": inst_id,
                "metric_key": "research.citations",
                "domain": "RESEARCH_PRODUCTIVITY",
                "numeric_value": 550.0,
                "unit": "count",
                "period": "2024-2025",
                "source_name": "Agent 20",
                "external_record_id": "rec-new-002",
            },
            # Item 1: Duplicate of pre-existing record
            {
                "institution_id": inst_id,
                "metric_key": "research.citations",
                "domain": "RESEARCH_PRODUCTIVITY",
                "numeric_value": 400.0,
                "unit": "count",
                "period": "2023-2024",
                "source_name": "Agent 20",
                "external_record_id": "rec-duplicate-target",
            },
            # Item 2: Unregistered metric without auto_register
            {
                "institution_id": inst_id,
                "metric_key": "unregistered.metric.key",
                "domain": "ACADEMIC_PERFORMANCE",
                "numeric_value": 99.0,
                "unit": "percent",
                "period": "2024-2025",
                "source_name": "Agent 71",
            },
            # Item 3: Invalid period format
            {
                "institution_id": inst_id,
                "metric_key": "research.citations",
                "domain": "RESEARCH_PRODUCTIVITY",
                "numeric_value": 600.0,
                "unit": "count",
                "period": "invalid-period-string",
                "source_name": "Agent 20",
            },
        ],
    }

    batch_res = client.post("/api/v1/evidence/ingest/batch", json=batch_payload)
    assert batch_res.status_code == 201
    result = batch_res.json()

    assert result["batch_id"] == "test-batch-uuid-001"
    assert result["total"] == 4
    assert result["inserted"] == 1
    assert result["duplicates"] == 1
    assert result["rejected"] == 2
    assert len(result["errors"]) == 2

    # Check errors details
    err_keys = [e["metric_key"] for e in result["errors"]]
    assert "unregistered.metric.key" in err_keys

    # Check audit log endpoint
    audit_res = client.get(f"/api/v1/evidence/batches/{result['batch_id']}")
    assert audit_res.status_code == 200
    audit_data = audit_res.json()
    assert audit_data["received_count"] == 4
    assert audit_data["inserted_count"] == 1
    assert audit_data["duplicate_count"] == 1
    assert audit_data["rejected_count"] == 2


def test_auto_register_metrics_behavior(client: TestClient):
    inst_id = setup_test_institution_and_metric(client)

    # 1. auto_register=True with display_name should register metric and ingest
    payload_valid = {
        "institution_id": inst_id,
        "metric_key": "admissions.applications_count",
        "domain": "ADMISSIONS_MARKET",
        "numeric_value": 8500.0,
        "unit": "count",
        "period": "2024-2025",
        "source_name": "Agent 38",
        "display_name": "Total Applications Received",
        "metric_description": "Total admission applications across undergraduate programs",
    }
    res_valid = client.post("/api/v1/evidence/ingest?auto_register=true", json=payload_valid)
    assert res_valid.status_code == 201
    data = res_valid.json()
    assert data["metric_key"] == "admissions.applications.count"

    # Verify metric is now present in catalog
    def_res = client.get("/api/v1/evidence/metrics/admissions.applications.count")
    assert def_res.status_code == 200
    assert def_res.json()["name"] == "Total Applications Received"

    # 2. auto_register=True without display_name should be rejected (Rule #3)
    payload_invalid = {
        "institution_id": inst_id,
        "metric_key": "unknown.without.name",
        "domain": "ACADEMIC_PERFORMANCE",
        "numeric_value": 10.0,
        "unit": "count",
        "period": "2024-2025",
        "source_name": "Manual",
    }
    res_invalid = client.post("/api/v1/evidence/ingest?auto_register=true", json=payload_invalid)
    assert res_invalid.status_code == 422


def test_evidence_immutability_and_historical_series(client: TestClient):
    inst_id = setup_test_institution_and_metric(client)

    # Ingest 3 distinct yearly observations for the same metric
    observations = [
        {"period": "2022-2023", "value": 1100.0, "as_of": "2023-06-30"},
        {"period": "2023-2024", "value": 1450.0, "as_of": "2024-06-30"},
        {"period": "2024-2025", "value": 1820.0, "as_of": "2025-06-30"},
    ]

    for obs in observations:
        res = client.post(
            "/api/v1/evidence/ingest",
            json={
                "institution_id": inst_id,
                "metric_key": "research.citations",
                "domain": "RESEARCH_PRODUCTIVITY",
                "numeric_value": obs["value"],
                "unit": "count",
                "period": obs["period"],
                "as_of_date": obs["as_of"],
                "source_name": "Agent 20",
            },
        )
        assert res.status_code == 201

    # Historical observations must all be preserved (immutability)
    series_res = client.get(f"/api/v1/evidence/series?institution_id={inst_id}&metric_key=research.citations")
    assert series_res.status_code == 200
    series_data = series_res.json()

    assert series_data["total_observations"] == 3
    assert len(series_data["series"]) == 3
    # Check ascending chronological order
    assert series_data["series"][0]["period"] == "2022-2023"
    assert series_data["series"][0]["numeric_value"] == 1100.0
    assert series_data["series"][1]["period"] == "2023-2024"
    assert series_data["series"][1]["numeric_value"] == 1450.0
    assert series_data["series"][2]["period"] == "2024-2025"
    assert series_data["series"][2]["numeric_value"] == 1820.0

    # Latest observation query
    latest_res = client.get(f"/api/v1/evidence/latest?institution_id={inst_id}&metric_key=research.citations")
    assert latest_res.status_code == 200
    latest_data = latest_res.json()
    assert latest_data["period"] == "2024-2025"
    assert latest_data["numeric_value"] == 1820.0
