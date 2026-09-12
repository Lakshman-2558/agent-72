"""Demo Script for Phase 8 — Strategic Plan Generation & Execution Framework for Agent 72.

End-to-End Pipeline Execution:
Evidence (Academic, Admissions, Placement, Research, Faculty, Infrastructure, Finance)
  -> Phase 4: Current Institutional Position Analysis
  -> Phase 5: Institutional Trajectory Analysis
  -> Phase 6: Strategic Intelligence Analysis
  -> Phase 7: Strategic Options, Scenarios & Prioritization
  -> Phase 8: Strategic Plan Generation & Execution Framework:
      1. Leadership Option Selection
      2. Plan Generation (Draft)
      3. Leadership Approval & Activation Governance
      4. Deterministic Execution Review & Corrective Actions
"""

import sys
from datetime import datetime, timezone, date
from pathlib import Path

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agent72.infrastructure.database.session import SessionLocal
from agent72.infrastructure.repositories.sqlalchemy_organization_repository import SQLAlchemyOrganizationRepository
from agent72.infrastructure.repositories.sqlalchemy_evidence_repository import SQLAlchemyEvidenceRepository
from agent72.infrastructure.repositories.sqlalchemy_analysis_repository import SQLAlchemyAnalysisRepository
from agent72.infrastructure.repositories.sqlalchemy_trajectory_repository import SQLAlchemyTrajectoryRepository
from agent72.infrastructure.repositories.sqlalchemy_strategic_intelligence_repository import SQLAlchemyStrategicIntelligenceRepository
from agent72.infrastructure.repositories.sqlalchemy_strategic_options_repository import SQLAlchemyStrategicOptionsRepository
from agent72.infrastructure.repositories.sqlalchemy_plan_repository import SQLAlchemyPlanRepository
from agent72.infrastructure.ai import get_ai_provider
from agent72.application.services.analysis_service import CurrentPositionAnalysisService
from agent72.application.services.trajectory_service import TrajectoryAnalysisService
from agent72.application.services.strategic_intelligence_service import StrategicIntelligenceService
from agent72.application.services.strategic_options_service import StrategicOptionsService
from agent72.application.services.strategic_plan_service import StrategicPlanExecutionService
from agent72.application.dtos.analysis_dto import CurrentPositionAnalysisRequestDTO
from agent72.application.dtos.trajectory_dto import TrajectoryAnalysisRequestDTO
from agent72.application.dtos.strategic_intelligence_dto import StrategicIntelligenceRequestDTO
from agent72.application.dtos.strategic_options_dto import StrategicOptionsRequestDTO
from agent72.application.dtos.strategic_plan_dto import (
    StrategicPlanGenerationRequestDTO,
    ExecutionReviewRequestDTO,
    PlanDecisionRequestDTO,
)
from agent72.domain.models.organization import Institution, OrganizationalUnit, UnitType, EntityStatus
from agent72.domain.models.evidence import (
    MetricDefinition,
    MetricDomain,
    MetricDirection,
    InstitutionalEvidence,
    SourceType,
    QualityTier,
)


def run_phase8_demo():
    print("=" * 90)
    print("   AGENT 72: STRATEGIC PLANNING AGENT - PHASE 8 STRATEGIC EXECUTION FRAMEWORK DEMO")
    print("=" * 90)

    session = SessionLocal()
    try:
        org_repo = SQLAlchemyOrganizationRepository(session)
        ev_repo = SQLAlchemyEvidenceRepository(session)
        analysis_repo = SQLAlchemyAnalysisRepository(session)
        traj_repo = SQLAlchemyTrajectoryRepository(session)
        strat_repo = SQLAlchemyStrategicIntelligenceRepository(session)
        options_repo = SQLAlchemyStrategicOptionsRepository(session)
        plan_repo = SQLAlchemyPlanRepository(session)
        ai_provider = get_ai_provider()

        # -------------------------------------------------------------
        # 1. Organization & Unit Setup
        # -------------------------------------------------------------
        inst = org_repo.get_institution_by_code("DEMO-APEX-P8")
        if not inst:
            inst = org_repo.create_institution(
                Institution(
                    code="DEMO-APEX-P8",
                    name="Apex Institute of Technology",
                    status=EntityStatus.ACTIVE,
                )
            )
        assert inst.id is not None

        existing_units = org_repo.list_units_by_institution(inst.id)
        unit_soe = next((u for u in existing_units if u.code == "DEMO-SOE-P8"), None)
        if not unit_soe:
            unit_soe = org_repo.create_unit(
                OrganizationalUnit(
                    institution_id=inst.id,
                    code="DEMO-SOE-P8",
                    name="School of Engineering",
                    unit_type=UnitType.SCHOOL,
                    status=EntityStatus.ACTIVE,
                )
            )
        unit_crp = next((u for u in existing_units if u.code == "DEMO-CRP-P8"), None)
        if not unit_crp:
            unit_crp = org_repo.create_unit(
                OrganizationalUnit(
                    institution_id=inst.id,
                    code="DEMO-CRP-P8",
                    name="Corporate Relations & Placement",
                    unit_type=UnitType.DEPARTMENT,
                    status=EntityStatus.ACTIVE,
                )
            )

        print(f"\n[1/7] Organization verified: '{inst.name}' ({inst.code})")
        print(f"      Units: '{unit_soe.name}', '{unit_crp.name}'")

        # -------------------------------------------------------------
        # 2. Register Canonical Metric Definitions
        # -------------------------------------------------------------
        metrics_meta = [
            ("placement.rate", "Placement Rate", MetricDomain.PLACEMENT_EMPLOYER_DEMAND, MetricDirection.HIGHER_IS_BETTER, "%", 85.0),
            ("regional.tech_demand_index", "Regional Tech Employer Demand Index", MetricDomain.PLACEMENT_EMPLOYER_DEMAND, MetricDirection.HIGHER_IS_BETTER, "index", 80.0),
            ("admissions.yield", "Admissions Yield", MetricDomain.ADMISSIONS_MARKET, MetricDirection.HIGHER_IS_BETTER, "%", 45.0),
            ("research.publications", "Annual Peer-Reviewed Publications", MetricDomain.RESEARCH_PRODUCTIVITY, MetricDirection.HIGHER_IS_BETTER, "count", 70.0),
            ("infra.lab_utilization_rate", "Laboratory Facility Utilization", MetricDomain.INFRASTRUCTURE, MetricDirection.LOWER_IS_BETTER, "%", 75.0),
            ("faculty.phd_ratio", "Faculty Doctoral Qualification Ratio", MetricDomain.FACULTY_CAPABILITY, MetricDirection.HIGHER_IS_BETTER, "%", 75.0),
        ]

        for key, name, domain, direction, unit_name, target in metrics_meta:
            existing = ev_repo.get_metric_definition(key)
            if not existing:
                ev_repo.create_metric_definition(
                    MetricDefinition(
                        metric_key=key,
                        name=name,
                        domain=domain,
                        direction=direction,
                        default_unit=unit_name,
                        description=f"{name} with target benchmark {target}",
                    )
                )

        # -------------------------------------------------------------
        # 3. Ingest Multi-Period Evidence
        # -------------------------------------------------------------
        now = datetime.now(timezone.utc)
        evidence_records = [
            # Placement: 88% -> 80% -> 72%
            ("placement.rate", 88.0, "%", "2022-2023", MetricDomain.PLACEMENT_EMPLOYER_DEMAND, "Career Services"),
            ("placement.rate", 80.0, "%", "2023-2024", MetricDomain.PLACEMENT_EMPLOYER_DEMAND, "Career Services"),
            ("placement.rate", 72.0, "%", "2024-2025", MetricDomain.PLACEMENT_EMPLOYER_DEMAND, "Career Services"),

            # Employer Demand: 85 -> 75 -> 68
            ("regional.tech_demand_index", 85.0, "index", "2022-2023", MetricDomain.PLACEMENT_EMPLOYER_DEMAND, "Labor Bureau"),
            ("regional.tech_demand_index", 75.0, "index", "2023-2024", MetricDomain.PLACEMENT_EMPLOYER_DEMAND, "Labor Bureau"),
            ("regional.tech_demand_index", 68.0, "index", "2024-2025", MetricDomain.PLACEMENT_EMPLOYER_DEMAND, "Labor Bureau"),

            # Admissions Yield: 45% -> 38% -> 30%
            ("admissions.yield", 45.0, "%", "2022-2023", MetricDomain.ADMISSIONS_MARKET, "Admissions Office"),
            ("admissions.yield", 38.0, "%", "2023-2024", MetricDomain.ADMISSIONS_MARKET, "Admissions Office"),
            ("admissions.yield", 30.0, "%", "2024-2025", MetricDomain.ADMISSIONS_MARKET, "Admissions Office"),

            # Research: 40 -> 52 -> 65
            ("research.publications", 40.0, "count", "2022-2023", MetricDomain.RESEARCH_PRODUCTIVITY, "R&D Cell"),
            ("research.publications", 52.0, "count", "2023-2024", MetricDomain.RESEARCH_PRODUCTIVITY, "R&D Cell"),
            ("research.publications", 65.0, "count", "2024-2025", MetricDomain.RESEARCH_PRODUCTIVITY, "R&D Cell"),

            # Lab Utilization: 88.5% (Capacity risk)
            ("infra.lab_utilization_rate", 88.5, "%", "2024-2025", MetricDomain.INFRASTRUCTURE, "Campus Facilities"),

            # Faculty PhD Ratio: 64.0%
            ("faculty.phd_ratio", 64.0, "%", "2024-2025", MetricDomain.FACULTY_CAPABILITY, "HR Cell"),
        ]

        batch_items = []
        for key, val, unit_name, period, domain, src in evidence_records:
            idempotency = f"{inst.id}_{key}_{period}_p8_demo"
            existing = ev_repo.find_existing_evidence(inst.id, idempotency)
            if not existing:
                batch_items.append(
                    InstitutionalEvidence(
                        institution_id=inst.id,
                        unit_id=unit_crp.id if "placement" in key else unit_soe.id,
                        metric_key=key,
                        domain=domain,
                        numeric_value=val,
                        unit=unit_name,
                        period=period,
                        as_of_date=date(2025, 6, 30),
                        captured_at=now,
                        source_type=SourceType.MANUAL,
                        source_name=src,
                        quality_tier=QualityTier.VERIFIED,
                        idempotency_key=idempotency,
                    )
                )

        if batch_items:
            ev_repo.record_evidence_batch(batch_items)
            print(f"[2/7] Ingested {len(batch_items)} historical observations across 3 academic years.")
        else:
            print("[2/7] Historical evidence records already present.")

        # -------------------------------------------------------------
        # 4. Run Phases 4, 5, 6 & 7 Prerequisites
        # -------------------------------------------------------------
        pos_svc = CurrentPositionAnalysisService(
            analysis_repository=analysis_repo,
            evidence_repository=ev_repo,
            organization_repository=org_repo,
        )
        traj_svc = TrajectoryAnalysisService(
            trajectory_repository=traj_repo,
            evidence_repository=ev_repo,
            organization_repository=org_repo,
            analysis_repository=analysis_repo,
        )
        strat_svc = StrategicIntelligenceService(
            strategic_intelligence_repository=strat_repo,
            analysis_repository=analysis_repo,
            trajectory_repository=traj_repo,
            evidence_repository=ev_repo,
            organization_repository=org_repo,
            ai_provider=ai_provider,
        )
        opt_svc = StrategicOptionsService(
            strategic_options_repository=options_repo,
            strategic_intelligence_repository=strat_repo,
            ai_provider=ai_provider,
        )

        pos_dto = pos_svc.generate_current_position_analysis(
            CurrentPositionAnalysisRequestDTO(
                institution_id=inst.id,
                analysis_period="2024-2025",
                title="Institutional Baseline Assessment",
            )
        )

        traj_dto = traj_svc.generate_trajectory_analysis(
            TrajectoryAnalysisRequestDTO(
                institution_id=inst.id,
                analysis_period="2024-2025",
                current_position_analysis_id=pos_dto.id,
                title="Institutional Longitudinal Trajectory",
            )
        )

        strat_dto = strat_svc.generate_strategic_intelligence_analysis(
            StrategicIntelligenceRequestDTO(
                institution_id=inst.id,
                analysis_period="2024-2025",
                current_position_analysis_id=pos_dto.id,
                trajectory_analysis_id=traj_dto.id,
                include_ai_synthesis=False,
            )
        )

        opt_dto = opt_svc.generate_strategic_options_analysis(
            StrategicOptionsRequestDTO(
                institution_id=inst.id,
                analysis_period="2024-2025",
                strategic_intelligence_analysis_id=strat_dto.id,
                include_ai_synthesis=False,
            )
        )

        print(f"[3/7] Upstream intelligence pipeline complete:")
        print(f"      - Position ID:     {pos_dto.id}")
        print(f"      - Trajectory ID:   {traj_dto.id}")
        print(f"      - Intelligence ID: {strat_dto.id}")
        print(f"      - Options ID:      {opt_dto.id} ({len(opt_dto.options)} strategic options generated)")

        # -------------------------------------------------------------
        # 5. Phase 8: Strategic Plan Generation from Selected Options
        # -------------------------------------------------------------
        plan_svc = StrategicPlanExecutionService(
            plan_repository=plan_repo,
            options_repository=options_repo,
            evidence_repository=ev_repo,
            organization_repository=org_repo,
            ai_provider=ai_provider,
        )

        selected_opt_ids = opt_dto.prioritized_option_ids[:2]
        print(f"\n[4/7] Leadership selecting top {len(selected_opt_ids)} prioritized options for strategic plan:")
        for idx, oid in enumerate(selected_opt_ids, 1):
            matching_opt = next((o for o in opt_dto.options if o.id == oid), None)
            print(f"      {idx}. [{oid}] {matching_opt.title if matching_opt else 'Option'}")

        gen_req = StrategicPlanGenerationRequestDTO(
            institution_id=inst.id,
            title="Institutional Strategic Vision 2026-2030",
            horizon_start_year=2026,
            horizon_end_year=2030,
            strategic_options_analysis_id=opt_dto.id,
            selected_option_ids=selected_opt_ids,
            override_selection_requirement=True,
            review_period="ANNUAL",
        )
        plan_res = plan_svc.generate_plan_from_options(gen_req)

        print(f"\n[5/7] Strategic Plan Generated:")
        print(f"      Plan ID:    {plan_res.id}")
        print(f"      Title:      {plan_res.title}")
        print(f"      Horizon:    {plan_res.horizon_start_year} - {plan_res.horizon_end_year}")
        print(f"      Status:     {plan_res.status} (Initial draft requires leadership approval)")
        print(f"      Objectives: {len(plan_res.objectives)}")

        for o_idx, obj in enumerate(plan_res.objectives, 1):
            print(f"\n      Objective {o_idx}: {obj.title}")
            print(f"        Rationale: {obj.strategic_rationale}")
            print(f"        Lead Unit: {obj.owner_unit_id}")
            print(f"        Targets ({len(obj.targets)}):")
            for tgt in obj.targets:
                gap_str = f" [Gap: {tgt.gap:+.1f} {tgt.gap_unit_label or tgt.unit}]" if tgt.gap is not None else ""
                print(f"          * {tgt.metric_key}: Baseline {tgt.baseline_value}{tgt.unit} -> Target {tgt.target_value}{tgt.unit} ({tgt.target_period}){gap_str}")
            print(f"        Initiatives ({len(obj.initiatives)}):")
            for init in obj.initiatives:
                print(f"          - Initiative: {init.title} [Owner: {init.owner_unit_id}, Resources: {init.resource_requirement}]")
                for ms in init.milestones:
                    print(f"            Milestone: {ms.title} (Due: {ms.due_period}, Status: {ms.status})")

        # -------------------------------------------------------------
        # 6. Governance Decision Lifecycle
        # -------------------------------------------------------------
        print(f"\n[6/7] Exercising Leadership Governance Lifecycle:")
        dec_approve = plan_svc.update_plan_decision(
            plan_res.id,
            PlanDecisionRequestDTO(
                decision="APPROVE",
                notes="Executive Board approved the 2026-2030 Institutional Strategic Plan.",
                decided_by="Board of Regents",
            ),
        )
        print(f"      - Action: APPROVE  -> Plan Status: {dec_approve.status}")

        dec_active = plan_svc.update_plan_decision(
            plan_res.id,
            PlanDecisionRequestDTO(
                decision="ACTIVATE",
                notes="Plan formally activated for operational execution in FY 2026-2027.",
                decided_by="Vice-Chancellor / Provost",
            ),
        )
        print(f"      - Action: ACTIVATE -> Plan Status: {dec_active.status}")

        # -------------------------------------------------------------
        # 7. Execution Review & Diagnostic Signals
        # -------------------------------------------------------------
        print(f"\n[7/7] Ingesting Observed Execution Evidence for 2026-2027:")
        # 1 target on track (research), 1 at risk (placement), 1 unobserved (admissions)
        observed_items = [
            InstitutionalEvidence(
                institution_id=inst.id,
                unit_id=unit_crp.id,
                metric_key="placement.rate",
                domain=MetricDomain.PLACEMENT_EMPLOYER_DEMAND,
                numeric_value=78.0,  # Target was ~82%, baseline 72% -> improved but lagging target (+6% vs +10% target)
                unit="%",
                period="2026-2027",
                as_of_date=date(2027, 4, 1),
                captured_at=now,
                source_type=SourceType.MANUAL,
                source_name="Placement Audit",
                quality_tier=QualityTier.VERIFIED,
                idempotency_key=f"{inst.id}_placement.rate_2026-2027_obs",
            ),
            InstitutionalEvidence(
                institution_id=inst.id,
                unit_id=unit_soe.id,
                metric_key="research.publications",
                domain=MetricDomain.RESEARCH_PRODUCTIVITY,
                numeric_value=85.0,  # Target was ~81.2 -> Exceeded target!
                unit="count",
                period="2026-2027",
                as_of_date=date(2027, 4, 1),
                captured_at=now,
                source_type=SourceType.MANUAL,
                source_name="Research Audit",
                quality_tier=QualityTier.VERIFIED,
                idempotency_key=f"{inst.id}_research.publications_2026-2027_obs",
            ),
        ]
        ev_repo.record_evidence_batch(observed_items)
        print(f"      Ingested 2 observed evidence records for period '2026-2027'.")

        review_req = ExecutionReviewRequestDTO(
            review_period="2026-2027",
            notes="Annual Mid-Term Operational Review FY 2026-2027.",
        )
        review = plan_svc.record_execution_review(plan_res.id, review_req)

        print(f"\n" + "=" * 90)
        print(f"   EXECUTION REVIEW RESULTS FOR PERIOD: {review.review_period}")
        print("=" * 90)
        print(f"Review ID:        {review.id}")
        print(f"Overall Status:   {review.overall_status}")
        print(f"Progress Summary: {review.progress_summary}")
        print(f"\nTarget Variances (Direction-Aware):")
        for v in review.target_variances:
            print(f"  * [{v.metric_key}] Status: {v.status}")
            print(f"    Baseline: {v.baseline_value}{v.unit} | Target: {v.target_value}{v.unit} | Observed: {v.observed_value}{v.unit}")
            print(f"    Variance Notation: {v.variance_notation}")
            if v.notes:
                print(f"    Notes: {v.notes}")

        print(f"\nDiagnostic Signals ({len(review.diagnostic_signals)}):")
        for s in review.diagnostic_signals:
            print(f"  * [{s.get('signal_type')}] {s.get('summary') or s.get('message')}")

        print(f"\nCorrective Action Candidates ({len(review.corrective_actions)}):")
        for ca in review.corrective_actions:
            print(f"  * [{ca.signal_type}] {ca.title}")
            print(f"    Suggested Action: {ca.suggested_action}")
            print(f"    Rationale: {ca.rationale}")
            print(f"    Requires Leadership Approval: {ca.requires_leadership_approval}")

        print(f"\nMandatory Leadership Disclaimer:")
        print(f"  \"{review.leadership_disclaimer}\"")
        print("=" * 90)
        print("   PHASE 8 DEMO COMPLETED SUCCESSFULLY!")
        print("=" * 90)

    finally:
        session.close()


if __name__ == "__main__":
    run_phase8_demo()
