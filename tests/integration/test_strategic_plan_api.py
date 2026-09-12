"""Integration tests for Phase 8 Strategic Plan Generation & Execution Framework API."""

from datetime import date
from fastapi.testclient import TestClient
import pytest


@pytest.fixture
def seed_pipeline_data(client: TestClient):
    """Seeds prerequisite Institution, Units, Metrics, Evidence, and Phase 7 Options Analysis."""
    # 1. Create Institution
    inst_payload = {
        "code": "APEX-P8",
        "name": "Apex Institute of Technology",
        "institution_type": "UNIVERSITY",
        "jurisdiction": "National",
    }
    inst_res = client.post("/api/v1/organizations/institutions", json=inst_payload)
    assert inst_res.status_code == 201, inst_res.text
    inst_id = inst_res.json()["id"]

    # 2. Create Units
    unit_res = client.post(
        "/api/v1/organizations/units",
        json={
            "institution_id": inst_id,
            "code": "TP",
            "name": "Corporate Relations & Placement",
            "unit_type": "DEPARTMENT",
        },
    )
    assert unit_res.status_code == 201
    unit_id = unit_res.json()["id"]

    # 3. Create Metric Definitions
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

    # 4. Ingest multi-period evidence
    evidence_items = [
        # Placement: declining (88 -> 80 -> 72)
        {"institution_id": inst_id, "unit_id": unit_id, "metric_key": "placement.rate", "domain": "PLACEMENT_EMPLOYER_DEMAND", "numeric_value": 88.0, "unit": "percent", "period": "2022-2023", "source_name": "Career", "source_type": "MANUAL"},
        {"institution_id": inst_id, "unit_id": unit_id, "metric_key": "placement.rate", "domain": "PLACEMENT_EMPLOYER_DEMAND", "numeric_value": 80.0, "unit": "percent", "period": "2023-2024", "source_name": "Career", "source_type": "MANUAL"},
        {"institution_id": inst_id, "unit_id": unit_id, "metric_key": "placement.rate", "domain": "PLACEMENT_EMPLOYER_DEMAND", "numeric_value": 72.0, "unit": "percent", "period": "2024-2025", "source_name": "Career", "source_type": "MANUAL"},

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
    ]
    client.post("/api/v1/evidence/ingest/batch", json={"items": evidence_items})

    # 5. Run Phase 4 Current Position Analysis
    pos_res = client.post(
        "/api/v1/analysis/current-position",
        json={"institution_id": inst_id, "analysis_period": "2024-2025"},
    )
    assert pos_res.status_code == 201, pos_res.text
    pos_id = pos_res.json()["id"]

    # 6. Run Phase 5 Trajectory Analysis
    traj_res = client.post(
        "/api/v1/analysis/trajectory",
        json={
            "institution_id": inst_id,
            "analysis_period": "2024-2025",
            "current_position_analysis_id": pos_id,
        },
    )
    assert traj_res.status_code == 201, traj_res.text
    traj_id = traj_res.json()["id"]

    # 7. Run Phase 6 Strategic Intelligence Analysis
    intel_res = client.post(
        "/api/v1/analysis/strategic-intelligence",
        json={
            "institution_id": inst_id,
            "analysis_period": "2024-2025",
            "current_position_analysis_id": pos_id,
            "trajectory_analysis_id": traj_id,
        },
    )
    assert intel_res.status_code == 201, intel_res.text
    intel_id = intel_res.json()["id"]

    # 8. Run Phase 7 Strategic Options Generation
    opt_res = client.post(
        "/api/v1/analysis/strategic-options",
        json={
            "institution_id": inst_id,
            "analysis_period": "2024-2025",
            "strategic_intelligence_analysis_id": intel_id,
            "include_ai_synthesis": False,
        },
    )
    assert opt_res.status_code == 201, opt_res.text
    opt_data = opt_res.json()
    opt_id = opt_data["id"]

    return {
        "institution_id": inst_id,
        "unit_id": unit_id,
        "strategic_options_analysis_id": opt_id,
        "options": opt_data["options"],
    }


def test_generate_and_retrieve_execution_plan(client: TestClient, seed_pipeline_data: dict):
    """Test generating a Phase 8 Strategic Plan from Phase 7 options and retrieving it."""
    inst_id = seed_pipeline_data["institution_id"]
    p7_id = seed_pipeline_data["strategic_options_analysis_id"]
    options = seed_pipeline_data["options"]

    # Take the top 2 options
    opt_ids = [opt["id"] for opt in options[:2]]

    payload = {
        "institution_id": inst_id,
        "title": "Institutional Strategic Plan 2026-2030",
        "horizon_start_year": 2026,
        "horizon_end_year": 2030,
        "strategic_options_analysis_id": p7_id,
        "selected_option_ids": opt_ids,
        "override_selection_requirement": True,
        "review_period": "ANNUAL",
    }

    # 1. Generate plan
    res = client.post("/api/v1/plans/generate", json=payload)
    assert res.status_code == 201, res.text
    plan = res.json()
    plan_id = plan["id"]

    # Assert plan structure and governance
    assert plan["status"] == "DRAFT"
    assert "leadership_disclaimer" in plan
    assert "decision-support" in plan["leadership_disclaimer"].lower()
    assert plan["horizon_start_year"] == 2026
    assert plan["horizon_end_year"] == 2030
    assert len(plan["objectives"]) >= 1

    obj = plan["objectives"][0]
    assert "strategic_targets" in obj
    assert "initiatives" in obj
    assert len(obj["initiatives"]) >= 1
    init = obj["initiatives"][0]
    assert len(init["milestones"]) >= 1
    assert init["unit_owner"] is not None

    # 2. Retrieve plan via GET
    get_res = client.get(f"/api/v1/plans/{plan_id}")
    assert get_res.status_code == 200
    retrieved = get_res.json()
    assert retrieved["id"] == plan_id
    assert retrieved["title"] == "Institutional Strategic Plan 2026-2030"
    assert retrieved["status"] == "DRAFT"


def test_plan_leadership_decision_lifecycle(client: TestClient, seed_pipeline_data: dict):
    """Test leadership decision transitions: DRAFT -> APPROVED -> ACTIVE."""
    inst_id = seed_pipeline_data["institution_id"]
    p7_id = seed_pipeline_data["strategic_options_analysis_id"]

    # Generate plan
    res = client.post(
        "/api/v1/plans/generate",
        json={
            "institution_id": inst_id,
            "title": "Governance Plan 2026",
            "horizon_start_year": 2026,
            "horizon_end_year": 2030,
            "strategic_options_analysis_id": p7_id,
            "override_selection_requirement": True,
        },
    )
    assert res.status_code == 201
    plan_id = res.json()["id"]

    # 1. Leadership Approves Plan
    dec_res = client.post(
        f"/api/v1/plans/{plan_id}/decision",
        json={
            "status": "APPROVED",
            "decision_maker_notes": "Board of Regents approved plan unanimously.",
        },
    )
    assert dec_res.status_code == 200
    assert dec_res.json()["status"] == "APPROVED"

    # 2. Leadership Activates Plan
    act_res = client.post(
        f"/api/v1/plans/{plan_id}/decision",
        json={
            "status": "ACTIVE",
            "decision_maker_notes": "Execution initiated for FY 2026-2027.",
        },
    )
    assert act_res.status_code == 200
    assert act_res.json()["status"] == "ACTIVE"


def test_plan_execution_review_endpoint(client: TestClient, seed_pipeline_data: dict):
    """Test the deterministic execution review endpoint /review."""
    inst_id = seed_pipeline_data["institution_id"]
    p7_id = seed_pipeline_data["strategic_options_analysis_id"]

    # Generate plan
    res = client.post(
        "/api/v1/plans/generate",
        json={
            "institution_id": inst_id,
            "title": "Reviewable Plan 2026",
            "horizon_start_year": 2026,
            "horizon_end_year": 2030,
            "strategic_options_analysis_id": p7_id,
            "override_selection_requirement": True,
        },
    )
    assert res.status_code == 201
    plan = res.json()
    plan_id = plan["id"]

    # Run execution review for 2026-2027
    rev_res = client.post(
        f"/api/v1/plans/{plan_id}/review",
        json={
            "review_period": "2026-2027",
            "review_date": "2027-04-15",
            "notes": "Mid-term execution review.",
        },
    )
    assert rev_res.status_code == 201, rev_res.text
    review = rev_res.json()

    assert review["strategic_plan_id"] == plan_id
    assert review["review_period"] == "2026-2027"
    assert review["overall_status"] in ["ON_TRACK", "AT_RISK", "OFF_TRACK", "INSUFFICIENT_EVIDENCE"]
    assert "leadership_disclaimer" in review
    assert isinstance(review["target_variances"], list)
    assert isinstance(review["milestone_statuses"], dict)
    assert isinstance(review["corrective_actions"], list)


def test_generation_validation_errors(client: TestClient):
    """Test validation errors on plan generation."""
    # 1. Non-existent institution
    res1 = client.post(
        "/api/v1/plans/generate",
        json={
            "institution_id": "non-existent-inst",
            "horizon_start_year": 2026,
            "horizon_end_year": 2030,
            "strategic_options_analysis_id": "non-existent-analysis",
        },
    )
    assert res1.status_code == 404

    # 2. Invalid horizon years
    res2 = client.post(
        "/api/v1/plans/generate",
        json={
            "institution_id": "inst-1",
            "horizon_start_year": 2030,
            "horizon_end_year": 2025,
            "strategic_options_analysis_id": "analysis-1",
        },
    )
    assert res2.status_code in [404, 422]
