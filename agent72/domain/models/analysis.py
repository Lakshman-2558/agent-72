"""Domain models for Current Institutional Position Analysis."""

from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from agent72.domain.models.evidence import (
    FreshnessStatus,
    MetricDomain,
    MetricDirection,
    QualityTier,
    SourceType,
)


class FindingCategory(str, Enum):
    STRENGTH = "STRENGTH"
    WEAKNESS = "WEAKNESS"
    GAP = "GAP"
    CONSTRAINT = "CONSTRAINT"
    STRUCTURAL_RISK = "STRUCTURAL_RISK"
    OPPORTUNITY = "OPPORTUNITY"
    DATA_GAP = "DATA_GAP"


class FindingSeverity(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


class ComparisonType(str, Enum):
    PREVIOUS_PERIOD = "PREVIOUS_PERIOD"
    PLAN_TARGET = "PLAN_TARGET"
    CONFIGURED_BASELINE = "CONFIGURED_BASELINE"
    NONE = "NONE"


class PerformanceStatus(str, Enum):
    POSITIVE_PERFORMANCE = "POSITIVE_PERFORMANCE"
    NEGATIVE_PERFORMANCE = "NEGATIVE_PERFORMANCE"
    BELOW_TARGET = "BELOW_TARGET"
    MEETS_TARGET = "MEETS_TARGET"
    EXCEEDS_TARGET = "EXCEEDS_TARGET"
    NEUTRAL = "NEUTRAL"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"


@dataclass
class PositionFinding:
    """A deterministic, evidence-backed finding explaining an institutional position signal."""
    id: Optional[str] = None
    category: FindingCategory = FindingCategory.STRENGTH
    title: str = ""
    description: str = ""
    severity: FindingSeverity = FindingSeverity.MEDIUM
    metric_key: Optional[str] = None
    observed_value: Optional[float] = None
    comparison_value: Optional[float] = None
    comparison_type: ComparisonType = ComparisonType.NONE
    evidence_ids: List[str] = field(default_factory=list)
    confidence_score: float = 1.0
    quality_tier: QualityTier = QualityTier.VERIFIED
    freshness_status: FreshnessStatus = FreshnessStatus.FRESH
    rationale: str = ""


@dataclass
class MetricAssessment:
    """Individual metric observation comparison, directionality, and variance assessment."""
    metric_key: str
    metric_name: str
    domain: MetricDomain
    unit: str
    direction: MetricDirection = MetricDirection.HIGHER_IS_BETTER
    latest_value: Optional[float] = None
    latest_period: Optional[str] = None
    previous_value: Optional[float] = None
    previous_period: Optional[str] = None
    change_direction: Optional[str] = None  # "↑", "↓", "→", or None
    absolute_change: Optional[float] = None
    percent_change: Optional[float] = None
    target_value: Optional[float] = None
    target_variance: Optional[float] = None
    performance_status: PerformanceStatus = PerformanceStatus.NEUTRAL
    comparison_status: str = "comparison_unavailable"
    freshness_status: FreshnessStatus = FreshnessStatus.FRESH
    quality_tier: QualityTier = QualityTier.VERIFIED
    confidence_score: float = 1.0
    evidence_id: Optional[str] = None


@dataclass
class EvidenceReference:
    """Explicit provenance trace connecting findings back to source evidence records."""
    evidence_id: str
    metric_key: str
    period: str
    as_of_date: date
    source_name: str
    source_type: SourceType
    confidence_score: float
    quality_tier: QualityTier
    freshness_status: FreshnessStatus


@dataclass
class ConfidenceAssessment:
    """Transparent confidence calculation explaining all scoring factors."""
    score: float = 1.0
    level: str = "HIGH"
    factors: Dict[str, Any] = field(default_factory=dict)
    explanation: str = ""


@dataclass
class CurrentPositionAnalysis:
    """Master institutional current position analysis snapshot (immutable/versioned)."""
    id: Optional[str] = None
    institution_id: str = ""
    organizational_unit_id: Optional[str] = None
    analysis_period: str = ""
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    key_metrics: List[MetricAssessment] = field(default_factory=list)
    strengths: List[PositionFinding] = field(default_factory=list)
    weaknesses: List[PositionFinding] = field(default_factory=list)
    gaps: List[PositionFinding] = field(default_factory=list)
    constraints: List[PositionFinding] = field(default_factory=list)
    structural_risks: List[PositionFinding] = field(default_factory=list)
    opportunities: List[PositionFinding] = field(default_factory=list)
    data_gaps: List[PositionFinding] = field(default_factory=list)

    evidence_references: List[EvidenceReference] = field(default_factory=list)
    assumptions: List[str] = field(default_factory=list)
    overall_confidence: ConfidenceAssessment = field(default_factory=ConfidenceAssessment)
    status: str = "FINALIZED"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
