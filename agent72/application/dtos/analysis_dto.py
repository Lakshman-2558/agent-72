"""Pydantic DTOs for Current Institutional Position Analysis."""

from datetime import date, datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field
from agent72.domain.models.analysis import (
    ComparisonType,
    FindingCategory,
    FindingSeverity,
    PerformanceStatus,
)
from agent72.domain.models.evidence import (
    FreshnessStatus,
    MetricDirection,
    MetricDomain,
    QualityTier,
    SourceType,
)


class CurrentPositionAnalysisRequestDTO(BaseModel):
    """Request payload to establish an institutional current position analysis."""
    institution_id: str = Field(..., min_length=1, description="Target institution UUID")
    organizational_unit_id: Optional[str] = Field(None, description="Optional unit/department UUID")
    analysis_period: str = Field(..., min_length=4, max_length=50, description="Academic period to establish baseline for, e.g. '2024-2025'")
    configured_baselines: Optional[Dict[str, float]] = Field(default=None, description="Optional manual baselines per metric key")
    include_plan_targets: bool = Field(default=True, description="Whether to compare against active strategic plan objectives")


class PositionFindingDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[str] = None
    category: FindingCategory
    title: str
    description: str
    severity: FindingSeverity
    metric_key: Optional[str] = None
    observed_value: Optional[float] = None
    comparison_value: Optional[float] = None
    comparison_type: ComparisonType = ComparisonType.NONE
    evidence_ids: List[str] = Field(default_factory=list)
    confidence_score: float
    quality_tier: QualityTier
    freshness_status: FreshnessStatus
    rationale: str


class MetricAssessmentDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    metric_key: str
    metric_name: str
    domain: MetricDomain
    unit: str
    direction: MetricDirection
    latest_value: Optional[float] = None
    latest_period: Optional[str] = None
    previous_value: Optional[float] = None
    previous_period: Optional[str] = None
    change_direction: Optional[str] = None
    absolute_change: Optional[float] = None
    percent_change: Optional[float] = None
    target_value: Optional[float] = None
    target_variance: Optional[float] = None
    performance_status: PerformanceStatus
    comparison_status: str
    freshness_status: FreshnessStatus
    quality_tier: QualityTier
    confidence_score: float
    evidence_id: Optional[str] = None


class EvidenceReferenceDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    evidence_id: str
    metric_key: str
    period: str
    as_of_date: date
    source_name: str
    source_type: SourceType
    confidence_score: float
    quality_tier: QualityTier
    freshness_status: FreshnessStatus


class ConfidenceAssessmentDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    score: float
    level: str
    factors: Dict[str, Any] = Field(default_factory=dict)
    explanation: str


class CurrentPositionAnalysisResponseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    institution_id: str
    organizational_unit_id: Optional[str] = None
    analysis_period: str
    generated_at: datetime
    overall_confidence: ConfidenceAssessmentDTO
    key_metrics: List[MetricAssessmentDTO] = Field(default_factory=list)
    strengths: List[PositionFindingDTO] = Field(default_factory=list)
    weaknesses: List[PositionFindingDTO] = Field(default_factory=list)
    gaps: List[PositionFindingDTO] = Field(default_factory=list)
    constraints: List[PositionFindingDTO] = Field(default_factory=list)
    structural_risks: List[PositionFindingDTO] = Field(default_factory=list)
    opportunities: List[PositionFindingDTO] = Field(default_factory=list)
    data_gaps: List[PositionFindingDTO] = Field(default_factory=list)
    evidence_references: List[EvidenceReferenceDTO] = Field(default_factory=list)
    assumptions: List[str] = Field(default_factory=list)
    status: str


class AnalysisListResponseDTO(BaseModel):
    total: int
    items: List[CurrentPositionAnalysisResponseDTO]
