"""Integration tests for Strategic Execution, Initiatives, Milestones, and Annual Reviews."""

from fastapi.testclient import TestClient


def test_plan_with_initiatives_milestones_and_review(client: TestClient):
    payload = {
        "title": "Vision 2030 Research & Innovation Roadmap",
        "institution_name": "Apex University",
        "horizon_start_year": 2026,
        "horizon_end_year": 2030,
        "existing_commitments": "Existing AICTE approval commitments and UGC compliance mandates.",
        "review_period": "ANNUAL",
        "objectives": [
            {
                "title": "Elevate Institutional Research Footprint",
                "description": "Increase Tier-1 journal output across all engineering departments",
                "target_metric": "Annual Q1 Publications",
                "metric_key": "research.publications.q1",
                "target_period": "2027-2028",
                "baseline_value": 150.0,
                "target_value": 300.0,
                "weight": 2.0,
                "owner": "Dean of Research",
                "initiatives": [
                    {
                        "title": "Seed Grant Incentive Program",
                        "description": "Provide competitive funding for interdisciplinary lab projects",
                        "owner": "Associate Dean R&D",
                        "budget": 2500000.0,
                        "status": "IN_PROGRESS",
                        "milestones": [
                            {
                                "title": "Publish RFP and selection criteria",
                                "target_date": "2026-06-30",
                                "status": "ACHIEVED",
                            },
                            {
                                "title": "Disburse first cycle of seed grants",
                                "target_date": "2026-09-30",
                                "status": "PENDING",
                            },
                        ],
                    }
                ],
            }
        ],
        "strategic_options": [
            {
                "title": "Cross-Departmental Lab Sharing",
                "rationale": "Optimizes capital expenditure across CSE and ECE",
                "resource_intensity": "MEDIUM",
                "risk_level": "LOW",
            }
        ],
        "scenarios": [
            {
                "name": "High Grant Adoption Scenario",
                "assumptions": "Faculty participation exceeds 60%",
                "projected_outcome": "Citation index growth of 25% year-over-year",
            }
        ],
    }

    # 1. Create strategic plan with initiatives and milestones
    create_res = client.post("/api/v1/plans", json=payload)
    assert create_res.status_code == 201, create_res.text
    created = create_res.json()
    plan_id = created["id"]
    assert created["review_period"] == "ANNUAL"
    assert created["existing_commitments"] is not None

    assert len(created["objectives"]) == 1
    obj = created["objectives"][0]
    assert obj["metric_key"] == "research.publications.q1"
    assert obj["target_period"] == "2027-2028"

    assert len(obj["initiatives"]) == 1
    init = obj["initiatives"][0]
    assert init["title"] == "Seed Grant Incentive Program"
    assert init["status"] == "IN_PROGRESS"
    assert init["budget"] == 2500000.0

    assert len(init["milestones"]) == 2
    assert init["milestones"][0]["title"] == "Publish RFP and selection criteria"
    assert init["milestones"][0]["status"] == "ACHIEVED"

    # 2. Add an annual execution review
    review_payload = {
        "period": "2026-2027",
        "review_date": "2027-04-15",
        "progress_summary": "Year 1 execution tracking shows 80% milestone achievement with positive faculty engagement.",
        "variance_notes": "Minor procurement delay on specialized server equipment.",
        "recommendations": "Accelerate equipment vendor tender process for Year 2.",
    }
    review_res = client.post(f"/api/v1/plans/{plan_id}/reviews", json=review_payload)
    assert review_res.status_code == 201
    rev_data = review_res.json()
    assert rev_data["period"] == "2026-2027"
    assert rev_data["plan_id"] == plan_id

    # 3. Retrieve plan and check execution reviews are embedded
    get_res = client.get(f"/api/v1/plans/{plan_id}")
    assert get_res.status_code == 200
    plan_data = get_res.json()
    assert len(plan_data["execution_reviews"]) == 1
    assert plan_data["execution_reviews"][0]["period"] == "2026-2027"
