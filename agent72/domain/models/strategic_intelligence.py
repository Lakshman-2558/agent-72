"""
Domain models for Strategic Intelligence: Risks, Constraints & External Environment (Phase 6).

Transforms:
Evidence -> Current Position -> Trajectory -> Strategic Intelligence

Answers:
"What important strategic issues, risks, constraints, opportunities and external forces should leadership consider?"

Strict architecture boundary:
Produces diagnostic strategic intelligence without final prescriptive strategic recommendations, options, or scenario plans.
"""

from datetime import date, datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from agent72.domain.models.analysis import ConfidenceAssessment
from agent72.domain.models.evidence import (
    FreshnessStatus,
    MetricDomain,
    QualityTier,
    SourceType,
)


class IssueCategory(str, Enum):
    """Classification of strategic issues."""
    RISK = "RISK"
    CONSTRAINT = "CONSTRAINT"
    OPPORTUNITY = "OPPORTUNITY"
    EXTERNAL_FACTOR = "EXTERNAL_FACTOR"
    STRATEGIC_ISSUE = "STRATEGIC_ISSUE"


class RiskSeverity(str, Enum):
    """Categorical severity assessment."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class LikelihoodLevel(str, Enum):
    """Likelihood of risk occurrence or trend continuation."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class ImpactLevel(str, Enum):
    """Potential organizational impact."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class UncertaintyLevel(str, Enum):
    """Evaluation of data ambiguity, missing information, or conflicting signals."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class ExternalFactorCategory(str, Enum):
    """Environmental, market, and regulatory categories."""
    REGULATORY = "REGULATORY"
    MARKET_SHIFT = "MARKET_SHIFT"
    EMPLOYER_DEMAND = "EMPLOYER_DEMAND"
    COMPETITOR_MOVEMENT = "COMPETITOR_MOVEMENT"
    DEMOGRAPHIC = "DEMOGRAPHIC"


class EvidenceReference(BaseModel):
    """Traceable canonical evidence link."""
    evidence_id: str
    metric_key: str
    period: str
    as_of_date: Optional[date] = None
    source_name: str
    source_type: SourceType = SourceType.MANUAL
    confidence_score: float = 0.0
    quality_tier: QualityTier = QualityTier.PROVISIONAL
    freshness_status: FreshnessStatus = FreshnessStatus.FRESH


class StrategicIssue(BaseModel):
    """
    Synthesized strategic issue connecting Current Position (Phase 4) and Trajectory (Phase 5).
    """
    id: str
    category: IssueCategory = IssueCategory.STRATEGIC_ISSUE
    title: str
    description: str
    severity: RiskSeverity = RiskSeverity.MEDIUM
    impact: ImpactLevel = ImpactLevel.MEDIUM
    likelihood: LikelihoodLevel = LikelihoodLevel.MEDIUM
    affected_domains: List[MetricDomain] = Field(default_factory=list)
    related_metrics: List[str] = Field(default_factory=list)
    current_position_links: List[str] = Field(default_factory=list)
    trajectory_links: List[str] = Field(default_factory=list)
    evidence_ids: List[str] = Field(default_factory=list)
    confidence: float = 0.8
    assumptions: List[str] = Field(default_factory=list)
    rationale: str


class RiskSignal(BaseModel):
    """
    Multi-metric structural risk supported by corroborating evidence.
    Explicitly distinguishes correlation from causation.
    """
    id: str
    title: str
    description: str
    severity: RiskSeverity = RiskSeverity.MEDIUM
    impact: ImpactLevel = ImpactLevel.MEDIUM
    likelihood: LikelihoodLevel = LikelihoodLevel.MEDIUM
    risk_score: float = 0.5
    scoring_factors: Dict[str, Any] = Field(default_factory=dict)
    affected_domains: List[MetricDomain] = Field(default_factory=list)
    related_metrics: List[str] = Field(default_factory=list)
    supporting_indicators: List[str] = Field(default_factory=list)
    correlation_vs_causation_note: str = ""
    evidence_ids: List[str] = Field(default_factory=list)
    confidence: float = 0.8
    uncertainty_level: UncertaintyLevel = UncertaintyLevel.MEDIUM
    rationale: str


class ConstraintSignal(BaseModel):
    """
    Persistent institutional constraint backed by evidence.
    Never inferred from missing data.
    """
    id: str
    title: str
    description: str
    constraint_type: str
    severity: RiskSeverity = RiskSeverity.MEDIUM
    affected_domains: List[MetricDomain] = Field(default_factory=list)
    related_metrics: List[str] = Field(default_factory=list)
    persistence: str = "MULTI_PERIOD"
    evidence_ids: List[str] = Field(default_factory=list)
    confidence: float = 0.8
    limitations_note: Optional[str] = None
    rationale: str


class OpportunitySignal(BaseModel):
    """
    Evidence-supported opportunity identified diagnostically.
    Does NOT contain action recommendations (reserved for Phase 7).
    """
    id: str
    title: str
    description: str
    opportunity_type: str
    potential_impact: ImpactLevel = ImpactLevel.MEDIUM
    urgency: LikelihoodLevel = LikelihoodLevel.MEDIUM
    affected_domains: List[MetricDomain] = Field(default_factory=list)
    related_metrics: List[str] = Field(default_factory=list)
    evidence_ids: List[str] = Field(default_factory=list)
    confidence: float = 0.8
    interpretation: str
    rationale: str


class ExternalFactor(BaseModel):
    """
    External environmental, market, regulatory, or competitor force.
    """
    id: str
    factor_name: str
    category: ExternalFactorCategory
    direction_impact: str
    description: str
    affected_domains: List[MetricDomain] = Field(default_factory=list)
    evidence_ids: List[str] = Field(default_factory=list)
    confidence: float = 0.8
    freshness: FreshnessStatus = FreshnessStatus.FRESH
    rationale: str


class StrategicPrioritySignal(BaseModel):
    """
    Preliminary priority signal based on impact, urgency, evidence depth, and exposure.
    Explicitly NOT final strategic plan prioritization.
    """
    id: str
    issue_id: str
    title: str
    category: IssueCategory
    priority_level: str  # LOW, MEDIUM, HIGH, URGENT
    priority_score: float
    scoring_factors: Dict[str, Any] = Field(default_factory=dict)
    rationale: str


class StrategicIntelligenceAnalysis(BaseModel):
    """
    Persisted immutable domain snapshot of institutional strategic intelligence.
    """
    id: Optional[str] = None
    institution_id: str
    organizational_unit_id: Optional[str] = None
    analysis_period: str
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    current_position_analysis_id: Optional[str] = None
    trajectory_analysis_id: Optional[str] = None
    strategic_issues: List[StrategicIssue] = Field(default_factory=list)
    risk_signals: List[RiskSignal] = Field(default_factory=list)
    constraint_signals: List[ConstraintSignal] = Field(default_factory=list)
    opportunity_signals: List[OpportunitySignal] = Field(default_factory=list)
    external_factors: List[ExternalFactor] = Field(default_factory=list)
    strategic_priority_signals: List[StrategicPrioritySignal] = Field(default_factory=list)
    evidence_references: List[EvidenceReference] = Field(default_factory=list)
    overall_confidence: ConfidenceAssessment
    uncertainty_summary: Dict[str, Any] = Field(default_factory=dict)
    ai_synthesis_notes: Optional[str] = None
    assumptions: List[str] = Field(default_factory=list)
    status: str = "FINALIZED"
