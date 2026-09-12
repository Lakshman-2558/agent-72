"""SQLAlchemy 2.0 ORM models for Agent 72 relational storage."""

import uuid
from datetime import date, datetime, timezone
from typing import List, Optional
from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from agent72.infrastructure.database.base import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


# ==============================================================================
# 1. Institutional Context Models
# ==============================================================================

class InstitutionModel(Base):
    __tablename__ = "institutions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    institution_type: Mapped[str] = mapped_column(String(50), default="UNIVERSITY", nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="ACTIVE", nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    units: Mapped[List["OrganizationalUnitModel"]] = relationship(
        "OrganizationalUnitModel",
        back_populates="institution",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class OrganizationalUnitModel(Base):
    __tablename__ = "organizational_units"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    institution_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    code: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    unit_type: Mapped[str] = mapped_column(String(50), default="DEPARTMENT", nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="ACTIVE", nullable=False)
    parent_unit_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("organizational_units.id", ondelete="SET NULL"), nullable=True, index=True
    )

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    institution: Mapped["InstitutionModel"] = relationship("InstitutionModel", back_populates="units")

    __table_args__ = (
        Index("ix_units_institution_code", "institution_id", "code", unique=True),
    )


# ==============================================================================
# 2. Institutional Evidence & Metric Models
# ==============================================================================

class MetricDefinitionModel(Base):
    __tablename__ = "metric_definitions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    metric_key: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    domain: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    direction: Mapped[str] = mapped_column(String(50), default="HIGHER_IS_BETTER", nullable=False)
    default_unit: Mapped[str] = mapped_column(String(50), default="count", nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)


class InstitutionalEvidenceModel(Base):
    __tablename__ = "institutional_evidence"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    institution_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    unit_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)
    metric_key: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    domain: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    numeric_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    text_value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    unit: Mapped[str] = mapped_column(String(50), nullable=False)

    # Time & Freshness
    period: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # e.g., "2024-2025" or "2024-Q1"
    period_start: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    period_end: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    as_of_date: Mapped[date] = mapped_column(Date, nullable=False)
    captured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    # Provenance
    source_type: Mapped[str] = mapped_column(String(50), default="MANUAL", nullable=False)
    source_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    source_reference: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    confidence_score: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    quality_tier: Mapped[str] = mapped_column(String(50), default="VERIFIED", nullable=False)
    is_stale: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Ingestion & Idempotency Metadata
    external_record_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    idempotency_key: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    ingestion_batch_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)

    __table_args__ = (
        Index("ix_evidence_inst_period", "institution_id", "period"),
        Index("ix_evidence_metric_period", "metric_key", "period"),
        Index("ix_evidence_domain_period", "domain", "period"),
        Index("ix_evidence_source_captured", "source_name", "captured_at"),
        Index("ix_evidence_source_idempotency", "source_name", "idempotency_key"),
    )


class IngestionBatchLogModel(Base):
    __tablename__ = "ingestion_batch_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    batch_id: Mapped[str] = mapped_column(String(36), unique=True, nullable=False, index=True)
    source_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    received_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    inserted_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    duplicate_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    rejected_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)


# ==============================================================================
# 3. Strategic Planning & Execution Models
# ==============================================================================

class StrategicPlanModel(Base):
    __tablename__ = "strategic_plans"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    institution_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("institutions.id", ondelete="SET NULL"), nullable=True, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    institution_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    horizon_start_year: Mapped[int] = mapped_column(Integer, nullable=False)
    horizon_end_year: Mapped[int] = mapped_column(Integer, nullable=False)
    vision_statement: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    mission_statement: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    existing_commitments: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    review_period: Mapped[str] = mapped_column(String(50), default="ANNUAL", nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="DRAFT", index=True)

    # Phase 8 Execution Fields
    source_analysis_ids: Mapped[Optional[list]] = mapped_column(JSON, default=list, nullable=True)
    selected_option_ids: Mapped[Optional[list]] = mapped_column(JSON, default=list, nullable=True)
    assumptions: Mapped[Optional[list]] = mapped_column(JSON, default=list, nullable=True)
    decision_support_disclaimer: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    engine_version: Mapped[Optional[str]] = mapped_column(String(50), default="1.0.0", nullable=True)
    previous_version_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    # Relationships
    objectives: Mapped[List["PlanObjectiveModel"]] = relationship(
        "PlanObjectiveModel",
        back_populates="plan",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    strategic_options: Mapped[List["StrategicOptionModel"]] = relationship(
        "StrategicOptionModel",
        back_populates="plan",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    scenarios: Mapped[List["PlanScenarioModel"]] = relationship(
        "PlanScenarioModel",
        back_populates="plan",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    execution_reviews: Mapped[List["ExecutionReviewModel"]] = relationship(
        "ExecutionReviewModel",
        back_populates="plan",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    __table_args__ = (
        Index("ix_plans_institution_horizon", "institution_name", "horizon_start_year", "horizon_end_year"),
    )


class PlanObjectiveModel(Base):
    __tablename__ = "plan_objectives"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    plan_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("strategic_plans.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    target_metric: Mapped[str] = mapped_column(String(255), nullable=False)
    metric_key: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    target_period: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    baseline_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    target_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    weight: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    owner: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Phase 8 Execution Fields
    source_option_ids: Mapped[Optional[list]] = mapped_column(JSON, default=list, nullable=True)
    strategic_issue_ids: Mapped[Optional[list]] = mapped_column(JSON, default=list, nullable=True)
    related_metrics: Mapped[Optional[list]] = mapped_column(JSON, default=list, nullable=True)
    status: Mapped[Optional[str]] = mapped_column(String(50), default="PROPOSED", nullable=True)
    priority: Mapped[Optional[str]] = mapped_column(String(50), default="MEDIUM", nullable=True)
    owner_unit_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    assumptions: Mapped[Optional[list]] = mapped_column(JSON, default=list, nullable=True)
    confidence: Mapped[Optional[float]] = mapped_column(Float, default=1.0, nullable=True)

    plan: Mapped["StrategicPlanModel"] = relationship("StrategicPlanModel", back_populates="objectives")
    initiatives: Mapped[List["PlanInitiativeModel"]] = relationship(
        "PlanInitiativeModel",
        back_populates="objective",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    targets: Mapped[List["StrategicTargetModel"]] = relationship(
        "StrategicTargetModel",
        back_populates="objective",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class StrategicTargetModel(Base):
    __tablename__ = "strategic_targets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    objective_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("plan_objectives.id", ondelete="CASCADE"), nullable=False, index=True
    )
    metric_key: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    metric_definition_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    baseline_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    baseline_period: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    target_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    target_period: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    direction: Mapped[str] = mapped_column(String(50), default="HIGHER_IS_BETTER", nullable=False)
    unit: Mapped[str] = mapped_column(String(50), default="count", nullable=False)
    measurement_frequency: Mapped[str] = mapped_column(String(50), default="ANNUAL", nullable=False)
    evidence_ids: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    assumptions: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="PROPOSED_TARGET", nullable=False)
    gap: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    gap_unit_label: Mapped[str] = mapped_column(String(50), default="", nullable=False)
    target_provenance: Mapped[str] = mapped_column(String(100), default="DERIVED_FROM_EVIDENCE", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    objective: Mapped["PlanObjectiveModel"] = relationship("PlanObjectiveModel", back_populates="targets")


class PlanInitiativeModel(Base):
    __tablename__ = "plan_initiatives"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    objective_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("plan_objectives.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    owner: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    budget: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="NOT_STARTED", nullable=False)
    start_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Phase 8 Execution Fields
    owner_unit_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    supporting_units: Mapped[Optional[list]] = mapped_column(JSON, default=list, nullable=True)
    source_option_ids: Mapped[Optional[list]] = mapped_column(JSON, default=list, nullable=True)
    dependencies: Mapped[Optional[list]] = mapped_column(JSON, default=list, nullable=True)
    resource_requirement: Mapped[Optional[str]] = mapped_column(String(50), default="UNKNOWN", nullable=True)
    implementation_risk: Mapped[Optional[str]] = mapped_column(String(50), default="MEDIUM", nullable=True)
    start_period: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    end_period: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    success_criteria: Mapped[Optional[list]] = mapped_column(JSON, default=list, nullable=True)
    evidence_ids: Mapped[Optional[list]] = mapped_column(JSON, default=list, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    objective: Mapped["PlanObjectiveModel"] = relationship("PlanObjectiveModel", back_populates="initiatives")
    milestones: Mapped[List["InitiativeMilestoneModel"]] = relationship(
        "InitiativeMilestoneModel",
        back_populates="initiative",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class InitiativeMilestoneModel(Base):
    __tablename__ = "initiative_milestones"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    initiative_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("plan_initiatives.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    target_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="PENDING", nullable=False)
    completion_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Phase 8 Execution Fields
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    due_period: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    completion_percentage: Mapped[Optional[float]] = mapped_column(Float, default=0.0, nullable=True)
    evidence_ids: Mapped[Optional[list]] = mapped_column(JSON, default=list, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    initiative: Mapped["PlanInitiativeModel"] = relationship("PlanInitiativeModel", back_populates="milestones")


class StrategicOptionModel(Base):
    __tablename__ = "strategic_options"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    plan_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("strategic_plans.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    rationale: Mapped[str] = mapped_column(Text, nullable=False)
    resource_intensity: Mapped[str] = mapped_column(String(50), default="MEDIUM", nullable=False)
    estimated_cost: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    risk_level: Mapped[str] = mapped_column(String(50), default="MEDIUM", nullable=False)

    plan: Mapped["StrategicPlanModel"] = relationship("StrategicPlanModel", back_populates="strategic_options")


class PlanScenarioModel(Base):
    __tablename__ = "plan_scenarios"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    plan_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("strategic_plans.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    assumptions: Mapped[str] = mapped_column(Text, nullable=False)
    projected_outcome: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    plan: Mapped["StrategicPlanModel"] = relationship("StrategicPlanModel", back_populates="scenarios")


class ExecutionReviewModel(Base):
    __tablename__ = "execution_reviews"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    plan_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("strategic_plans.id", ondelete="CASCADE"), nullable=False, index=True
    )
    period: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    review_date: Mapped[date] = mapped_column(Date, nullable=False)
    progress_summary: Mapped[str] = mapped_column(Text, nullable=False)
    variance_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    recommendations: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Phase 8 Execution Fields
    overall_status: Mapped[Optional[str]] = mapped_column(String(50), default="ON_TRACK", nullable=True)
    objective_statuses: Mapped[Optional[dict]] = mapped_column(JSON, default=dict, nullable=True)
    initiative_statuses: Mapped[Optional[dict]] = mapped_column(JSON, default=dict, nullable=True)
    milestone_statuses: Mapped[Optional[dict]] = mapped_column(JSON, default=dict, nullable=True)
    metric_variances: Mapped[Optional[list]] = mapped_column(JSON, default=list, nullable=True)
    diagnostic_signals: Mapped[Optional[list]] = mapped_column(JSON, default=list, nullable=True)
    risks: Mapped[Optional[list]] = mapped_column(JSON, default=list, nullable=True)
    corrective_actions: Mapped[Optional[list]] = mapped_column(JSON, default=list, nullable=True)
    assumptions: Mapped[Optional[list]] = mapped_column(JSON, default=list, nullable=True)
    evidence_ids: Mapped[Optional[list]] = mapped_column(JSON, default=list, nullable=True)
    confidence: Mapped[Optional[float]] = mapped_column(Float, default=1.0, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    plan: Mapped["StrategicPlanModel"] = relationship("StrategicPlanModel", back_populates="execution_reviews")



# ==============================================================================
# 4. Current Position Analysis Models
# ==============================================================================

class CurrentPositionAnalysisModel(Base):
    __tablename__ = "institutional_analyses"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    institution_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    unit_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("organizational_units.id", ondelete="SET NULL"), nullable=True, index=True
    )
    analysis_period: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    overall_confidence_score: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    confidence_level: Mapped[str] = mapped_column(String(20), default="HIGH", nullable=False)
    confidence_factors: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

    # Structured assessments & findings
    key_metrics: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    strengths: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    weaknesses: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    gaps: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    constraints: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    structural_risks: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    opportunities: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    data_gaps: Mapped[list] = mapped_column(JSON, default=list, nullable=False)

    evidence_references: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    assumptions: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="FINALIZED", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    __table_args__ = (
        Index("ix_analyses_inst_period", "institution_id", "analysis_period"),
        Index("ix_analyses_unit_period", "unit_id", "analysis_period"),
    )


# ==============================================================================
# 5. Institutional Trajectory Analysis Models
# ==============================================================================

class TrajectoryAnalysisModel(Base):
    __tablename__ = "institutional_trajectory_analyses"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    institution_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    unit_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("organizational_units.id", ondelete="SET NULL"), nullable=True, index=True
    )
    analysis_period: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    overall_confidence_score: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    confidence_level: Mapped[str] = mapped_column(String(20), default="HIGH", nullable=False)
    confidence_factors: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

    # Structured assessments & findings
    metric_trends: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    trajectory_signals: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    data_limitations: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    evidence_references: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    assumptions: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="FINALIZED", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    __table_args__ = (
        Index("ix_traj_analyses_inst_period", "institution_id", "analysis_period"),
        Index("ix_traj_analyses_unit_period", "unit_id", "analysis_period"),
    )


# ==============================================================================
# 6. Strategic Intelligence Analysis Models (Phase 6)
# ==============================================================================

class StrategicIntelligenceAnalysisModel(Base):
    __tablename__ = "institutional_strategic_intelligence_analyses"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    institution_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    unit_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("organizational_units.id", ondelete="SET NULL"), nullable=True, index=True
    )
    analysis_period: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    current_position_analysis_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    trajectory_analysis_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)

    overall_confidence_score: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    confidence_level: Mapped[str] = mapped_column(String(20), default="HIGH", nullable=False)
    confidence_factors: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

    # Structured assessments & signals
    strategic_issues: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    risk_signals: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    constraint_signals: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    opportunity_signals: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    external_factors: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    strategic_priority_signals: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    evidence_references: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    uncertainty_summary: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    ai_synthesis_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    assumptions: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="FINALIZED", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    __table_args__ = (
        Index("ix_strat_intel_inst_period", "institution_id", "analysis_period"),
        Index("ix_strat_intel_unit_period", "unit_id", "analysis_period"),
    )


# ==============================================================================
# 7. Strategic Options, Scenarios & Prioritization Models (Phase 7)
# ==============================================================================

class StrategicOptionsAnalysisModel(Base):
    __tablename__ = "institutional_strategic_options_analyses"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    institution_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    unit_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("organizational_units.id", ondelete="SET NULL"), nullable=True, index=True
    )
    analysis_period: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    strategic_intelligence_analysis_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)

    # Structured strategic choices, scenarios & evaluations
    options: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    scenarios: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    evaluations: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    prioritized_option_ids: Mapped[list] = mapped_column(JSON, default=list, nullable=False)

    assumptions: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    uncertainty: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    data_limitations: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    decision_support_disclaimer: Mapped[str] = mapped_column(
        Text,
        default=(
            "Strategic options and priority signals are decision-support outputs. "
            "Final strategic decisions remain with institutional leadership/governing bodies."
        ),
        nullable=False,
    )
    engine_version: Mapped[str] = mapped_column(String(50), default="1.0.0", nullable=False)
    ai_synthesis_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    status: Mapped[str] = mapped_column(String(50), default="FINALIZED", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    __table_args__ = (
        Index("ix_strat_options_inst_period", "institution_id", "analysis_period"),
        Index("ix_strat_options_unit_period", "unit_id", "analysis_period"),
    )


