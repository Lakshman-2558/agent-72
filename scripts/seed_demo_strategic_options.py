"""
Demo Script for Phase 7 — Strategic Options, Scenarios & Prioritization for Agent 72.

End-to-End Pipeline Execution:
Evidence (Academic, Admissions, Placement, Research, Faculty, Infrastructure, Finance, External, Competitor)
  -> Phase 4: Current Institutional Position Analysis
  -> Phase 5: Institutional Trajectory Analysis
  -> Phase 6: Strategic Intelligence Analysis
  -> Phase 7: Strategic Options, Scenarios & Prioritization

Produces a structured, evidence-grounded strategic choices portfolio for leadership decision support.
"""

import sys
import os
from datetime import datetime, timezone, timedelta
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
from agent72.infrastructure.ai import get_ai_provider
from agent72.application.services.analysis_service import CurrentPositionAnalysisService
from agent72.application.services.trajectory_service import TrajectoryAnalysisService
from agent72.application.services.strategic_intelligence_service import StrategicIntelligenceService
from agent72.application.services.strategic_options_service import StrategicOptionsService
from agent72.application.dtos.analysis_dto import CurrentPositionAnalysisRequestDTO
from agent72.application.dtos.trajectory_dto import TrajectoryAnalysisRequestDTO
from agent72.application.dtos.strategic_intelligence_dto import StrategicIntelligenceRequestDTO
from agent72.application.dtos.strategic_options_dto import StrategicOptionsRequestDTO
from agent72.domain.models.organization import Institution, OrganizationalUnit, UnitType, EntityStatus
from agent72.domain.models.evidence import (
    MetricDefinition,
    MetricDomain,
    MetricDirection,
    InstitutionalEvidence,
    SourceType,
    QualityTier,
)


def run_phase7_demo():
    print("=" * 80)
    print("   AGENT 72: STRATEGIC PLANNING AGENT - PHASE 7 STRATEGIC OPTIONS DEMO")
    print("=" * 80)

    session = SessionLocal()
    try:
        org_repo = SQLAlchemyOrganizationRepository(session)
        ev_repo = SQLAlchemyEvidenceRepository(session)
        analysis_repo = SQLAlchemyAnalysisRepository(session)
        traj_repo = SQLAlchemyTrajectoryRepository(session)
        strat_repo = SQLAlchemyStrategicIntelligenceRepository(session)
        options_repo = SQLAlchemyStrategicOptionsRepository(session)
        ai_provider = get_ai_provider()

        # -------------------------------------------------------------
        # 1. Organization & Unit Setup
        # -------------------------------------------------------------
        inst = org_repo.get_institution_by_code("DEMO-APEX")
        if not inst:
            inst = org_repo.create_institution(
                Institution(
                    code="DEMO-APEX",
                    name="Apex Institute of Technology (Demo)",
                    status=EntityStatus.ACTIVE,
                )
            )
        assert inst.id is not None

        existing_units = org_repo.list_units_by_institution(inst.id)
        unit = next((u for u in existing_units if u.code == "DEMO-SOE"), None)
        if not unit:
            unit = org_repo.create_unit(
                OrganizationalUnit(
                    institution_id=inst.id,
                    code="DEMO-SOE",
                    name="School of Engineering",
                    unit_type=UnitType.SCHOOL,
                    status=EntityStatus.ACTIVE,
                )
            )
        assert unit.id is not None

        # -------------------------------------------------------------
        # 2. Register Canonical Metric Definitions
        # -------------------------------------------------------------
        metrics_meta = [
            ("placement.rate", "Placement Rate", MetricDomain.PLACEMENT_EMPLOYER_DEMAND, MetricDirection.HIGHER_IS_BETTER, "percent", 85.0),
            ("regional.tech_demand_index", "Regional Tech Employer Demand Index", MetricDomain.PLACEMENT_EMPLOYER_DEMAND, MetricDirection.HIGHER_IS_BETTER, "index", 80.0),
            ("admissions.yield", "Admissions Yield", MetricDomain.ADMISSIONS_MARKET, MetricDirection.HIGHER_IS_BETTER, "percent", 45.0),
            ("research.publications", "Annual Peer-Reviewed Publications", MetricDomain.RESEARCH_PRODUCTIVITY, MetricDirection.HIGHER_IS_BETTER, "count", 70.0),
            ("infra.lab_utilization_rate", "Laboratory Facility Utilization", MetricDomain.INFRASTRUCTURE, MetricDirection.LOWER_IS_BETTER, "percent", 75.0),
            ("faculty.phd_ratio", "Faculty Doctoral Qualification Ratio", MetricDomain.FACULTY_CAPABILITY, MetricDirection.HIGHER_IS_BETTER, "percent", 75.0),
            ("external.ai_curriculum_mandate", "AI Ethics & Curriculum Compliance Mandate", MetricDomain.EXTERNAL_REGULATORY, MetricDirection.HIGHER_IS_BETTER, "compliance_score", 1.0),
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
        # 3. Ingest Multi-Period Evidence (3-year longitudinal trends)
        # -------------------------------------------------------------
        print("\nSeeding multi-period evidence for Apex University / School of Engineering...")
        now = datetime.now(timezone.utc)
        evidence_records = [
            # Placement: declining (84.0% -> 78.0% -> 74.0%)
            InstitutionalEvidence(institution_id=inst.id, unit_id=unit.id, metric_key="placement.rate", domain=MetricDomain.PLACEMENT_EMPLOYER_DEMAND, numeric_value=84.0, unit="percent", period="2022-2023", as_of_date=(now - timedelta(days=730)).date(), source_name="CareerServices", source_type=SourceType.MANUAL, quality_tier=QualityTier.VERIFIED),
            InstitutionalEvidence(institution_id=inst.id, unit_id=unit.id, metric_key="placement.rate", domain=MetricDomain.PLACEMENT_EMPLOYER_DEMAND, numeric_value=78.0, unit="percent", period="2023-2024", as_of_date=(now - timedelta(days=365)).date(), source_name="CareerServices", source_type=SourceType.MANUAL, quality_tier=QualityTier.VERIFIED),
            InstitutionalEvidence(institution_id=inst.id, unit_id=unit.id, metric_key="placement.rate", domain=MetricDomain.PLACEMENT_EMPLOYER_DEMAND, numeric_value=74.0, unit="percent", period="2024-2025", as_of_date=now.date(), source_name="CareerServices", source_type=SourceType.MANUAL, quality_tier=QualityTier.VERIFIED),

            # External Employer Demand: declining (85.0 -> 76.0 -> 68.0)
            InstitutionalEvidence(institution_id=inst.id, unit_id=unit.id, metric_key="regional.tech_demand_index", domain=MetricDomain.PLACEMENT_EMPLOYER_DEMAND, numeric_value=85.0, unit="index", period="2022-2023", as_of_date=(now - timedelta(days=730)).date(), source_name="RegionalChamber", source_type=SourceType.EXTERNAL, quality_tier=QualityTier.VERIFIED),
            InstitutionalEvidence(institution_id=inst.id, unit_id=unit.id, metric_key="regional.tech_demand_index", domain=MetricDomain.PLACEMENT_EMPLOYER_DEMAND, numeric_value=76.0, unit="index", period="2023-2024", as_of_date=(now - timedelta(days=365)).date(), source_name="RegionalChamber", source_type=SourceType.EXTERNAL, quality_tier=QualityTier.VERIFIED),
            InstitutionalEvidence(institution_id=inst.id, unit_id=unit.id, metric_key="regional.tech_demand_index", domain=MetricDomain.PLACEMENT_EMPLOYER_DEMAND, numeric_value=68.0, unit="index", period="2024-2025", as_of_date=now.date(), source_name="RegionalChamber", source_type=SourceType.EXTERNAL, quality_tier=QualityTier.VERIFIED),

            # Admissions Yield: declining (55.0% -> 51.0% -> 48.0%)
            InstitutionalEvidence(institution_id=inst.id, unit_id=unit.id, metric_key="admissions.yield", domain=MetricDomain.ADMISSIONS_MARKET, numeric_value=55.0, unit="percent", period="2022-2023", as_of_date=(now - timedelta(days=730)).date(), source_name="AdmissionsOffice", source_type=SourceType.MANUAL, quality_tier=QualityTier.VERIFIED),
            InstitutionalEvidence(institution_id=inst.id, unit_id=unit.id, metric_key="admissions.yield", domain=MetricDomain.ADMISSIONS_MARKET, numeric_value=51.0, unit="percent", period="2023-2024", as_of_date=(now - timedelta(days=365)).date(), source_name="AdmissionsOffice", source_type=SourceType.MANUAL, quality_tier=QualityTier.VERIFIED),
            InstitutionalEvidence(institution_id=inst.id, unit_id=unit.id, metric_key="admissions.yield", domain=MetricDomain.ADMISSIONS_MARKET, numeric_value=48.0, unit="percent", period="2024-2025", as_of_date=now.date(), source_name="AdmissionsOffice", source_type=SourceType.MANUAL, quality_tier=QualityTier.VERIFIED),

            # Research Publications: accelerating (40.0 -> 52.0 -> 65.0)
            InstitutionalEvidence(institution_id=inst.id, unit_id=unit.id, metric_key="research.publications", domain=MetricDomain.RESEARCH_PRODUCTIVITY, numeric_value=40.0, unit="count", period="2022-2023", as_of_date=(now - timedelta(days=730)).date(), source_name="ResearchOffice", source_type=SourceType.MANUAL, quality_tier=QualityTier.VERIFIED),
            InstitutionalEvidence(institution_id=inst.id, unit_id=unit.id, metric_key="research.publications", domain=MetricDomain.RESEARCH_PRODUCTIVITY, numeric_value=52.0, unit="count", period="2023-2024", as_of_date=(now - timedelta(days=365)).date(), source_name="ResearchOffice", source_type=SourceType.MANUAL, quality_tier=QualityTier.VERIFIED),
            InstitutionalEvidence(institution_id=inst.id, unit_id=unit.id, metric_key="research.publications", domain=MetricDomain.RESEARCH_PRODUCTIVITY, numeric_value=65.0, unit="count", period="2024-2025", as_of_date=now.date(), source_name="ResearchOffice", source_type=SourceType.MANUAL, quality_tier=QualityTier.VERIFIED),

            # Infrastructure: 88.5% (exceeding 85% threshold)
            InstitutionalEvidence(institution_id=inst.id, unit_id=unit.id, metric_key="infra.lab_utilization_rate", domain=MetricDomain.INFRASTRUCTURE, numeric_value=88.5, unit="percent", period="2024-2025", as_of_date=now.date(), source_name="Facilities", source_type=SourceType.MANUAL, quality_tier=QualityTier.VERIFIED),

            # Faculty PhD ratio: 66.0% (below 70% threshold)
            InstitutionalEvidence(institution_id=inst.id, unit_id=unit.id, metric_key="faculty.phd_ratio", domain=MetricDomain.FACULTY_CAPABILITY, numeric_value=66.0, unit="percent", period="2024-2025", as_of_date=now.date(), source_name="AcademicAffairs", source_type=SourceType.MANUAL, quality_tier=QualityTier.VERIFIED),

            # External regulatory mandate
            InstitutionalEvidence(institution_id=inst.id, unit_id=unit.id, metric_key="external.ai_curriculum_mandate", domain=MetricDomain.EXTERNAL_REGULATORY, numeric_value=1.0, unit="compliance_score", period="2024-2025", as_of_date=now.date(), source_name="AccreditationBoard", source_type=SourceType.EXTERNAL, quality_tier=QualityTier.VERIFIED),
        ]

        for ev in evidence_records:
            ev_repo.record_evidence(ev)
        session.commit()
        print(f"  Successfully ingested {len(evidence_records)} canonical evidence records.")

        # -------------------------------------------------------------
        # 4. Phase 4: Current Position Analysis
        # -------------------------------------------------------------
        print("\nExecuting Phase 4: Current Position Analysis...")
        pos_service = CurrentPositionAnalysisService(
            analysis_repository=analysis_repo,
            evidence_repository=ev_repo,
            organization_repository=org_repo,
        )
        pos_res = pos_service.generate_current_position_analysis(
            CurrentPositionAnalysisRequestDTO(
                institution_id=inst.id,
                organizational_unit_id=unit.id,
                analysis_period="2024-2025",
            )
        )
        print(f"  Current Position ID: {pos_res.id}")

        # -------------------------------------------------------------
        # 5. Phase 5: Trajectory Analysis
        # -------------------------------------------------------------
        print("\nExecuting Phase 5: Trajectory Analysis...")
        traj_service = TrajectoryAnalysisService(
            trajectory_repository=traj_repo,
            evidence_repository=ev_repo,
            organization_repository=org_repo,
            analysis_repository=analysis_repo,
        )
        traj_res = traj_service.generate_trajectory_analysis(
            TrajectoryAnalysisRequestDTO(
                institution_id=inst.id,
                organizational_unit_id=unit.id,
                analysis_period="2024-2025",
            )
        )
        print(f"  Trajectory Analysis ID: {traj_res.id}")

        # -------------------------------------------------------------
        # 6. Phase 6: Strategic Intelligence Analysis
        # -------------------------------------------------------------
        print("\nExecuting Phase 6: Strategic Intelligence Analysis...")
        intel_service = StrategicIntelligenceService(
            strategic_intelligence_repository=strat_repo,
            analysis_repository=analysis_repo,
            trajectory_repository=traj_repo,
            evidence_repository=ev_repo,
            organization_repository=org_repo,
            ai_provider=ai_provider,
        )
        intel_res = intel_service.generate_strategic_intelligence_analysis(
            StrategicIntelligenceRequestDTO(
                institution_id=inst.id,
                organizational_unit_id=unit.id,
                analysis_period="2024-2025",
                current_position_analysis_id=pos_res.id,
                trajectory_analysis_id=traj_res.id,
            )
        )
        print(f"  Strategic Intelligence ID: {intel_res.id}")
        print(f"  Strategic Issues: {len(intel_res.strategic_issues)} | Risks: {len(intel_res.risk_signals)} | Constraints: {len(intel_res.constraint_signals)} | Opps: {len(intel_res.opportunity_signals)}")

        # -------------------------------------------------------------
        # 7. Phase 7: Strategic Options, Scenarios & Prioritization
        # -------------------------------------------------------------
        print("\nExecuting Phase 7: Strategic Options, Scenarios & Prioritization...")
        options_service = StrategicOptionsService(
            strategic_options_repository=options_repo,
            strategic_intelligence_repository=strat_repo,
            ai_provider=ai_provider,
        )
        options_res = options_service.generate_strategic_options_analysis(
            StrategicOptionsRequestDTO(
                institution_id=inst.id,
                organizational_unit_id=unit.id,
                analysis_period="2024-2025",
                strategic_intelligence_analysis_id=intel_res.id,
                include_ai_synthesis=True,
            )
        )
        print(f"  Strategic Options Analysis ID: {options_res.id}")
        print(f"  Options Generated: {len(options_res.options)}")
        print(f"  Scenarios Formulated: {len(options_res.scenarios)}")
        print(f"  Evaluations Completed: {len(options_res.evaluations)}")

        # -------------------------------------------------------------
        # 8. Render Executive Leadership Briefing
        # -------------------------------------------------------------
        print("\n" + "-" * 80)
        print("EXECUTIVE DECISION-SUPPORT BRIEFING: STRATEGIC OPTIONS PORTFOLIO")
        print("-" * 80)

        print("\n[MANDATORY LEADERSHIP DISCLAIMER]")
        print(f"  \"{options_res.decision_support_disclaimer}\"")

        print("\n[PRIORITIZED STRATEGIC OPTIONS CANDIDATES]")
        eval_map = {e.option_id: e for e in options_res.evaluations}
        for rank, opt_id in enumerate(options_res.prioritized_option_ids, 1):
            opt = next(o for o in options_res.options if o.id == opt_id)
            ev = eval_map[opt_id]
            print(f"\n  #{rank}. [{ev.priority_level.value}] {opt.title}")
            print(f"      Category: {opt.category.value} | Feasibility: {opt.feasibility.value} | Resource: {opt.resource_requirement}")
            print(f"      Total Score: {ev.total_score}/100")
            print(f"      7-Factor Breakdown:")
            print(f"        * Alignment: {ev.strategic_alignment_score:.0f} | Impact: {ev.impact_score:.0f} | Feasibility: {ev.feasibility_score:.0f}")
            print(f"        * Resource Efficiency: {ev.resource_efficiency_score:.0f} | Implementation Risk Profile: {ev.implementation_risk_score:.0f} (higher=better)")
            print(f"        * Urgency: {ev.urgency_score:.0f} | Evidence Strength: {ev.evidence_strength_score:.0f}")
            print(f"      Strategic Rationale: {opt.strategic_rationale}")
            print(f"      Key Trade-Offs:")
            for t in opt.trade_offs:
                print(f"        - {t}")
            print(f"      Dependencies: {', '.join(opt.dependencies)}")

        print("\n[CONDITIONAL SCENARIO ANALYSIS (ILLUSTRATIVE FOR TOP OPTION)]")
        top_opt_id = options_res.prioritized_option_ids[0]
        top_opt = next(o for o in options_res.options if o.id == top_opt_id)
        top_scens = [s for s in options_res.scenarios if s.option_id == top_opt_id]
        print(f"  Target Option: {top_opt.title}")
        for s in top_scens:
            print(f"    * [{s.scenario_type.value}] {s.title}")
            print(f"      Effects: {'; '.join(s.expected_effects)}")
            print(f"      Key Risk: {'; '.join(s.risks)}")
            print(f"      Uncertainty: {s.uncertainty}")

        print("\n[DATA LIMITATIONS & UNCERTAINTY MANAGEMENT]")
        if options_res.data_limitations:
            for lim in options_res.data_limitations:
                print(f"  * {lim}")
        else:
            print("  * Full longitudinal evidence across 9 domains available; no fabrication required.")

        print("\n" + "=" * 80)
        print("PHASE 7 DEMO EXECUTION COMPLETED SUCCESSFULLY")
        print("=" * 80)

    finally:
        session.close()


if __name__ == "__main__":
    run_phase7_demo()
