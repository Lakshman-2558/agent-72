"""
Demo Data Seeder for Institutional Trajectory Analysis (Phase 5).

Populates realistic 3-year multi-domain canonical evidence series for:
- Academic Performance
- Admissions & Market
- Placement & Employer Demand
- Research
- Faculty Capability
- Infrastructure

Adheres to explicit provenance:
- Agent-generated: source_type = AGENT
- Manual: source_type = MANUAL
Clearly distinguishes simulated demo evidence from real external agents.
"""

import sys
import os
from pathlib import Path

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agent72.infrastructure.database.session import SessionLocal
from agent72.infrastructure.repositories.sqlalchemy_organization_repository import SQLAlchemyOrganizationRepository
from agent72.infrastructure.repositories.sqlalchemy_evidence_repository import SQLAlchemyEvidenceRepository
from agent72.infrastructure.repositories.sqlalchemy_analysis_repository import SQLAlchemyAnalysisRepository
from agent72.infrastructure.repositories.sqlalchemy_trajectory_repository import SQLAlchemyTrajectoryRepository
from agent72.application.services.trajectory_service import TrajectoryAnalysisService
from agent72.application.services.analysis_service import CurrentPositionAnalysisService
from agent72.application.dtos.trajectory_dto import TrajectoryAnalysisRequestDTO
from agent72.application.dtos.analysis_dto import CurrentPositionAnalysisRequestDTO
from agent72.domain.models.organization import Institution, OrganizationalUnit, UnitType, EntityStatus
from agent72.domain.models.evidence import (
    MetricDefinition,
    MetricDomain,
    MetricDirection,
    InstitutionalEvidence,
    SourceType,
    QualityTier,
)


def seed_demo_data():
    print("=== Seeding Phase 5 Institutional Trajectory Demo Data ===")

    session = SessionLocal()
    try:
        org_repo = SQLAlchemyOrganizationRepository(session)
        ev_repo = SQLAlchemyEvidenceRepository(session)
        analysis_repo = SQLAlchemyAnalysisRepository(session)
        traj_repo = SQLAlchemyTrajectoryRepository(session)

        # 1. Institution
        inst = org_repo.get_institution_by_code("DEMO-APEX")
        if not inst:
            inst = org_repo.create_institution(
                Institution(
                    code="DEMO-APEX",
                    name="Apex Institute of Technology (Demo)",
                    status=EntityStatus.ACTIVE,
                )
            )
            print(f"Created Demo Institution: {inst.name} ({inst.id})")
        else:
            print(f"Found Existing Demo Institution: {inst.name} ({inst.id})")

        # 2. Organizational Unit
        existing_units = org_repo.list_units_by_institution(inst.id)
        unit = next((u for u in existing_units if u.code == "DEMO-SOE"), None)
        if not unit:
            unit = org_repo.create_unit(
                OrganizationalUnit(
                    institution_id=inst.id,
                    code="DEMO-SOE",
                    name="School of Engineering (Demo)",
                    unit_type=UnitType.SCHOOL,
                    status=EntityStatus.ACTIVE,
                )
            )
            print(f"Created Demo Unit: {unit.name} ({unit.id})")
        else:
            print(f"Found Existing Demo Unit: {unit.name} ({unit.id})")

        # 3. Metric Definitions across the 6 Main Domains
        metric_catalogs = [
            # Academic Performance
            MetricDefinition(
                metric_key="academic.graduation.rate",
                name="Graduation Rate",
                domain=MetricDomain.ACADEMIC_PERFORMANCE,
                direction=MetricDirection.HIGHER_IS_BETTER,
                default_unit="percent",
                description="Undergraduate cohort 4-year completion percentage.",
            ),
            MetricDefinition(
                metric_key="academic.dropout.rate",
                name="Student Dropout Rate",
                domain=MetricDomain.ACADEMIC_PERFORMANCE,
                direction=MetricDirection.LOWER_IS_BETTER,
                default_unit="percent",
                description="Annual undergraduate withdrawal rate.",
            ),
            # Admissions & Market
            MetricDefinition(
                metric_key="admissions.yield",
                name="Admissions Yield",
                domain=MetricDomain.ADMISSIONS_MARKET,
                direction=MetricDirection.HIGHER_IS_BETTER,
                default_unit="percent",
                description="Percentage of admitted students who matriculate.",
            ),
            MetricDefinition(
                metric_key="admissions.selectivity",
                name="Admissions Acceptance Rate",
                domain=MetricDomain.ADMISSIONS_MARKET,
                direction=MetricDirection.LOWER_IS_BETTER,
                default_unit="percent",
                description="Percentage of total applicants admitted.",
            ),
            # Placement & Employer Demand
            MetricDefinition(
                metric_key="placement.rate",
                name="Placement Rate",
                domain=MetricDomain.PLACEMENT_EMPLOYER_DEMAND,
                direction=MetricDirection.HIGHER_IS_BETTER,
                default_unit="percent",
                description="Percentage of graduates placed in employment or higher education within 6 months.",
            ),
            MetricDefinition(
                metric_key="placement.median.salary",
                name="Median Graduate Starting Salary",
                domain=MetricDomain.PLACEMENT_EMPLOYER_DEMAND,
                direction=MetricDirection.HIGHER_IS_BETTER,
                default_unit="usd_thousands",
                description="Median starting annual salary in thousands USD.",
            ),
            # Research
            MetricDefinition(
                metric_key="research.publications",
                name="Peer-Reviewed Publications",
                domain=MetricDomain.RESEARCH_PRODUCTIVITY,
                direction=MetricDirection.HIGHER_IS_BETTER,
                default_unit="count",
                description="Annual faculty peer-reviewed publications.",
            ),
            MetricDefinition(
                metric_key="research.grant.funding",
                name="Sponsored Research Funding",
                domain=MetricDomain.RESEARCH_PRODUCTIVITY,
                direction=MetricDirection.HIGHER_IS_BETTER,
                default_unit="usd_thousands",
                description="Total competitive sponsored research grants in thousands USD.",
            ),
            # Faculty Capability
            MetricDefinition(
                metric_key="faculty.phd.ratio",
                name="Faculty Terminal Degree (PhD) Ratio",
                domain=MetricDomain.FACULTY_CAPABILITY,
                direction=MetricDirection.HIGHER_IS_BETTER,
                default_unit="percent",
                description="Proportion of full-time faculty holding doctoral degrees.",
            ),
            MetricDefinition(
                metric_key="faculty.student.ratio",
                name="Student-Faculty Ratio",
                domain=MetricDomain.FACULTY_CAPABILITY,
                direction=MetricDirection.LOWER_IS_BETTER,
                default_unit="ratio",
                description="Number of students per full-time faculty member.",
            ),
            # Infrastructure
            MetricDefinition(
                metric_key="infra.lab.utilization",
                name="Engineering Lab Utilization Rate",
                domain=MetricDomain.INFRASTRUCTURE,
                direction=MetricDirection.HIGHER_IS_BETTER,
                default_unit="percent",
                description="Weekly average utilization rate of research and teaching laboratories.",
            ),
            MetricDefinition(
                metric_key="infra.smart.classrooms",
                name="Smart Classroom Penetration",
                domain=MetricDomain.INFRASTRUCTURE,
                direction=MetricDirection.HIGHER_IS_BETTER,
                default_unit="percent",
                description="Percentage of instructional spaces equipped with active digital learning infrastructure.",
            ),
        ]

        for m in metric_catalogs:
            if not ev_repo.get_metric_definition(m.metric_key):
                ev_repo.create_metric_definition(m)

        print(f"Registered/Verified {len(metric_catalogs)} Metric Definitions across 6 Domains.")

        # 4. Realistic 3-Year Evidence Series (2022-2023, 2023-2024, 2024-2025)
        # Provenance:
        # Agent-generated metrics: SourceType.AGENT (clearly marked simulated agent source)
        # Administrative/institutional records: SourceType.MANUAL
        evidence_series = [
            # 1. Graduation Rate (IMPROVING: 74.0 -> 76.5 -> 79.2)
            ("academic.graduation.rate", MetricDomain.ACADEMIC_PERFORMANCE, "percent", "2022-2023", 74.0, SourceType.AGENT, "Agent 71 (Simulation)", QualityTier.VERIFIED, 0.95),
            ("academic.graduation.rate", MetricDomain.ACADEMIC_PERFORMANCE, "percent", "2023-2024", 76.5, SourceType.AGENT, "Agent 71 (Simulation)", QualityTier.VERIFIED, 0.95),
            ("academic.graduation.rate", MetricDomain.ACADEMIC_PERFORMANCE, "percent", "2024-2025", 79.2, SourceType.AGENT, "Agent 71 (Simulation)", QualityTier.VERIFIED, 0.95),

            # 2. Dropout Rate (IMPROVING / LOWER_IS_BETTER: 9.8 -> 8.4 -> 7.1)
            ("academic.dropout.rate", MetricDomain.ACADEMIC_PERFORMANCE, "percent", "2022-2023", 9.8, SourceType.AGENT, "Agent 71 (Simulation)", QualityTier.VERIFIED, 0.92),
            ("academic.dropout.rate", MetricDomain.ACADEMIC_PERFORMANCE, "percent", "2023-2024", 8.4, SourceType.AGENT, "Agent 71 (Simulation)", QualityTier.VERIFIED, 0.92),
            ("academic.dropout.rate", MetricDomain.ACADEMIC_PERFORMANCE, "percent", "2024-2025", 7.1, SourceType.AGENT, "Agent 71 (Simulation)", QualityTier.VERIFIED, 0.92),

            # 3. Admissions Yield (DECLINING: 44.0 -> 39.5 -> 34.2)
            ("admissions.yield", MetricDomain.ADMISSIONS_MARKET, "percent", "2022-2023", 44.0, SourceType.AGENT, "Agent 71 (Simulation)", QualityTier.VERIFIED, 0.90),
            ("admissions.yield", MetricDomain.ADMISSIONS_MARKET, "percent", "2023-2024", 39.5, SourceType.AGENT, "Agent 71 (Simulation)", QualityTier.VERIFIED, 0.90),
            ("admissions.yield", MetricDomain.ADMISSIONS_MARKET, "percent", "2024-2025", 34.2, SourceType.AGENT, "Agent 71 (Simulation)", QualityTier.VERIFIED, 0.90),

            # 4. Admissions Selectivity (IMPROVING / LOWER_IS_BETTER: 32.0 -> 29.5 -> 26.0)
            ("admissions.selectivity", MetricDomain.ADMISSIONS_MARKET, "percent", "2022-2023", 32.0, SourceType.AGENT, "Agent 71 (Simulation)", QualityTier.VERIFIED, 0.91),
            ("admissions.selectivity", MetricDomain.ADMISSIONS_MARKET, "percent", "2023-2024", 29.5, SourceType.AGENT, "Agent 71 (Simulation)", QualityTier.VERIFIED, 0.91),
            ("admissions.selectivity", MetricDomain.ADMISSIONS_MARKET, "percent", "2024-2025", 26.0, SourceType.AGENT, "Agent 71 (Simulation)", QualityTier.VERIFIED, 0.91),

            # 5. Placement Rate (IMPROVING & ACCELERATING: 71.5 -> 76.0 (+4.5) -> 82.4 (+6.4))
            ("placement.rate", MetricDomain.PLACEMENT_EMPLOYER_DEMAND, "percent", "2022-2023", 71.5, SourceType.AGENT, "Agent 71 (Simulation)", QualityTier.VERIFIED, 0.96),
            ("placement.rate", MetricDomain.PLACEMENT_EMPLOYER_DEMAND, "percent", "2023-2024", 76.0, SourceType.AGENT, "Agent 71 (Simulation)", QualityTier.VERIFIED, 0.96),
            ("placement.rate", MetricDomain.PLACEMENT_EMPLOYER_DEMAND, "percent", "2024-2025", 82.4, SourceType.AGENT, "Agent 71 (Simulation)", QualityTier.VERIFIED, 0.96),

            # 6. Median Salary (IMPROVING: 62.0 -> 66.5 -> 72.0)
            ("placement.median.salary", MetricDomain.PLACEMENT_EMPLOYER_DEMAND, "usd_thousands", "2022-2023", 62.0, SourceType.AGENT, "Agent 71 (Simulation)", QualityTier.ESTIMATED, 0.88),
            ("placement.median.salary", MetricDomain.PLACEMENT_EMPLOYER_DEMAND, "usd_thousands", "2023-2024", 66.5, SourceType.AGENT, "Agent 71 (Simulation)", QualityTier.ESTIMATED, 0.88),
            ("placement.median.salary", MetricDomain.PLACEMENT_EMPLOYER_DEMAND, "usd_thousands", "2024-2025", 72.0, SourceType.AGENT, "Agent 71 (Simulation)", QualityTier.VERIFIED, 0.94),

            # 7. Research Publications (IMPROVING: 145 -> 180 -> 230)
            ("research.publications", MetricDomain.RESEARCH_PRODUCTIVITY, "count", "2022-2023", 145.0, SourceType.AGENT, "Agent 20 (Simulation)", QualityTier.VERIFIED, 0.94),
            ("research.publications", MetricDomain.RESEARCH_PRODUCTIVITY, "count", "2023-2024", 180.0, SourceType.AGENT, "Agent 20 (Simulation)", QualityTier.VERIFIED, 0.94),
            ("research.publications", MetricDomain.RESEARCH_PRODUCTIVITY, "count", "2024-2025", 230.0, SourceType.AGENT, "Agent 20 (Simulation)", QualityTier.VERIFIED, 0.94),

            # 8. Research Grant Funding (IMPROVING: 2400 -> 3100 -> 4200)
            ("research.grant.funding", MetricDomain.RESEARCH_PRODUCTIVITY, "usd_thousands", "2022-2023", 2400.0, SourceType.MANUAL, "Office of Sponsored Research (Demo)", QualityTier.VERIFIED, 0.95),
            ("research.grant.funding", MetricDomain.RESEARCH_PRODUCTIVITY, "usd_thousands", "2023-2024", 3100.0, SourceType.MANUAL, "Office of Sponsored Research (Demo)", QualityTier.VERIFIED, 0.95),
            ("research.grant.funding", MetricDomain.RESEARCH_PRODUCTIVITY, "usd_thousands", "2024-2025", 4200.0, SourceType.MANUAL, "Office of Sponsored Research (Demo)", QualityTier.VERIFIED, 0.95),

            # 9. Faculty PhD Ratio (IMPROVING / DECELERATING: 68.0 -> 72.0 (+4.0) -> 73.5 (+1.5))
            ("faculty.phd.ratio", MetricDomain.FACULTY_CAPABILITY, "percent", "2022-2023", 68.0, SourceType.MANUAL, "Faculty Affairs Office (Demo)", QualityTier.VERIFIED, 0.92),
            ("faculty.phd.ratio", MetricDomain.FACULTY_CAPABILITY, "percent", "2023-2024", 72.0, SourceType.MANUAL, "Faculty Affairs Office (Demo)", QualityTier.VERIFIED, 0.92),
            ("faculty.phd.ratio", MetricDomain.FACULTY_CAPABILITY, "percent", "2024-2025", 73.5, SourceType.MANUAL, "Faculty Affairs Office (Demo)", QualityTier.VERIFIED, 0.92),

            # 10. Student-Faculty Ratio (IMPROVING / LOWER_IS_BETTER: 17.5 -> 16.8 -> 16.0)
            ("faculty.student.ratio", MetricDomain.FACULTY_CAPABILITY, "ratio", "2022-2023", 17.5, SourceType.MANUAL, "Registrar (Demo)", QualityTier.VERIFIED, 0.93),
            ("faculty.student.ratio", MetricDomain.FACULTY_CAPABILITY, "ratio", "2023-2024", 16.8, SourceType.MANUAL, "Registrar (Demo)", QualityTier.VERIFIED, 0.93),
            ("faculty.student.ratio", MetricDomain.FACULTY_CAPABILITY, "ratio", "2024-2025", 16.0, SourceType.MANUAL, "Registrar (Demo)", QualityTier.VERIFIED, 0.93),

            # 11. Lab Utilization (STABLE: 82.0 -> 82.5 -> 82.2 - within ±2% threshold)
            ("infra.lab.utilization", MetricDomain.INFRASTRUCTURE, "percent", "2022-2023", 82.0, SourceType.MANUAL, "Campus Facilities (Demo)", QualityTier.ESTIMATED, 0.85),
            ("infra.lab.utilization", MetricDomain.INFRASTRUCTURE, "percent", "2023-2024", 82.5, SourceType.MANUAL, "Campus Facilities (Demo)", QualityTier.ESTIMATED, 0.85),
            ("infra.lab.utilization", MetricDomain.INFRASTRUCTURE, "percent", "2024-2025", 82.2, SourceType.MANUAL, "Campus Facilities (Demo)", QualityTier.ESTIMATED, 0.85),

            # 12. Smart Classrooms (IMPROVING: 40.0 -> 55.0 -> 70.0)
            ("infra.smart.classrooms", MetricDomain.INFRASTRUCTURE, "percent", "2022-2023", 40.0, SourceType.MANUAL, "Campus Facilities (Demo)", QualityTier.VERIFIED, 0.90),
            ("infra.smart.classrooms", MetricDomain.INFRASTRUCTURE, "percent", "2023-2024", 55.0, SourceType.MANUAL, "Campus Facilities (Demo)", QualityTier.VERIFIED, 0.90),
            ("infra.smart.classrooms", MetricDomain.INFRASTRUCTURE, "percent", "2024-2025", 70.0, SourceType.MANUAL, "Campus Facilities (Demo)", QualityTier.VERIFIED, 0.90),
        ]

        recorded_count = 0
        for metric_key, domain, unit_str, period, val, src_type, src_name, tier, conf in evidence_series:
            idempotency = f"demo_seed:{inst.id}:{metric_key}:{period}"
            existing = ev_repo.find_existing_evidence(inst.id, idempotency)
            if not existing:
                ev_repo.record_evidence(
                    InstitutionalEvidence(
                        institution_id=inst.id,
                        metric_key=metric_key,
                        domain=domain,
                        numeric_value=val,
                        unit=unit_str,
                        period=period,
                        source_type=src_type,
                        source_name=src_name,
                        source_reference="Phase 5 Demo Seeder",
                        quality_tier=tier,
                        confidence_score=conf,
                        idempotency_key=idempotency,
                    )
                )
                recorded_count += 1

        print(f"Ingested {recorded_count} new historical evidence observations across 3 academic periods.")

        # 5. Generate Current Position Analysis for 2024-2025 to enable Signal Synthesis
        pos_service = CurrentPositionAnalysisService(
            analysis_repository=analysis_repo,
            evidence_repository=ev_repo,
            organization_repository=org_repo,
        )
        pos_snapshot = pos_service.generate_current_position_analysis(
            CurrentPositionAnalysisRequestDTO(
                institution_id=inst.id,
                analysis_period="2024-2025",
                configured_baselines={
                    "placement.rate": 85.0,  # 82.4% vs 85.0% -> Below Target GAP
                    "admissions.yield": 40.0,  # 34.2% vs 40.0% -> Below Target GAP
                    "academic.graduation.rate": 78.0,  # 79.2% vs 78.0% -> Exceeds Target STRENGTH
                },
            )
        )
        print(f"Generated Current Position Analysis: {pos_snapshot.id}")

        # 6. Generate Trajectory Analysis for 2024-2025
        traj_service = TrajectoryAnalysisService(
            trajectory_repository=traj_repo,
            evidence_repository=ev_repo,
            organization_repository=org_repo,
            analysis_repository=analysis_repo,
        )
        traj_snapshot = traj_service.generate_trajectory_analysis(
            TrajectoryAnalysisRequestDTO(
                institution_id=inst.id,
                analysis_period="2024-2025",
                current_position_analysis_id=pos_snapshot.id,
            )
        )
        print(f"\nSuccessfully Generated Trajectory Analysis [{traj_snapshot.id}]:")
        print(f"  Confidence: {traj_snapshot.overall_confidence.level} ({traj_snapshot.overall_confidence.score*100:.0f}%)")
        print(f"  Metrics Evaluated: {len(traj_snapshot.metric_trends)}")
        print(f"  Structured Signals: {len(traj_snapshot.trajectory_signals)}")

        print("\nTrajectory Summary Highlights:")
        for m in traj_snapshot.metric_trends[:6]:
            print(f"  - {m.metric_name}: {m.earliest_value} ({m.earliest_period}) -> {m.latest_value} ({m.latest_period}) | {m.trend_status.value} | Consistency: {m.consistency.value} | Acceleration: {m.acceleration.value}")

        print("\nSample Trajectory Signals:")
        for s in traj_snapshot.trajectory_signals:
            print(f"  * [{s.status}] {s.title}: {s.interpretation}")

    finally:
        session.close()

    print("\n=== Demo Data Seeding Complete ===")


if __name__ == "__main__":
    seed_demo_data()
