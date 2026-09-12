"""
Data Transfer Objects for Strategic Intelligence: Risks, Constraints & External Environment (Phase 6).
"""

from datetime import date, datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from agent72.application.dtos.analysis_dto import ConfidenceAssessmentDTO
from agent72.domain.models.evidence import (
    FreshnessStatus,
    MetricDomain,
    QualityTier,
    SourceType,
)
from agent72.domain.models.strategic_intelligence import (
    ExternalFactorCategory,
    ImpactLevel,
    IssueCategory,
    LikelihoodLevel,
    RiskSeverity,
    UncertaintyLevel,
)


class StrategicIntelligenceRequestDTO(BaseModel):
    """Input payload to trigger deterministic strategic intelligence analysis."""
    institution_id: str = Field(..., description="Target institution ID")
    organizational_unit_id: Optional[str] = Field(None, description="Optional organizational unit scope")
    analysis_period: str = Field(..., description="Target academic period (e.g., '2024-2025')")
    current_position_analysis_id: Optional[str] = Field(
        None, description="Optional ID of Current Position Analysis to use as baseline"
    )
    trajectory_analysis_id: Optional[str] = Field(
        None, description="Optional ID of Trajectory Analysis to use for directional momentum"
    )
    include_ai_synthesis: bool = Field(
        default=False,
        description="Whether to generate optional natural-language synthesis grouping (never alters deterministic scores)",
    )


class EvidenceReferenceDTO(BaseModel):
    evidence_id: str
    metric_key: str
    period: str
    as_of_date: Optional[date] = None
    source_name: str
    source_type: SourceType
    confidence_score: float
    quality_tier: QualityTier
    freshness_status: FreshnessStatus


class StrategicIssueDTO(BaseModel):
    id: str
    category: IssueCategory
    title: str
    description: str
    severity: RiskSeverity
    impact: ImpactLevel
    likelihood: LikelihoodLevel
    affected_domains: List[MetricDomain] = Field(default_factory=list)
    related_metrics: List[str] = Field(default_factory=list)
    current_position_links: List[str] = Field(default_factory=list)
    trajectory_links: List[str] = Field(default_factory=list)
    evidence_ids: List[str] = Field(default_factory=list)
    confidence: float
    assumptions: List[str] = Field(default_factory=list)
    rationale: str


class RiskSignalDTO(BaseModel):
    id: str
    title: str
    description: str
    severity: RiskSeverity
    impact: ImpactLevel
    likelihood: LikelihoodLevel
    risk_score: float
    scoring_factors: Dict[str, Any] = Field(default_factory=dict)
    affected_domains: List[MetricDomain] = Field(default_factory=list)
    related_metrics: List[str] = Field(default_factory=list)
    supporting_indicators: List[str] = Field(default_factory=list)
    correlation_vs_causation_note: str = ""
    evidence_ids: List[str] = Field(default_factory=list)
    confidence: float
    uncertainty_level: UncertaintyLevel
    rationale: str


class ConstraintSignalDTO(BaseModel):
    id: str
    title: str
    description: str
    constraint_type: str
    severity: RiskSeverity
    affected_domains: List[MetricDomain] = Field(default_factory=list)
    related_metrics: List[str] = Field(default_factory=list)
    persistence: str
    evidence_ids: List[str] = Field(default_factory=list)
    confidence: float
    limitations_note: Optional[str] = None
    rationale: str


class OpportunitySignalDTO(BaseModel):
    id: str
    title: str
    description: str
    opportunity_type: str
    potential_impact: ImpactLevel
    urgency: LikelihoodLevel
    affected_domains: List[MetricDomain] = Field(default_factory=list)
    related_metrics: List[str] = Field(default_factory=list)
    evidence_ids: List[str] = Field(default_factory=list)
    confidence: float
    interpretation: str
    rationale: str


class ExternalFactorDTO(BaseModel):
    id: str
    factor_name: str
    category: ExternalFactorCategory
    direction_impact: str
    description: str
    affected_domains: List[MetricDomain] = Field(default_factory=list)
    evidence_ids: List[str] = Field(default_factory=list)
    confidence: float
    freshness: FreshnessStatus
    rationale: str


class StrategicPrioritySignalDTO(BaseModel):
    id: str
    issue_id: str
    title: str
    category: IssueCategory
    priority_level: str
    priority_score: float
    scoring_factors: Dict[str, Any] = Field(default_factory=dict)
    rationale: str


class StrategicIntelligenceResponseDTO(BaseModel):
    id: str
    institution_id: str
    organizational_unit_id: Optional[str] = None
    analysis_period: str
    generated_at: datetime
    current_position_analysis_id: Optional[str] = None
    trajectory_analysis_id: Optional[str] = None
    overall_confidence: ConfidenceAssessmentDTO
    strategic_issues: List[StrategicIssueDTO] = Field(default_factory=list)
    risk_signals: List[RiskSignalDTO] = Field(default_factory=list)
    constraint_signals: List[ConstraintSignalDTO] = Field(default_factory=list)
    opportunity_signals: List[OpportunitySignalDTO] = Field(default_factory=list)
    external_factors: List[ExternalFactorDTO] = Field(default_factory=list)
    strategic_priority_signals: List[StrategicPrioritySignalDTO] = Field(default_factory=list)
    evidence_references: List[EvidenceReferenceDTO] = Field(default_factory=list)
    uncertainty_summary: Dict[str, Any] = Field(default_factory=dict)
    ai_synthesis_notes: Optional[str] = None
    assumptions: List[str] = Field(default_factory=list)
    status: str = "FINALIZED"


class StrategicIntelligenceListResponseDTO(BaseModel):
    total: int
    items: List[StrategicIntelligenceResponseDTO] = Field(default_factory=list)
