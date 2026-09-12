"""Integration tests for Phase 7 Strategic Options, Scenarios & Prioritization API."""

from fastapi.testclient import TestClient


def setup_institution_and_all_prerequisites(client: TestClient):
    """Helper setting up an institution, multi-domain evidence, Phase 4, Phase 5, and Phase 6."""
    # 1. Create Institution
    inst_res = client.post(
        "/api/v1/organizations/institutions",
        json={"code": "OPT-UNIV", "name": "Strategic Options University"},
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
            "metric_key": "employer.demand.index",
            "name": "Employer Demand Index",
            "domain": "PLACEMENT_EMPLOYER_DEMAND",
            "direction": "HIGHER_IS_BETTER",
            "default_unit": "index",
        },
        {
            "metric_key": "admissions.yield",
            "name": "Admissions Yield",
            "domain": "ADMISSIONS_MARKET",
            "direction": "HIGHER_IS_BETTER",
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

        # Employer Demand: declining index
        {"institution_id": inst_id, "metric_key": "employer.demand.index", "domain": "PLACEMENT_EMPLOYER_DEMAND", "numeric_value": 85.0, "unit": "index", "period": "2022-2023", "source_name": "Bureau", "source_type": "EXTERNAL"},
        {"institution_id": inst_id, "metric_key": "employer.demand.index", "domain": "PLACEMENT_EMPLOYER_DEMAND", "numeric_value": 75.0, "unit": "index", "period": "2023-2024", "source_name": "Bureau", "source_type": "EXTERNAL"},
        {"institution_id": inst_id, "metric_key": "employer.demand.index", "domain": "PLACEMENT_EMPLOYER_DEMAND", "numeric_value": 68.0, "unit": "index", "period": "2024-2025", "source_name": "Bureau", "source_type": "EXTERNAL"},

        # Admissions: declining yield (45 -> 38 -> 30)
        {"institution_id": inst_id, "metric_key": "admissions.yield", "domain": "ADMISSIONS_MARKET", "numeric_value": 45.0, "unit": "percent", "period": "2022-2023", "source_name": "Admissions", "source_type": "MANUAL"},
        {"institution_id": inst_id, "metric_key": "admissions.yield", "domain": "ADMISSIONS_MARKET", "numeric_value": 38.0, "unit": "percent", "period": "2023-2024", "source_name": "Admissions", "source_type": "MANUAL"},
        {"institution_id": inst_id, "metric_key": "admissions.yield", "domain": "ADMISSIONS_MARKET", "numeric_value": 30.0, "unit": "percent", "period": "2024-2025", "source_name": "Admissions", "source_type": "MANUAL"},

        # Research: accelerating (40 -> 52 -> 65)
        {"institution_id": inst_id, "metric_key": "research.publications", "domain": "RESEARCH_PRODUCTIVITY", "numeric_value": 40.0, "unit": "count", "period": "2022-2023", "source_name": "ResearchOffice", "source_type": "MANUAL"},
        {"institution_id": inst_id, "metric_key": "research.publications", "domain": "RESEARCH_PRODUCTIVITY", "numeric_value": 52.0, "unit": "count", "period": "2023-2024", "source_name": "ResearchOffice", "source_type": "MANUAL"},
        {"institution_id": inst_id, "metric_key": "research.publications", "domain": "RESEARCH_PRODUCTIVITY", "numeric_value": 65.0, "unit": "count", "period": "2024-2025", "source_name": "ResearchOffice", "source_type": "MANUAL"},

        # Lab utilization: 88.5% (above 85% threshold)
        {"institution_id": inst_id, "metric_key": "infra.lab.utilization", "domain": "INFRASTRUCTURE", "numeric_value": 88.5, "unit": "percent", "period": "2024-2025", "source_name": "Facilities", "source_type": "MANUAL"},

        # Faculty PhD ratio: 65.0% (below 70% threshold)
        {"institution_id": inst_id, "metric_key": "faculty.phd.ratio", "domain": "FACULTY_CAPABILITY", "numeric_value": 65.0, "unit": "percent", "period": "2024-2025", "source_name": "HR", "source_type": "MANUAL"},

        # External regulatory observation
        {"institution_id": inst_id, "metric_key": "external.ai_curriculum_mandate", "domain": "EXTERNAL_REGULATORY", "numeric_value": 1.0, "unit": "boolean", "period": "2024-2025", "source_name": "Accreditor", "source_type": "EXTERNAL"},
    ]
    for ev in evidence_items:
        client.post("/api/v1/evidence/ingest", json=ev)

    # 4. Generate Phase 4 Current Position Analysis
    pos_res = client.post(
        "/api/v1/analysis/current-position",
        json={"institution_id": inst_id, "analysis_period": "2024-2025"},
    )
    assert pos_res.status_code == 201

    # 5. Generate Phase 5 Trajectory Analysis
    traj_res = client.post(
        "/api/v1/analysis/trajectory",
        json={"institution_id": inst_id, "analysis_period": "2024-2025"},
    )
    assert traj_res.status_code == 201

    # 6. Generate Phase 6 Strategic Intelligence Analysis
    intel_res = client.post(
        "/api/v1/analysis/strategic-intelligence",
        json={"institution_id": inst_id, "analysis_period": "2024-2025"},
    )
    assert intel_res.status_code == 201
    intel_id = intel_res.json()["id"]

    return inst_id, intel_id


def test_generate_strategic_options_end_to_end(client: TestClient):
    """Verifies end-to-end POST generation of Strategic Options Analysis snapshot."""
    inst_id, intel_id = setup_institution_and_all_prerequisites(client)

    payload = {
        "institution_id": inst_id,
        "analysis_period": "2024-2025",
        "strategic_intelligence_analysis_id": intel_id,
        "include_ai_synthesis": False,
    }
    res = client.post("/api/v1/analysis/strategic-options", json=payload)
    assert res.status_code == 201
    data = res.json()

    assert data["institution_id"] == inst_id
    assert data["analysis_period"] == "2024-2025"
    assert data["strategic_intelligence_analysis_id"] == intel_id
    assert data["status"] == "FINALIZED"

    # Verify options count (3 to 8 range)
    assert 3 <= len(data["options"]) <= 8

    # Verify 4 scenarios per option
    assert len(data["scenarios"]) == len(data["options"]) * 4

    # Verify evaluations across all 7 dimensions
    assert len(data["evaluations"]) == len(data["options"])
    first_eval = data["evaluations"][0]
    assert "strategic_alignment_score" in first_eval
    assert "impact_score" in first_eval
    assert "feasibility_score" in first_eval
    assert "resource_efficiency_score" in first_eval
    assert "implementation_risk_score" in first_eval
    assert "urgency_score" in first_eval
    assert "evidence_strength_score" in first_eval
    assert "total_score" in first_eval
    assert "priority_level" in first_eval
    assert "trade_offs" in first_eval
    assert "rationale" in first_eval

    # Verify prioritized ordering
    assert len(data["prioritized_option_ids"]) == len(data["options"])

    # Verify mandatory leadership decision-support disclaimer
    expected_disclaimer = (
        "Strategic options and priority signals are decision-support outputs. "
        "Final strategic decisions remain with institutional leadership/governing bodies."
    )
    assert data["decision_support_disclaimer"] == expected_disclaimer


def test_get_strategic_options_by_id(client: TestClient):
    """Verifies GET by analysis ID returns immutable snapshot."""
    inst_id, intel_id = setup_institution_and_all_prerequisites(client)

    create_res = client.post(
        "/api/v1/analysis/strategic-options",
        json={"institution_id": inst_id, "analysis_period": "2024-2025"},
    )
    created_id = create_res.json()["id"]

    get_res = client.get(f"/api/v1/analysis/strategic-options/{created_id}")
    assert get_res.status_code == 200
    data = get_res.json()
    assert data["id"] == created_id
    assert data["institution_id"] == inst_id
    assert len(data["options"]) == len(create_res.json()["options"])


def test_list_strategic_options_filtering_and_pagination(client: TestClient):
    """Verifies GET list with filters and pagination parameters."""
    inst_id, intel_id = setup_institution_and_all_prerequisites(client)

    client.post(
        "/api/v1/analysis/strategic-options",
        json={"institution_id": inst_id, "analysis_period": "2024-2025"},
    )

    # Query list
    list_res = client.get(
        "/api/v1/analysis/strategic-options",
        params={"institution_id": inst_id, "analysis_period": "2024-2025", "skip": 0, "limit": 10},
    )
    assert list_res.status_code == 200
    data = list_res.json()
    assert data["total"] >= 1
    assert len(data["items"]) >= 1
    assert data["items"][0]["institution_id"] == inst_id


def test_get_nonexistent_strategic_options_returns_404(client: TestClient):
    """Verifies that querying a nonexistent analysis ID returns HTTP 404."""
    res = client.get("/api/v1/analysis/strategic-options/nonexistent-id-999")
    assert res.status_code == 404


def test_missing_phase6_prerequisite_returns_422(client: TestClient):
    """Verifies that requesting options for an institution without Phase 6 intelligence returns HTTP 422."""
    inst_res = client.post(
        "/api/v1/organizations/institutions",
        json={"code": "NOPREREQ-UNIV", "name": "No Prereq University"},
    )
    inst_id = inst_res.json()["id"]

    res = client.post(
        "/api/v1/analysis/strategic-options",
        json={"institution_id": inst_id, "analysis_period": "2024-2025"},
    )
    assert res.status_code == 422
    assert "Missing required prerequisite Strategic Intelligence Analysis" in res.text
