"""
Historical 5-Year Data Ingestion & Analysis Engine for Agent 72.

Reads canonical time-series evidence from:
- data/vignan_historical_performance_5_years.csv
- data/departmental_performance_5_years.csv

Populates 5 full academic years of historical observations (2020-2021 through 2024-2025)
into institutional_evidence and triggers the full Agent 72 analysis pipeline:
1. Current Position Analysis (Phase 4)
2. 5-Year Trajectory Analysis (Phase 5)
3. Strategic Intelligence Synthesis (Phase 6)
4. Strategic Options Generation & Scenario Evaluation (Phase 7)
"""

import csv
import sys
import os
from datetime import date, datetime
from pathlib import Path

# Ensure project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from agent72.infrastructure.database.session import SessionLocal
from agent72.infrastructure.database.models import (
    InstitutionModel,
    OrganizationalUnitModel,
    MetricDefinitionModel,
    InstitutionalEvidenceModel,
)
from agent72.domain.models.evidence import (
    MetricDefinition,
    MetricDomain,
    MetricDirection,
    InstitutionalEvidence,
    SourceType,
    QualityTier,
)
from agent72.infrastructure.repositories.sqlalchemy_organization_repository import SQLAlchemyOrganizationRepository
from agent72.infrastructure.repositories.sqlalchemy_evidence_repository import SQLAlchemyEvidenceRepository
from agent72.infrastructure.repositories.sqlalchemy_analysis_repository import SQLAlchemyAnalysisRepository
from agent72.infrastructure.repositories.sqlalchemy_trajectory_repository import SQLAlchemyTrajectoryRepository
from agent72.infrastructure.repositories.sqlalchemy_strategic_intelligence_repository import SQLAlchemyStrategicIntelligenceRepository
from agent72.infrastructure.repositories.sqlalchemy_strategic_options_repository import SQLAlchemyStrategicOptionsRepository

from agent72.application.services.analysis_service import CurrentPositionAnalysisService
from agent72.application.services.trajectory_service import TrajectoryAnalysisService
from agent72.application.services.strategic_intelligence_service import StrategicIntelligenceService
from agent72.application.services.strategic_options_service import StrategicOptionsService

from agent72.application.dtos.analysis_dto import CurrentPositionAnalysisRequestDTO
from agent72.application.dtos.trajectory_dto import TrajectoryAnalysisRequestDTO
from agent72.application.dtos.strategic_intelligence_dto import StrategicIntelligenceRequestDTO
from agent72.application.dtos.strategic_options_dto import StrategicOptionsRequestDTO


def ingest_5_year_data():
    csv_path = PROJECT_ROOT / "data" / "vignan_historical_performance_5_years.csv"
    if not csv_path.exists():
        print(f"Error: {csv_path} not found.")
        return

    print("================================================================")
    print(" Agent 72: Ingesting 5-Year Historical Performance Data")
    print(f" File: {csv_path.name}")
    print("================================================================")

    session = SessionLocal()
    try:
        org_repo = SQLAlchemyOrganizationRepository(session)
        ev_repo = SQLAlchemyEvidenceRepository(session)
        analysis_repo = SQLAlchemyAnalysisRepository(session)
        traj_repo = SQLAlchemyTrajectoryRepository(session)
        intel_repo = SQLAlchemyStrategicIntelligenceRepository(session)
        options_repo = SQLAlchemyStrategicOptionsRepository(session)

        # 1. Target Institution (Prefer Vignan's University)
        institutions = session.query(InstitutionModel).all()
        target_insts = [
            i for i in institutions
            if any(k in i.code.upper() for k in ["VIGNAN", "APEX"]) or "Vignan" in i.name
        ]
        if not target_insts:
            target_insts = institutions[:1]

        if not target_insts:
            print("No institutions found in database.")
            return

        for inst in target_insts:
            print(f"\nTargeting Institution: {inst.name} [ID: {inst.id}, Code: {inst.code}]")

            # 2. Read and Ingest CSV Records
            rows_ingested = 0
            rows_skipped = 0

            with open(csv_path, mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    period = row["academic_period"].strip()
                    metric_key = row["metric_key"].strip()
                    metric_name = row["metric_name"].strip()
                    domain_str = row["domain"].strip().upper()
                    numeric_val = float(row["numeric_value"].strip())
                    unit = row["unit"].strip()
                    direction_str = row["direction"].strip().upper()
                    src_name = row["source_name"].strip()
                    src_type_str = row["source_type"].strip().upper()
                    quality_str = row["quality_tier"].strip().upper()
                    conf_score = float(row["confidence_score"].strip())
                    as_of = date.fromisoformat(row["as_of_date"].strip())
                    notes = row.get("notes", "").strip()

                    # Domain enum lookup
                    domain = MetricDomain[domain_str] if domain_str in MetricDomain.__members__ else MetricDomain.ACADEMIC_PERFORMANCE
                    direction = MetricDirection[direction_str] if direction_str in MetricDirection.__members__ else MetricDirection.HIGHER_IS_BETTER
                    src_type = SourceType[src_type_str] if src_type_str in SourceType.__members__ else SourceType.MANUAL
                    quality_tier = QualityTier[quality_str] if quality_str in QualityTier.__members__ else QualityTier.VERIFIED

                    # Ensure MetricDefinition exists
                    m_def = ev_repo.get_metric_definition(metric_key)
                    if not m_def:
                        ev_repo.create_metric_definition(
                            MetricDefinition(
                                metric_key=metric_key,
                                name=metric_name,
                                domain=domain,
                                direction=direction,
                                default_unit=unit,
                                description=f"Canonical indicator: {metric_name}",
                            )
                        )

                    # Check for existing observation in the same period
                    existing = (
                        session.query(InstitutionalEvidenceModel)
                        .filter_by(
                            institution_id=inst.id,
                            metric_key=metric_key,
                            period=period,
                        )
                        .first()
                    )

                    idempotency = f"5yr-{inst.id}-{metric_key}-{period}"

                    if existing:
                        # Update with canonical 5-year observation values
                        existing.numeric_value = numeric_val
                        existing.unit = unit
                        existing.as_of_date = as_of
                        existing.confidence_score = conf_score
                        existing.quality_tier = quality_tier.value
                        existing.source_name = src_name
                        existing.source_type = src_type.value
                        existing.source_reference = notes or "5-Year Historical Ingestion"
                        existing.is_stale = False
                        rows_skipped += 1
                    else:
                        evidence_obj = InstitutionalEvidence(
                            institution_id=inst.id,
                            metric_key=metric_key,
                            domain=domain,
                            numeric_value=numeric_val,
                            unit=unit,
                            period=period,
                            source_type=src_type,
                            source_name=src_name,
                            source_reference=notes or "5-Year Historical Ingestion",
                            quality_tier=quality_tier,
                            confidence_score=conf_score,
                            as_of_date=as_of,
                            idempotency_key=idempotency,
                        )
                        ev_repo.record_evidence(evidence_obj)
                        rows_ingested += 1

            session.commit()
            print(f"  -> Ingestion Complete: {rows_ingested} inserted, {rows_skipped} updated/aligned.")

            # 3. Trigger Full Deterministic Analysis Pipeline
            print("\n  -> Generating Updated Current Position Analysis (2024-2025)...")
            pos_service = CurrentPositionAnalysisService(
                analysis_repository=analysis_repo,
                evidence_repository=ev_repo,
                organization_repository=org_repo,
            )
            pos_analysis = pos_service.generate_current_position_analysis(
                CurrentPositionAnalysisRequestDTO(
                    institution_id=inst.id,
                    analysis_period="2024-2025",
                    configured_baselines={
                        "placement.rate": 80.0,
                        "admissions.yield": 38.0,
                        "academic.graduation.rate": 78.0,
                        "faculty.phd.ratio": 75.0,
                        "research.publications": 200.0,
                    },
                )
            )
            print(f"     Status: OK | Findings: {len(pos_analysis.strengths)} strengths, {len(pos_analysis.weaknesses)} weaknesses, {len(pos_analysis.gaps)} gaps")

            print("\n  -> Generating 5-Year Trajectory Analysis (2024-2025)...")
            traj_service = TrajectoryAnalysisService(
                trajectory_repository=traj_repo,
                evidence_repository=ev_repo,
                organization_repository=org_repo,
                analysis_repository=analysis_repo,
            )
            traj_analysis = traj_service.generate_trajectory_analysis(
                TrajectoryAnalysisRequestDTO(
                    institution_id=inst.id,
                    analysis_period="2024-2025",
                    current_position_analysis_id=pos_analysis.id,
                )
            )
            print(f"     Status: OK | Trends: {len(traj_analysis.metric_trends)} metrics | Signals: {len(traj_analysis.trajectory_signals)}")
            print(f"     Confidence: {traj_analysis.overall_confidence.level} ({traj_analysis.overall_confidence.score*100:.0f}%)")

            # 4. Generate Strategic Intelligence & Options
            print("\n  -> Generating Strategic Intelligence Synthesis (2024-2025)...")
            intel_service = StrategicIntelligenceService(
                strategic_intelligence_repository=intel_repo,
                analysis_repository=analysis_repo,
                trajectory_repository=traj_repo,
                evidence_repository=ev_repo,
                organization_repository=org_repo,
            )
            intel_analysis = intel_service.generate_strategic_intelligence_analysis(
                StrategicIntelligenceRequestDTO(
                    institution_id=inst.id,
                    analysis_period="2024-2025",
                    current_position_analysis_id=pos_analysis.id,
                    trajectory_analysis_id=traj_analysis.id,
                )
            )
            print(f"     Status: OK | Issues: {len(intel_analysis.strategic_issues)} | Risks: {len(intel_analysis.risk_signals)} | Constraints: {len(intel_analysis.constraint_signals)}")

            print("\n  -> Generating Strategic Options & Scenario Evaluations (2024-2025)...")
            options_service = StrategicOptionsService(
                strategic_options_repository=options_repo,
                strategic_intelligence_repository=intel_repo,
            )
            options_analysis = options_service.generate_strategic_options_analysis(
                StrategicOptionsRequestDTO(
                    institution_id=inst.id,
                    analysis_period="2024-2025",
                    strategic_intelligence_analysis_id=intel_analysis.id,
                )
            )
            print(f"     Status: OK | Options: {len(options_analysis.options)} actionable options generated & ranked.")

            print("\n--- 5-Year Trajectory Metric Trends Summary ---")
            for m in traj_analysis.metric_trends:
                net = (m.absolute_change if m.absolute_change is not None else 0.0)
                arrow = "+" if net > 0 else ""
                print(
                    f"  * {m.metric_name:32} : {m.earliest_value} ({m.earliest_period}) -> {m.latest_value} ({m.latest_period}) "
                    f"[{arrow}{net:.1f} {m.unit}] | Status: {m.trend_status.value:20} | Consistency: {m.consistency.value}"
                )

            print("\n--- Key Synthesized Trajectory Signals ---")
            for s in traj_analysis.trajectory_signals[:5]:
                print(f"  * [{s.severity}] {s.title}: {s.description}")

    finally:
        session.close()

    print("\n================================================================")
    print(" 5-Year Historical Ingestion & Multi-Stage Analysis Complete!")
    print("================================================================")


if __name__ == "__main__":
    ingest_5_year_data()
