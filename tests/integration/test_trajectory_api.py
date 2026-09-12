"""Integration tests for Phase 5 Institutional Trajectory Analysis API."""

from fastapi.testclient import TestClient


def setup_institution_and_3year_evidence(client: TestClient) -> str:
    """Helper creating an institution and 3-year multi-domain evidence series."""
    inst_res = client.post(
        "/api/v1/organizations/institutions",
        json={"code": "TRAJ-UNIV", "name": "Trajectory University"},
    )
    inst_id = inst_res.json()["id"]

    # Register Metric Definitions
    metrics = [
        {
            "metric_key": "placement.rate",
            "name": "Placement Rate",
            "domain": "PLACEMENT_EMPLOYER_DEMAND",
            "direction": "HIGHER_IS_BETTER",
            "default_unit": "percent",
        },
        {
            "metric_key": "admissions.yield",
            "name": "Admissions Yield",
            "domain": "ADMISSIONS_MARKET",
            "direction": "HIGHER_IS_BETTER",
            "default_unit": "percent",
        },
        {
            "metric_key": "academic.dropout_rate",
            "name": "Student Dropout Rate",
            "domain": "ACADEMIC_PERFORMANCE",
            "direction": "LOWER_IS_BETTER",
            "default_unit": "percent",
        },
        {
            "metric_key": "research.citations",
            "name": "Annual Citations",
            "domain": "RESEARCH_PRODUCTIVITY",
            "direction": "HIGHER_IS_BETTER",
            "default_unit": "count",
        },
        {
            "metric_key": "faculty.ratio",
            "name": "Student Faculty Ratio",
            "domain": "FACULTY_CAPABILITY",
            "direction": "LOWER_IS_BETTER",
            "default_unit": "ratio",
        },
        {
            "metric_key": "infra.capacity",
            "name": "Campus Seat Capacity",
            "domain": "INFRASTRUCTURE",
            "direction": "NEUTRAL",
            "default_unit": "seats",
        },
        {
            "metric_key": "governance.compliance",
            "name": "Compliance Index",
            "domain": "EXTERNAL_REGULATORY",
            "direction": "HIGHER_IS_BETTER",
            "default_unit": "score",
        },
    ]
    for m in metrics:
        client.post("/api/v1/evidence/metrics", json=m)

    # Ingest 3-Year Historical Evidence
    # Periods: 2022-2023, 2023-2024, 2024-2025
    evidence_items = [
        # Placement Rate: 72% -> 76% -> 81% (Accelerating Improvement)
        {"institution_id": inst_id, "metric_key": "placement.rate", "domain": "PLACEMENT_EMPLOYER_DEMAND", "numeric_value": 72.0, "unit": "percent", "period": "2022-2023", "source_name": "Agent 71", "source_type": "AGENT"},
        {"institution_id": inst_id, "metric_key": "placement.rate", "domain": "PLACEMENT_EMPLOYER_DEMAND", "numeric_value": 76.0, "unit": "percent", "period": "2023-2024", "source_name": "Agent 71", "source_type": "AGENT"},
        {"institution_id": inst_id, "metric_key": "placement.rate", "domain": "PLACEMENT_EMPLOYER_DEMAND", "numeric_value": 81.0, "unit": "percent", "period": "2024-2025", "source_name": "Agent 71", "source_type": "AGENT"},

        # Admissions Yield: 45% -> 40% -> 34% (Declining)
        {"institution_id": inst_id, "metric_key": "admissions.yield", "domain": "ADMISSIONS_MARKET", "numeric_value": 45.0, "unit": "percent", "period": "2022-2023", "source_name": "Agent 71", "source_type": "AGENT"},
        {"institution_id": inst_id, "metric_key": "admissions.yield", "domain": "ADMISSIONS_MARKET", "numeric_value": 40.0, "unit": "percent", "period": "2023-2024", "source_name": "Agent 71", "source_type": "AGENT"},
        {"institution_id": inst_id, "metric_key": "admissions.yield", "domain": "ADMISSIONS_MARKET", "numeric_value": 34.0, "unit": "percent", "period": "2024-2025", "source_name": "Agent 71", "source_type": "AGENT"},

        # Dropout Rate: 10.2% -> 8.5% -> 7.2% (Lower is better -> Improving)
        {"institution_id": inst_id, "metric_key": "academic.dropout_rate", "domain": "ACADEMIC_PERFORMANCE", "numeric_value": 10.2, "unit": "percent", "period": "2022-2023", "source_name": "Agent 71", "source_type": "AGENT"},
        {"institution_id": inst_id, "metric_key": "academic.dropout_rate", "domain": "ACADEMIC_PERFORMANCE", "numeric_value": 8.5, "unit": "percent", "period": "2023-2024", "source_name": "Agent 71", "source_type": "AGENT"},
        {"institution_id": inst_id, "metric_key": "academic.dropout_rate", "domain": "ACADEMIC_PERFORMANCE", "numeric_value": 7.2, "unit": "percent", "period": "2024-2025", "source_name": "Agent 71", "source_type": "AGENT"},

        # Citations: 2000 -> 2600 -> 3300 (Accelerating Research Traction)
        {"institution_id": inst_id, "metric_key": "research.citations", "domain": "RESEARCH_PRODUCTIVITY", "numeric_value": 2000.0, "unit": "count", "period": "2022-2023", "source_name": "Agent 20", "source_type": "AGENT"},
        {"institution_id": inst_id, "metric_key": "research.citations", "domain": "RESEARCH_PRODUCTIVITY", "numeric_value": 2600.0, "unit": "count", "period": "2023-2024", "source_name": "Agent 20", "source_type": "AGENT"},
        {"institution_id": inst_id, "metric_key": "research.citations", "domain": "RESEARCH_PRODUCTIVITY", "numeric_value": 3300.0, "unit": "count", "period": "2024-2025", "source_name": "Agent 20", "source_type": "AGENT"},

        # Student Faculty Ratio: 15.0 -> 15.1 -> 15.05 (Stable)
        {"institution_id": inst_id, "metric_key": "faculty.ratio", "domain": "FACULTY_CAPABILITY", "numeric_value": 15.0, "unit": "ratio", "period": "2022-2023", "source_name": "Manual", "source_type": "MANUAL"},
        {"institution_id": inst_id, "metric_key": "faculty.ratio", "domain": "FACULTY_CAPABILITY", "numeric_value": 15.1, "unit": "ratio", "period": "2023-2024", "source_name": "Manual", "source_type": "MANUAL"},
        {"institution_id": inst_id, "metric_key": "faculty.ratio", "domain": "FACULTY_CAPABILITY", "numeric_value": 15.05, "unit": "ratio", "period": "2024-2025", "source_name": "Manual", "source_type": "MANUAL"},

        # Seat capacity: single observation (2024-2025: 5000 seats -> Data limitation)
        {"institution_id": inst_id, "metric_key": "infra.capacity", "domain": "INFRASTRUCTURE", "numeric_value": 5000.0, "unit": "seats", "period": "2024-2025", "source_name": "Facilities", "source_type": "MANUAL"},
        # governance.compliance has 0 observations (Data limitation)
    ]
    client.post("/api/v1/evidence/ingest/batch", json={"items": evidence_items})
    return inst_id


def test_generate_trajectory_analysis_full_pipeline(client: TestClient):
    """Test generating a multi-period trajectory analysis through the REST API."""
    inst_id = setup_institution_and_3year_evidence(client)

    # Generate Current Position Analysis first so Trajectory can synthesize signals
    pos_res = client.post(
        "/api/v1/analysis/current-position",
        json={
            "institution_id": inst_id,
            "analysis_period": "2024-2025",
            "configured_baselines": {
                "placement.rate": 85.0,  # Target is 85% -> 81% is below target (GAP)
                "admissions.yield": 40.0,  # Target is 40% -> 34% is below target (GAP)
            },
        },
    )
    assert pos_res.status_code == 201
    pos_id = pos_res.json()["id"]

    # Now execute Trajectory Analysis
    traj_res = client.post(
        "/api/v1/analysis/trajectory",
        json={
            "institution_id": inst_id,
            "analysis_period": "2024-2025",
            "current_position_analysis_id": pos_id,
        },
    )
    assert traj_res.status_code == 201
    traj_data = traj_res.json()

    assert traj_data["id"] is not None
    assert traj_data["institution_id"] == inst_id
    assert traj_data["analysis_period"] == "2024-2025"
    assert traj_data["status"] == "FINALIZED"
    assert traj_data["overall_confidence"]["level"] in ("HIGH", "MEDIUM")

    trends = {t["metric_key"]: t for t in traj_data["metric_trends"]}

    # 1. Placement: 72 -> 76 -> 81 (IMPROVING, HIGH consistency, ACCELERATING)
    p_trend = trends["placement.rate"]
    assert p_trend["trend_status"] == "IMPROVING"
    assert p_trend["consistency"] == "HIGH"
    assert p_trend["acceleration"] in ("ACCELERATING", "CONSTANT_VELOCITY")
    assert p_trend["absolute_change"] == 9.0

    # 2. Admissions Yield: 45 -> 40 -> 34 (DECLINING, HIGH consistency)
    y_trend = trends["admissions.yield"]
    assert y_trend["trend_status"] == "DECLINING"
    assert y_trend["consistency"] == "HIGH"
    assert y_trend["absolute_change"] == -11.0

    # 3. Dropout Rate (LOWER_IS_BETTER): 10.2 -> 8.5 -> 7.2 (IMPROVING)
    d_trend = trends["academic.dropout.rate"]
    assert d_trend["trend_status"] == "IMPROVING"
    assert d_trend["consistency"] == "HIGH"

    # 4. Student Faculty Ratio: 15.0 -> 15.1 -> 15.05 (STABLE)
    r_trend = trends["faculty.ratio"]
    assert r_trend["trend_status"] == "STABLE"

    # 5. Infrastructure capacity: 1 observation -> INSUFFICIENT_DATA
    c_trend = trends["infra.capacity"]
    assert c_trend["trend_status"] == "INSUFFICIENT_DATA"

    # 6. Data Limitations check
    lims = {l["metric_key"]: l for l in traj_data["data_limitations"]}
    assert "infra.capacity" in lims
    assert "governance.compliance" in lims

    # 7. Structured Signals check
    signals = {s["signal_type"]: s for s in traj_data["trajectory_signals"]}
    assert "GAP_IMPROVING" in signals
    assert "placement.rate" == signals["GAP_IMPROVING"]["metric_key"]
    assert "GAP_DECLINING" in signals
    assert "admissions.yield" == signals["GAP_DECLINING"]["metric_key"]

    # 8. Evidence references check
    assert len(traj_data["evidence_references"]) >= 15
    for ref in traj_data["evidence_references"]:
        assert ref["evidence_id"] is not None
        assert ref["source_name"] in ("Agent 71", "Agent 20", "Manual", "Facilities")


def test_get_trajectory_analysis_by_id(client: TestClient):
    """Test retrieving an immutable trajectory analysis snapshot by ID."""
    inst_id = setup_institution_and_3year_evidence(client)
    create_res = client.post(
        "/api/v1/analysis/trajectory",
        json={"institution_id": inst_id, "analysis_period": "2024-2025"},
    )
    analysis_id = create_res.json()["id"]

    get_res = client.get(f"/api/v1/analysis/trajectory/{analysis_id}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == analysis_id
    assert get_res.json()["institution_id"] == inst_id


def test_list_trajectory_analyses_with_pagination(client: TestClient):
    """Test listing historical trajectory snapshots with filtering and pagination."""
    inst_id = setup_institution_and_3year_evidence(client)
    for p in ["2023-2024", "2024-2025"]:
        client.post(
            "/api/v1/analysis/trajectory",
            json={"institution_id": inst_id, "analysis_period": p},
        )

    list_res = client.get(f"/api/v1/analysis/trajectory?institution_id={inst_id}&limit=10")
    assert list_res.status_code == 200
    body = list_res.json()
    assert body["total"] >= 2
    assert len(body["items"]) >= 2


def test_nonexistent_institution_trajectory_fails(client: TestClient):
    """Analysis for non-existent institution should return 404 EntityNotFoundException."""
    res = client.post(
        "/api/v1/analysis/trajectory",
        json={"institution_id": "nonexistent-inst-uuid", "analysis_period": "2024-2025"},
    )
    assert res.status_code == 404
