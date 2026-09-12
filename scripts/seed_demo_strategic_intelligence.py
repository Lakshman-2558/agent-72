"""
Demo Script for Phase 6 — Strategic Intelligence for Agent 72.

End-to-End Pipeline Execution:
Evidence (Academic, Admissions, Placement, Research, Faculty, Infrastructure, Finance, External, Competitor)
  -> Phase 4: Current Institutional Position Analysis
  -> Phase 5: Institutional Trajectory Analysis
  -> Phase 6: Strategic Intelligence Analysis

Produces clear, explainable diagnostic strategic intelligence for institutional leadership.
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
from agent72.infrastructure.ai import get_ai_provider
from agent72.application.services.analysis_service import CurrentPositionAnalysisService
from agent72.application.services.trajectory_service import TrajectoryAnalysisService
from agent72.application.services.strategic_intelligence_service import StrategicIntelligenceService
from agent72.application.dtos.analysis_dto import CurrentPositionAnalysisRequestDTO
from agent72.application.dtos.trajectory_dto import TrajectoryAnalysisRequestDTO
from agent72.application.dtos.strategic_intelligence_dto import StrategicIntelligenceRequestDTO
from agent72.domain.models.organization import Institution, OrganizationalUnit, UnitType, EntityStatus
from agent72.domain.models.evidence import (
    MetricDefinition,
    MetricDomain,
    MetricDirection,
    InstitutionalEvidence,
    SourceType,
    QualityTier,
)


def run_phase6_demo():
    print("=" * 80)
    print("   AGENT 72: STRATEGIC PLANNING AGENT - PHASE 6 STRATEGIC INTELLIGENCE DEMO")
    print("=" * 80)

    session = SessionLocal()
    try:
        org_repo = SQLAlchemyOrganizationRepository(session)
        ev_repo = SQLAlchemyEvidenceRepository(session)
        analysis_repo = SQLAlchemyAnalysisRepository(session)
        traj_repo = SQLAlchemyTrajectoryRepository(session)
        strat_repo = SQLAlchemyStrategicIntelligenceRepository(session)
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
            print(f"[+] Created Demo Institution: {inst.name} ({inst.id})")
        else:
            print(f"[*] Found Existing Demo Institution: {inst.name} ({inst.id})")

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
            print(f"[+] Created Demo Unit: {unit.name} ({unit.id})")
        else:
            print(f"[*] Found Existing Demo Unit: {unit.name} ({unit.id})")

        # -------------------------------------------------------------
        # 2. Register Metric Definitions Across All Required Domains
        # -------------------------------------------------------------
        metric_definitions = [
            # Academic Performance
            MetricDefinition(
                metric_key="academic.graduation.rate",
                name="Graduation Rate",
                domain=MetricDomain.ACADEMIC_PERFORMANCE,
                direction=MetricDirection.HIGHER_IS_BETTER,
                default_unit="percent",
                description="Undergraduate 4-year completion percentage.",
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
                description="Percentage of admitted students matriculating.",
            ),
            # Placement & Employer Demand
            MetricDefinition(
                metric_key="placement.rate",
                name="Placement Rate",
                domain=MetricDomain.PLACEMENT_EMPLOYER_DEMAND,
                direction=MetricDirection.HIGHER_IS_BETTER,
                default_unit="percent",
                description="Percentage of graduates placed in employment within 6 months.",
            ),
            MetricDefinition(
                metric_key="placement.employer.demand.index",
                name="Regional Tech Employer Demand Indicator",
                domain=MetricDomain.PLACEMENT_EMPLOYER_DEMAND,
                direction=MetricDirection.HIGHER_IS_BETTER,
                default_unit="index",
                description="Composite index of regional engineering and tech entry-level hiring demand.",
            ),
            # Research Productivity
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
            # Finance & Resources
            MetricDefinition(
                metric_key="finance.operating.margin",
                name="Institutional Operating Margin",
                domain=MetricDomain.FINANCE_RESOURCES,
                direction=MetricDirection.HIGHER_IS_BETTER,
                default_unit="percent",
                description="Net operating surplus percentage after direct academic costs.",
            ),
            # External Regulatory
            MetricDefinition(
                metric_key="external.regulatory.compliance.status",
                name="National STEM Laboratory Safety Accreditation Mandate",
                domain=MetricDomain.EXTERNAL_REGULATORY,
                direction=MetricDirection.NEUTRAL,
                default_unit="text",
                description="Regulatory safety audit standard issued by National Higher Education Board.",
            ),
            # Peer / Competitor
            MetricDefinition(
                metric_key="peer.competitor.program.expansion",
                name="Regional Competitor AI and Robotics Programs",
                domain=MetricDomain.PEER_COMPETITOR,
                direction=MetricDirection.NEUTRAL,
                default_unit="text",
                description="Monitored expansion of competing institutions in adjacent market territories.",
            ),
        ]

        for m_def in metric_definitions:
            existing = ev_repo.get_metric_definition(m_def.metric_key)
            if not existing:
                ev_repo.create_metric_definition(m_def)
                print(f"[+] Registered Metric Definition: {m_def.metric_key} [{m_def.domain.value}]")

        # -------------------------------------------------------------
        # 3. Seed Realistic Multi-Period Canonical Evidence
        # -------------------------------------------------------------
        now = datetime.now(timezone.utc)
        evidence_batch = [
            # 1. Placement: below target (85%) and declining across 3 periods (88 -> 82 -> 76)
            InstitutionalEvidence(
                institution_id=inst.id,
                unit_id=unit.id,
                metric_key="placement.rate",
                period="2022-2023",
                numeric_value=88.0,
                unit="percent",
                source_name="Institutional Career Services",
                source_type=SourceType.MANUAL,
                quality_tier=QualityTier.VERIFIED,
                confidence_score=0.90,
                domain=MetricDomain.PLACEMENT_EMPLOYER_DEMAND,
                as_of_date=(now - timedelta(days=730)).date(),
            ),
            InstitutionalEvidence(
                institution_id=inst.id,
                unit_id=unit.id,
                metric_key="placement.rate",
                period="2023-2024",
                numeric_value=82.0,
                unit="percent",
                source_name="Institutional Career Services",
                source_type=SourceType.MANUAL,
                quality_tier=QualityTier.VERIFIED,
                confidence_score=0.90,
                domain=MetricDomain.PLACEMENT_EMPLOYER_DEMAND,
                as_of_date=(now - timedelta(days=365)).date(),
            ),
            InstitutionalEvidence(
                institution_id=inst.id,
                unit_id=unit.id,
                metric_key="placement.rate",
                period="2024-2025",
                numeric_value=76.0,
                unit="percent",
                source_name="Institutional Career Services",
                source_type=SourceType.MANUAL,
                quality_tier=QualityTier.VERIFIED,
                confidence_score=0.92,
                domain=MetricDomain.PLACEMENT_EMPLOYER_DEMAND,
                as_of_date=(now - timedelta(days=30)).date(),
            ),
            # External Employer Demand: Weakening employer demand
            InstitutionalEvidence(
                institution_id=inst.id,
                unit_id=unit.id,
                metric_key="placement.employer.demand.index",
                period="2024-2025",
                numeric_value=48.5,
                text_value="Weakening hiring demand and recruitment freezes reported across regional tech employers.",
                unit="index",
                source_name="State Workforce Development Board",
                source_type=SourceType.EXTERNAL,
                quality_tier=QualityTier.ESTIMATED,
                confidence_score=0.88,
                domain=MetricDomain.PLACEMENT_EMPLOYER_DEMAND,
                as_of_date=(now - timedelta(days=45)).date(),
            ),
            # 2. Research Publications: Strongly improving (120 -> 155 -> 195)
            InstitutionalEvidence(
                institution_id=inst.id,
                unit_id=unit.id,
                metric_key="research.publications",
                period="2022-2023",
                numeric_value=120.0,
                unit="count",
                source_name="Office of Research Administration",
                source_type=SourceType.MANUAL,
                quality_tier=QualityTier.VERIFIED,
                confidence_score=0.95,
                domain=MetricDomain.RESEARCH_PRODUCTIVITY,
                as_of_date=(now - timedelta(days=730)).date(),
            ),
            InstitutionalEvidence(
                institution_id=inst.id,
                unit_id=unit.id,
                metric_key="research.publications",
                period="2023-2024",
                numeric_value=155.0,
                unit="count",
                source_name="Office of Research Administration",
                source_type=SourceType.MANUAL,
                quality_tier=QualityTier.VERIFIED,
                confidence_score=0.95,
                domain=MetricDomain.RESEARCH_PRODUCTIVITY,
                as_of_date=(now - timedelta(days=365)).date(),
            ),
            InstitutionalEvidence(
                institution_id=inst.id,
                unit_id=unit.id,
                metric_key="research.publications",
                period="2024-2025",
                numeric_value=195.0,
                unit="count",
                source_name="Office of Research Administration",
                source_type=SourceType.MANUAL,
                quality_tier=QualityTier.VERIFIED,
                confidence_score=0.95,
                domain=MetricDomain.RESEARCH_PRODUCTIVITY,
                as_of_date=(now - timedelta(days=20)).date(),
            ),
            # Sponsored Research Grants ($k): (3200 -> 4100 -> 5400)
            InstitutionalEvidence(
                institution_id=inst.id,
                unit_id=unit.id,
                metric_key="research.grant.funding",
                period="2024-2025",
                numeric_value=5400.0,
                unit="usd_thousands",
                source_name="Sponsored Projects Office",
                source_type=SourceType.MANUAL,
                quality_tier=QualityTier.VERIFIED,
                confidence_score=0.95,
                domain=MetricDomain.RESEARCH_PRODUCTIVITY,
                as_of_date=(now - timedelta(days=20)).date(),
            ),
            # 3. Infrastructure Lab Utilization: approaching capacity (72% -> 81% -> 89.5%, threshold=85%)
            InstitutionalEvidence(
                institution_id=inst.id,
                unit_id=unit.id,
                metric_key="infra.lab.utilization",
                period="2022-2023",
                numeric_value=72.0,
                unit="percent",
                source_name="Campus Facilities & Space Management",
                source_type=SourceType.MANUAL,
                quality_tier=QualityTier.VERIFIED,
                confidence_score=0.92,
                domain=MetricDomain.INFRASTRUCTURE,
                as_of_date=(now - timedelta(days=730)).date(),
            ),
            InstitutionalEvidence(
                institution_id=inst.id,
                unit_id=unit.id,
                metric_key="infra.lab.utilization",
                period="2023-2024",
                numeric_value=81.0,
                unit="percent",
                source_name="Campus Facilities & Space Management",
                source_type=SourceType.MANUAL,
                quality_tier=QualityTier.VERIFIED,
                confidence_score=0.92,
                domain=MetricDomain.INFRASTRUCTURE,
                as_of_date=(now - timedelta(days=365)).date(),
            ),
            InstitutionalEvidence(
                institution_id=inst.id,
                unit_id=unit.id,
                metric_key="infra.lab.utilization",
                period="2024-2025",
                numeric_value=89.5,
                unit="percent",
                source_name="Campus Facilities & Space Management",
                source_type=SourceType.MANUAL,
                quality_tier=QualityTier.VERIFIED,
                confidence_score=0.94,
                domain=MetricDomain.INFRASTRUCTURE,
                as_of_date=(now - timedelta(days=15)).date(),
            ),
            # 4. Admissions Yield: (42% -> 38% -> 34%)
            InstitutionalEvidence(
                institution_id=inst.id,
                unit_id=unit.id,
                metric_key="admissions.yield",
                period="2022-2023",
                numeric_value=42.0,
                unit="percent",
                source_name="Office of Enrollment Management",
                source_type=SourceType.MANUAL,
                quality_tier=QualityTier.VERIFIED,
                confidence_score=0.90,
                domain=MetricDomain.ADMISSIONS_MARKET,
                as_of_date=(now - timedelta(days=730)).date(),
            ),
            InstitutionalEvidence(
                institution_id=inst.id,
                unit_id=unit.id,
                metric_key="admissions.yield",
                period="2023-2024",
                numeric_value=38.0,
                unit="percent",
                source_name="Office of Enrollment Management",
                source_type=SourceType.MANUAL,
                quality_tier=QualityTier.VERIFIED,
                confidence_score=0.90,
                domain=MetricDomain.ADMISSIONS_MARKET,
                as_of_date=(now - timedelta(days=365)).date(),
            ),
            InstitutionalEvidence(
                institution_id=inst.id,
                unit_id=unit.id,
                metric_key="admissions.yield",
                period="2024-2025",
                numeric_value=34.0,
                unit="percent",
                source_name="Office of Enrollment Management",
                source_type=SourceType.MANUAL,
                quality_tier=QualityTier.VERIFIED,
                confidence_score=0.90,
                domain=MetricDomain.ADMISSIONS_MARKET,
                as_of_date=(now - timedelta(days=40)).date(),
            ),
            # Academic Dropout Rate: (5.2% -> 6.1% -> 7.8%)
            InstitutionalEvidence(
                institution_id=inst.id,
                unit_id=unit.id,
                metric_key="academic.dropout.rate",
                period="2022-2023",
                numeric_value=5.2,
                unit="percent",
                source_name="Registrar Student Records",
                source_type=SourceType.MANUAL,
                quality_tier=QualityTier.VERIFIED,
                confidence_score=0.92,
                domain=MetricDomain.ACADEMIC_PERFORMANCE,
                as_of_date=(now - timedelta(days=730)).date(),
            ),
            InstitutionalEvidence(
                institution_id=inst.id,
                unit_id=unit.id,
                metric_key="academic.dropout.rate",
                period="2023-2024",
                numeric_value=6.1,
                unit="percent",
                source_name="Registrar Student Records",
                source_type=SourceType.MANUAL,
                quality_tier=QualityTier.VERIFIED,
                confidence_score=0.92,
                domain=MetricDomain.ACADEMIC_PERFORMANCE,
                as_of_date=(now - timedelta(days=365)).date(),
            ),
            InstitutionalEvidence(
                institution_id=inst.id,
                unit_id=unit.id,
                metric_key="academic.dropout.rate",
                period="2024-2025",
                numeric_value=7.8,
                unit="percent",
                source_name="Registrar Student Records",
                source_type=SourceType.MANUAL,
                quality_tier=QualityTier.VERIFIED,
                confidence_score=0.92,
                domain=MetricDomain.ACADEMIC_PERFORMANCE,
                as_of_date=(now - timedelta(days=35)).date(),
            ),
            # 5. Faculty PhD Ratio: (66.0%, below 70% threshold)
            InstitutionalEvidence(
                institution_id=inst.id,
                unit_id=unit.id,
                metric_key="faculty.phd.ratio",
                period="2024-2025",
                numeric_value=66.0,
                unit="percent",
                source_name="Faculty Affairs Office",
                source_type=SourceType.MANUAL,
                quality_tier=QualityTier.VERIFIED,
                confidence_score=0.91,
                domain=MetricDomain.FACULTY_CAPABILITY,
                as_of_date=(now - timedelta(days=50)).date(),
            ),
            # 6. Finance: Operating Margin (4.2%)
            InstitutionalEvidence(
                institution_id=inst.id,
                unit_id=unit.id,
                metric_key="finance.operating.margin",
                period="2024-2025",
                numeric_value=4.2,
                unit="percent",
                source_name="University Financial Comptroller",
                source_type=SourceType.MANUAL,
                quality_tier=QualityTier.VERIFIED,
                confidence_score=0.95,
                domain=MetricDomain.FINANCE_RESOURCES,
                as_of_date=(now - timedelta(days=60)).date(),
            ),
            # 7. External Regulatory (Stale observation - 450 days old)
            InstitutionalEvidence(
                institution_id=inst.id,
                unit_id=unit.id,
                metric_key="external.regulatory.compliance.status",
                period="2023-2024",
                numeric_value=None,
                text_value="Mandated updates to bioengineering lab ventilation and digital audit logs under consideration by federal regulators.",
                unit="text",
                source_name="Higher Education Regulatory Gazette",
                source_type=SourceType.EXTERNAL,
                quality_tier=QualityTier.ESTIMATED,
                confidence_score=0.75,
                domain=MetricDomain.EXTERNAL_REGULATORY,
                as_of_date=(now - timedelta(days=450)).date(),
                is_stale=True,
            ),
            # 8. Peer Competitor Movement
            InstitutionalEvidence(
                institution_id=inst.id,
                unit_id=unit.id,
                metric_key="peer.competitor.program.expansion",
                period="2024-2025",
                numeric_value=None,
                text_value="Two regional competitor universities launched subsidized engineering master's tracks with corporate co-op partnerships.",
                unit="text",
                source_name="Regional Consortium Market Intelligence",
                source_type=SourceType.EXTERNAL,
                quality_tier=QualityTier.ESTIMATED,
                confidence_score=0.82,
                domain=MetricDomain.PEER_COMPETITOR,
                as_of_date=(now - timedelta(days=60)).date(),
            ),
        ]

        print(f"\n[*] Seeding {len(evidence_batch)} multi-period evidence records across all required domains...")
        for ev in evidence_batch:
            created = ev_repo.record_evidence(ev)
            tag = " [STALE]" if ev.is_stale else ""
            print(f"    - {ev.metric_key} ({ev.period}): {ev.numeric_value or ev.text_value}{tag}")

        session.commit()
        print("\n[+] Evidence persistence complete.")

        # -------------------------------------------------------------
        # 4. Pipeline Execution: Phase 4 -> Phase 5 -> Phase 6
        # -------------------------------------------------------------
        period = "2024-2025"
        print(f"\n{'='*30} PIPELINE EXECUTION ({period}) {'='*30}")

        # Step 4A: Phase 4 Current Position Analysis
        print("\n--> [1/3] Executing Phase 4: Current Institutional Position Analysis...")
        pos_service = CurrentPositionAnalysisService(
            analysis_repository=analysis_repo,
            evidence_repository=ev_repo,
            organization_repository=org_repo,
        )
        pos_res = pos_service.generate_current_position_analysis(
            CurrentPositionAnalysisRequestDTO(
                institution_id=inst.id,
                organizational_unit_id=unit.id,
                analysis_period=period,
                configured_baselines={
                    "placement.rate": 85.0,
                    "academic.dropout.rate": 5.0,
                    "admissions.yield": 40.0,
                    "faculty.phd.ratio": 70.0,
                },
            )
        )
        print(f"    [+] Current Position Finalized: ID={pos_res.id}")
        print(f"        Strengths: {len(pos_res.strengths)} | Weaknesses: {len(pos_res.weaknesses)} | Gaps: {len(pos_res.gaps)}")

        # Step 4B: Phase 5 Trajectory Analysis
        print("\n--> [2/3] Executing Phase 5: Institutional Trajectory Analysis...")
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
                analysis_period=period,
                current_position_analysis_id=pos_res.id,
            )
        )
        print(f"    [+] Trajectory Analysis Finalized: ID={traj_res.id}")
        print(f"        Metrics Tracked: {len(traj_res.metric_trends)} | Status: {traj_res.status}")

        # Step 4C: Phase 6 Strategic Intelligence Analysis
        print("\n--> [3/3] Executing Phase 6: Strategic Intelligence Synthesis...")
        strat_service = StrategicIntelligenceService(
            strategic_intelligence_repository=strat_repo,
            analysis_repository=analysis_repo,
            trajectory_repository=traj_repo,
            evidence_repository=ev_repo,
            organization_repository=org_repo,
            ai_provider=ai_provider,
        )
        strat_res = strat_service.generate_strategic_intelligence_analysis(
            StrategicIntelligenceRequestDTO(
                institution_id=inst.id,
                organizational_unit_id=unit.id,
                analysis_period=period,
                current_position_analysis_id=pos_res.id,
                trajectory_analysis_id=traj_res.id,
                include_ai_synthesis=True,
            )
        )
        print(f"    [+] Strategic Intelligence Finalized: ID={strat_res.id}")

        # -------------------------------------------------------------
        # 5. Formatted Executive Findings for Leadership
        # -------------------------------------------------------------
        print("\n" + "=" * 80)
        print("               EXECUTIVE STRATEGIC INTELLIGENCE BRIEFING")
        print("=" * 80)
        print(f"Institution:     {inst.name}")
        print(f"Scope:           {unit.name} ({unit.code})")
        print(f"Analysis Period: {strat_res.analysis_period}")
        print(f"Analysis ID:     {strat_res.id}")
        print(f"Confidence:      {strat_res.overall_confidence.level} ({strat_res.overall_confidence.score:.2f})")
        print(f"Generated At:    {strat_res.generated_at.isoformat()}")

        # Strategic Issues
        print(f"\n--- [1] STRATEGIC ISSUES ({len(strat_res.strategic_issues)}) ---")
        for idx, issue in enumerate(strat_res.strategic_issues, 1):
            print(f"  {idx}. [{issue.severity.value}] {issue.title}")
            print(f"     Details:    {issue.description}")
            print(f"     Rationale:  {issue.rationale}")

        # Structural Multi-Metric Risks
        print(f"\n--- [2] STRUCTURAL RISKS ({len(strat_res.risk_signals)}) ---")
        for idx, risk in enumerate(strat_res.risk_signals, 1):
            print(f"  {idx}. [{risk.severity.value}] {risk.title} (Score: {risk.risk_score})")
            print(f"     Description:  {risk.description}")
            print(f"     Indicators:   {', '.join(risk.supporting_indicators)}")
            print(f"     Correlation vs Causation: {risk.correlation_vs_causation_note}")

        # Evidence-Backed Constraints
        print(f"\n--- [3] OPERATIONAL & CAPACITY CONSTRAINTS ({len(strat_res.constraint_signals)}) ---")
        for idx, con in enumerate(strat_res.constraint_signals, 1):
            print(f"  {idx}. [{con.severity.value}] {con.title} (Type: {con.constraint_type})")
            print(f"     Description:  {con.description}")
            print(f"     Persistence:  {con.persistence}")

        # Evidence-Backed Opportunities
        print(f"\n--- [4] STRATEGIC OPPORTUNITIES ({len(strat_res.opportunity_signals)}) ---")
        for idx, opp in enumerate(strat_res.opportunity_signals, 1):
            print(f"  {idx}. [Impact: {opp.potential_impact.value}] {opp.title}")
            print(f"     Description:    {opp.description}")
            print(f"     Interpretation: {opp.interpretation}")

        # External Environmental Factors
        print(f"\n--- [5] EXTERNAL FORCES & MARKET SHIFTS ({len(strat_res.external_factors)}) ---")
        for idx, ext in enumerate(strat_res.external_factors, 1):
            print(f"  {idx}. [{ext.category.value}] {ext.factor_name} (Impact: {ext.direction_impact}, Freshness: {ext.freshness.value})")
            print(f"     Description: {ext.description}")

        # Preliminary Priority Signals
        print(f"\n--- [6] PRELIMINARY STRATEGIC PRIORITY SIGNALS ({len(strat_res.strategic_priority_signals)}) ---")
        for idx, prio in enumerate(strat_res.strategic_priority_signals, 1):
            print(f"  {idx}. [{prio.priority_level}] {prio.title} (Score: {prio.priority_score:.2f})")
            print(f"     Rationale: {prio.rationale}")

        # Uncertainty Summary
        print("\n--- [7] UNCERTAINTY & DATA LIMITATIONS ---")
        unc = strat_res.uncertainty_summary
        print(f"  Level:               {unc.get('overall_uncertainty_level')}")
        print(f"  Data Limitations:    {unc.get('data_limitations_count')}")
        print(f"  Stale Observations:  {unc.get('stale_evidence_count')}")
        print(f"  Conflicting Signals: {unc.get('conflicting_signals_count')}")
        print(f"  Deficiency Note:     {unc.get('information_deficiency_statement')}")

        # AI Synthesis (Strictly Grouping / Summarizing findings without altering truth)
        if strat_res.ai_synthesis_notes:
            print("\n--- [8] EXECUTIVE AI SYNTHESIS (Guardrailed Grouping) ---")
            print(f"  {strat_res.ai_synthesis_notes.strip()}")

        print("\n" + "=" * 80)
        print("   DEMO COMPLETED SUCCESSFULLY: FOUNDATION READY FOR PHASE 7 STRATEGIC OPTIONS")
        print("=" * 80)

    finally:
        session.close()


if __name__ == "__main__":
    run_phase6_demo()
