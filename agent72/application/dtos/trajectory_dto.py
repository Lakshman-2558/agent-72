"""
Data Transfer Objects for Institutional Trajectory Analysis (Phase 5).
"""

from datetime import date, datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from agent72.application.dtos.analysis_dto import ConfidenceAssessmentDTO
from agent72.domain.models.evidence import (
    FreshnessStatus,
    MetricDirection,
    MetricDomain,
    QualityTier,
    SourceType,
)
from agent72.domain.models.trajectory import (
    AccelerationStatus,
    ConsistencyRating,
    TrajectoryStatus,
)


class TrajectoryAnalysisRequestDTO(BaseModel):
    """Input payload to trigger deterministic institutional trajectory analysis."""
    institution_id: str = Field(..., description="Target institution ID")
    organizational_unit_id: Optional[str] = Field(None, description="Optional organizational unit scope")
    analysis_period: str = Field(..., description="Target academic period (e.g., '2024-2025')")
    current_position_analysis_id: Optional[str] = Field(
        None, description="Optional ID of Current Position Analysis to synthesize trajectory signals"
    )
    min_significant_change_percent: Optional[float] = Field(
        None, description="Optional override for significance change threshold in percent"
    )


class PeriodObservationDTO(BaseModel):
    period: str
    numeric_value: float
    evidence_id: Optional[str] = None
    as_of_date: Optional[date] = None
    quality_tier: QualityTier
    confidence_score: float
    is_stale: bool = False


class TrajectoryEvidenceReferenceDTO(BaseModel):
    evidence_id: str
    metric_key: str
    period: str
    as_of_date: Optional[date] = None
    source_name: str
    source_type: SourceType
    confidence_score: float
    quality_tier: QualityTier
    freshness_status: FreshnessStatus


class TrajectoryMetricDTO(BaseModel):
    metric_key: str
    metric_name: str
    domain: MetricDomain
    unit: str = ""
    direction: MetricDirection
    observations: List[PeriodObservationDTO] = Field(default_factory=list)
    latest_value: Optional[float] = None
    earliest_value: Optional[float] = None
    latest_period: Optional[str] = None
    earliest_period: Optional[str] = None
    absolute_change: Optional[float] = None
    percentage_change: Optional[float] = None
    change_direction: Optional[str] = None
    trend_status: TrajectoryStatus
    consistency: ConsistencyRating
    volatility: Optional[str] = None
    volatility_score: Optional[float] = None
    acceleration: AccelerationStatus
    confidence_score: float = 0.0
    confidence: float = 0.0
    evidence_ids: List[str] = Field(default_factory=list)


class TrajectorySignalDTO(BaseModel):
    metric_key: str
    signal_type: str
    status: str = ""
    interpretation: str = ""
    title: str
    description: str
    severity: str
    rationale: str


class TrajectoryDataLimitationDTO(BaseModel):
    metric_key: str
    limitation_type: str
    description: str
    observation_count: int
    rationale: str


class TrajectoryAnalysisResponseDTO(BaseModel):
    id: str
    institution_id: str
    organizational_unit_id: Optional[str] = None
    analysis_period: str
    generated_at: datetime
    overall_confidence: ConfidenceAssessmentDTO
    metric_trends: List[TrajectoryMetricDTO] = Field(default_factory=list)
    trajectory_signals: List[TrajectorySignalDTO] = Field(default_factory=list)
    data_limitations: List[TrajectoryDataLimitationDTO] = Field(default_factory=list)
    evidence_references: List[TrajectoryEvidenceReferenceDTO] = Field(default_factory=list)
    assumptions: List[str] = Field(default_factory=list)
    status: str = "FINALIZED"


class TrajectoryAnalysisListResponseDTO(BaseModel):
    total: int
    items: List[TrajectoryAnalysisResponseDTO] = Field(default_factory=list)
