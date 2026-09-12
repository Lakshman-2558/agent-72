"""
Domain models for Institutional Trajectory Analysis (Phase 5).

Provides deterministic representation of institutional performance trends over time,
including direction, magnitude of change, consistency, volatility, acceleration,
and synthesis with current institutional position.
"""

from datetime import datetime, date, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from agent72.domain.models.evidence import (
    MetricDirection,
    MetricDomain,
    QualityTier,
    SourceType,
    FreshnessStatus,
)
from agent72.domain.models.analysis import ConfidenceAssessment


class TrajectoryStatus(str, Enum):
    """Deterministic classification of directional trajectory."""
    IMPROVING = "IMPROVING"
    STABLE = "STABLE"
    DECLINING = "DECLINING"
    VOLATILE = "VOLATILE"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"


class ConsistencyRating(str, Enum):
    """Evaluation of sign consistency across consecutive historical periods."""
    HIGH = "HIGH"
    MODERATE = "MODERATE"
    LOW = "LOW"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"


class VolatilityRating(str, Enum):
    """Evaluation of period-to-period variability."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"


class AccelerationStatus(str, Enum):
    """Evaluation of second-order change (velocity of change across consecutive periods)."""
    ACCELERATING = "ACCELERATING"
    DECELERATING = "DECELERATING"
    CONSTANT_VELOCITY = "CONSTANT_VELOCITY"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"


class PeriodObservation(BaseModel):
    """Chronological observation of a metric for a specific period."""
    period: str
    numeric_value: float
    evidence_id: Optional[str] = None
    as_of_date: Optional[date] = None
    quality_tier: QualityTier = QualityTier.PROVISIONAL
    confidence_score: float = 0.0
    is_stale: bool = False


class TrajectoryEvidenceReference(BaseModel):
    """Traceable reference to underlying canonical evidence used in trajectory calculation."""
    evidence_id: str
    metric_key: str
    period: str
    as_of_date: Optional[date] = None
    source_name: str
    source_type: SourceType = SourceType.MANUAL
    confidence_score: float = 0.0
    quality_tier: QualityTier = QualityTier.PROVISIONAL
    freshness_status: FreshnessStatus = FreshnessStatus.FRESH


class TrajectoryMetric(BaseModel):
    """
    Trajectory assessment for an individual institutional metric.

    Contains chronological observations, overall and period changes, consistency,
    volatility, acceleration, and polarity-aware trend status.
    """
    metric_key: str
    metric_name: str
    domain: MetricDomain
    unit: str = ""
    direction: MetricDirection
    observations: List[PeriodObservation] = Field(default_factory=list)
    latest_value: Optional[float] = None
    earliest_value: Optional[float] = None
    latest_period: Optional[str] = None
    earliest_period: Optional[str] = None
    absolute_change: Optional[float] = None
    percentage_change: Optional[float] = None
    change_direction: Optional[str] = None
    trend_status: TrajectoryStatus = TrajectoryStatus.INSUFFICIENT_DATA
    consistency: ConsistencyRating = ConsistencyRating.INSUFFICIENT_DATA
    volatility: Optional[str] = None
    volatility_score: Optional[float] = None
    acceleration: AccelerationStatus = AccelerationStatus.INSUFFICIENT_DATA
    confidence_score: float = 0.0
    evidence_ids: List[str] = Field(default_factory=list)

    @property
    def confidence(self) -> float:
        return self.confidence_score


class TrajectorySignal(BaseModel):
    """
    Structured synthesis signal connecting current position findings with trajectory trends.

    Examples:
    - Current Gap + Improving Trajectory -> status: "BELOW_TARGET_IMPROVING"
      interpretation: "Performance is improving but remains below the current target."
    """
    metric_key: str
    signal_type: str
    status: str = ""
    interpretation: str = ""
    title: str
    description: str
    severity: str = "MEDIUM"
    rationale: str


class TrajectoryDataLimitation(BaseModel):
    """Isolated historical data limitation where series depth is insufficient to infer a trend."""
    metric_key: str
    limitation_type: str
    description: str
    observation_count: int = 0
    rationale: str


class TrajectoryAnalysis(BaseModel):
    """
    Persisted immutable domain snapshot of institutional trajectory analysis.

    Represents an explainable answer to 'Where are we heading?'.
    """
    id: Optional[str] = None
    institution_id: str
    organizational_unit_id: Optional[str] = None
    analysis_period: str
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metric_trends: List[TrajectoryMetric] = Field(default_factory=list)
    trajectory_signals: List[TrajectorySignal] = Field(default_factory=list)
    data_limitations: List[TrajectoryDataLimitation] = Field(default_factory=list)
    evidence_references: List[TrajectoryEvidenceReference] = Field(default_factory=list)
    assumptions: List[str] = Field(default_factory=list)
    overall_confidence: ConfidenceAssessment
    status: str = "FINALIZED"
