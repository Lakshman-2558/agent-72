"""Integration tests for Phase 6 Strategic Intelligence API."""

from fastapi.testclient import TestClient


def setup_institution_and_prerequisites(client: TestClient):
    """Helper setting up an institution, evidence, Phase 4 position, and Phase 5 trajectory."""
    # 1. Create Institution
    inst_res = client.post(
        "/api/v1/organizations/institutions",
        json={"code": "STRAT-UNIV", "name": "Strategic University"},
    )
    inst_id = inst_res.json()["id"]

    # 2. Register Metric Definitions
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
            "metric_key": "research.publications",
            "name": "Publications",
            "domain": "RESEARCH_PRODUCTIVITY",
            "direction": "HIGHER_IS_BETTER",
            "default_unit": "count",
        },
        {
            "metric_key": "infra.lab.utilization",
            "name": "Lab Utilization",
            "domain": "INFRASTRUCTURE",
            "direction": "HIGHER_IS_BETTER",
            "default_unit": "percent",
        },
        {
            "metric_key": "faculty.phd.ratio",
            "name": "Faculty PhD Ratio",
            "domain": "FACULTY_CAPABILITY",
            "direction": "HIGHER_IS_BETTER",
            "default_unit": "percent",
        },
    ]
    for m in metrics:
        client.post("/api/v1/evidence/metrics", json=m)

    # 3. Ingest multi-period evidence
    evidence_items = [
        # Placement: declining (88 -> 80 -> 72)
        {"institution_id": inst_id, "metric_key": "placement.rate", "domain": "PLACEMENT_EMPLOYER_DEMAND", "numeric_value": 88.0, "unit": "percent", "period": "2022-2023", "source_name": "Career", "source_type": "MANUAL"},
        {"institution_id": inst_id, "metric_key": "placement.rate", "domain": "PLACEMENT_EMPLOYER_DEMAND", "numeric_value": 80.0, "unit": "percent", "period": "2023-2024", "source_name": "Career", "source_type": "MANUAL"},
        {"institution_id": inst_id, "metric_key": "placement.rate", "domain": "PLACEMENT_EMPLOYER_DEMAND", "numeric_value": 72.0, "unit": "percent", "period": "2024-2025", "source_name": "Career", "source_type": "MANUAL"},

        # Admissions: declining (45 -> 38 -> 30)
        {"institution_id": inst_id, "metric_key": "admissions.yield", "domain": "ADMISSIONS_MARKET", "numeric_value": 45.0, "unit": "percent", "period": "2022-2023", "source_name": "Admissions", "source_type": "MANUAL"},
        {"institution_id": inst_id, "metric_key": "admissions.yield", "domain": "ADMISSIONS_MARKET", "numeric_value": 38.0, "unit": "percent", "period": "2023-2024", "source_name": "Admissions", "source_type": "MANUAL"},
        {"institution_id": inst_id, "metric_key": "admissions.yield", "domain": "ADMISSIONS_MARKET", "numeric_value": 30.0, "unit": "percent", "period": "2024-2025", "source_name": "Admissions", "source_type": "MANUAL"},

        # Research: accelerating (100 -> 140 -> 190)
        {"institution_id": inst_id, "metric_key": "research.publications", "domain": "RESEARCH_PRODUCTIVITY", "numeric_value": 100.0, "unit": "count", "period": "2022-2023", "source_name": "Research", "source_type": "MANUAL"},
        {"institution_id": inst_id, "metric_key": "research.publications", "domain": "RESEARCH_PRODUCTIVITY", "numeric_value": 140.0, "unit": "count", "period": "2023-2024", "source_name": "Research", "source_type": "MANUAL"},
        {"institution_id": inst_id, "metric_key": "research.publications", "domain": "RESEARCH_PRODUCTIVITY", "numeric_value": 190.0, "unit": "count", "period": "2024-2025", "source_name": "Research", "source_type": "MANUAL"},

        # Infrastructure: reaching 88.5% (>= 85% capacity threshold)
        {"institution_id": inst_id, "metric_key": "infra.lab.utilization", "domain": "INFRASTRUCTURE", "numeric_value": 88.5, "unit": "percent", "period": "2024-2025", "source_name": "Facilities", "source_type": "MANUAL"},

        # Faculty: 64% PhD (< 70% threshold)
        {"institution_id": inst_id, "metric_key": "faculty.phd.ratio", "domain": "FACULTY_CAPABILITY", "numeric_value": 64.0, "unit": "percent", "period": "2024-2025", "source_name": "HR", "source_type": "MANUAL"},
    ]
    client.post("/api/v1/evidence/ingest/batch", json={"items": evidence_items})

    # 4. Generate Phase 4 Current Position Analysis
    pos_res = client.post(
        "/api/v1/analysis/current-position",
        json={
            "institution_id": inst_id,
            "analysis_period": "2024-2025",
            "configured_baselines": {
                "placement.rate": 85.0,  # Below target
            },
        },
    )
    assert pos_res.status_code == 201
    pos_id = pos_res.json()["id"]

    # 5. Generate Phase 5 Trajectory Analysis
    traj_res = client.post(
        "/api/v1/analysis/trajectory",
        json={
            "institution_id": inst_id,
            "analysis_period": "2024-2025",
            "current_position_analysis_id": pos_id,
        },
    )
    assert traj_res.status_code == 201
    traj_id = traj_res.json()["id"]

    return inst_id, pos_id, traj_id


def test_generate_strategic_intelligence_end_to_end(client: TestClient):
    inst_id, pos_id, traj_id = setup_institution_and_prerequisites(client)

    strat_res = client.post(
        "/api/v1/analysis/strategic-intelligence",
        json={
            "institution_id": inst_id,
            "analysis_period": "2024-2025",
            "current_position_analysis_id": pos_id,
            "trajectory_analysis_id": traj_id,
            "include_ai_synthesis": True,
        },
    )
    assert strat_res.status_code == 201
    data = strat_res.json()

    assert data["id"] is not None
    assert data["institution_id"] == inst_id
    assert data["analysis_period"] == "2024-2025"
    assert data["status"] == "FINALIZED"
    assert len(data["strategic_issues"]) >= 1
    assert len(data["risk_signals"]) >= 1
    assert len(data["constraint_signals"]) >= 1
    assert len(data["opportunity_signals"]) >= 1
    assert len(data["strategic_priority_signals"]) >= 1
    assert data["uncertainty_summary"] is not None
    assert data["ai_synthesis_notes"] is not None


def test_get_strategic_intelligence_by_id(client: TestClient):
    inst_id, pos_id, traj_id = setup_institution_and_prerequisites(client)

    create_res = client.post(
        "/api/v1/analysis/strategic-intelligence",
        json={
            "institution_id": inst_id,
            "analysis_period": "2024-2025",
            "current_position_analysis_id": pos_id,
            "trajectory_analysis_id": traj_id,
        },
    )
    analysis_id = create_res.json()["id"]

    get_res = client.get(f"/api/v1/analysis/strategic-intelligence/{analysis_id}")
    assert get_res.status_code == 200
    data = get_res.json()
    assert data["id"] == analysis_id
    assert data["institution_id"] == inst_id


def test_list_strategic_intelligence_filtering_and_pagination(client: TestClient):
    inst_id, pos_id, traj_id = setup_institution_and_prerequisites(client)

    client.post(
        "/api/v1/analysis/strategic-intelligence",
        json={
            "institution_id": inst_id,
            "analysis_period": "2024-2025",
            "current_position_analysis_id": pos_id,
            "trajectory_analysis_id": traj_id,
        },
    )

    # Filter by institution_id
    list_res = client.get(f"/api/v1/analysis/strategic-intelligence?institution_id={inst_id}&analysis_period=2024-2025")
    assert list_res.status_code == 200
    data = list_res.json()
    assert data["total"] >= 1
    assert len(data["items"]) >= 1

    # Pagination
    page_res = client.get(f"/api/v1/analysis/strategic-intelligence?institution_id={inst_id}&skip=0&limit=1")
    assert page_res.status_code == 200
    assert len(page_res.json()["items"]) == 1


def test_get_nonexistent_strategic_intelligence_returns_404(client: TestClient):
    res = client.get("/api/v1/analysis/strategic-intelligence/nonexistent-id-12345")
    assert res.status_code == 404


def test_missing_prerequisites_returns_400(client: TestClient):
    # Valid institution but no Phase 4 or Phase 5 analyses run
    inst_res = client.post(
        "/api/v1/organizations/institutions",
        json={"code": "NOPREREQ", "name": "No Prereq University"},
    )
    inst_id = inst_res.json()["id"]

    res = client.post(
        "/api/v1/analysis/strategic-intelligence",
        json={
            "institution_id": inst_id,
            "analysis_period": "2024-2025",
        },
    )
    assert res.status_code == 422
    assert "Prerequisite Current Position Analysis" in res.json()["error"]["message"]
