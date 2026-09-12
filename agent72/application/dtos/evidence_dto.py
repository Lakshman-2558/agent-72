"""Pydantic DTOs for Canonical Evidence Ingestion, Metrics Catalog, Provenance, and Freshness."""

import re
import uuid
from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator
from agent72.domain.models.evidence import (
    MetricDomain,
    MetricDirection,
    QualityTier,
    SourceType,
    FreshnessStatus,
)

ACADEMIC_PERIOD_REGEX = re.compile(r"^(\d{4}-\d{4}|\d{4}-\d{2}|\d{4}-[qQ][1-4]|\d{4})$")


class MetricDefinitionCreateDTO(BaseModel):
    metric_key: str = Field(..., min_length=2, max_length=100, description="Canonical unique metric key, e.g. 'research.publications.q1'")
    name: str = Field(..., min_length=2, max_length=255, description="Human readable name")
    domain: MetricDomain = Field(..., description="Institutional domain")
    direction: MetricDirection = Field(default=MetricDirection.HIGHER_IS_BETTER, description="Metric polarity (HIGHER_IS_BETTER, LOWER_IS_BETTER, TARGET_RANGE, NEUTRAL)")
    default_unit: str = Field(default="count", min_length=1, max_length=50)
    description: Optional[str] = None


class MetricDefinitionResponseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    metric_key: str
    name: str
    domain: MetricDomain
    direction: MetricDirection
    default_unit: str
    description: Optional[str]
    created_at: datetime


class MetricDefinitionListResponseDTO(BaseModel):
    total: int
    items: List[MetricDefinitionResponseDTO]


class EvidenceIngestionDTO(BaseModel):
    """
    Canonical Ingestion DTO for time-series evidence.
    Used by external source agents (20, 38, 49, 71, etc.) or manual ingress to supply data.
    """
    institution_id: str = Field(..., min_length=1, description="Institution UUID")
    unit_id: Optional[str] = Field(None, description="Optional department/unit UUID")
    metric_key: str = Field(..., min_length=2, max_length=100, description="Target metric key")
    domain: MetricDomain | str = Field(..., description="Indicator domain")
    numeric_value: Optional[float] = Field(None, description="Numeric measurement")
    text_value: Optional[str] = Field(None, description="Descriptive/qualitative value")
    unit: str = Field(..., min_length=1, max_length=50, description="Measurement unit e.g. 'count', 'percent', 'INR'")
    period: str = Field(..., min_length=1, max_length=50, description="Academic year (e.g. '2024-2025' or '2024-25'), quarter ('2024-Q1'), or year")
    period_start: Optional[date] = None
    period_end: Optional[date] = None
    as_of_date: date = Field(default_factory=lambda: datetime.now().date(), description="Date measurement was recorded/fresh as of")
    source_type: SourceType = Field(default=SourceType.MANUAL, description="AGENT, EXTERNAL, or MANUAL")
    source_name: str = Field(..., min_length=1, max_length=100, description="e.g. 'Agent 20', 'Agent 38', 'NIRF 2024'")
    source_reference: Optional[str] = Field(None, max_length=255, description="Run ID, batch ID, or publication DOI/URL")
    confidence_score: float = Field(default=1.0, ge=0.0, le=1.0, description="Confidence metric between 0.0 and 1.0")
    quality_tier: QualityTier = Field(default=QualityTier.VERIFIED)
    external_record_id: Optional[str] = Field(None, max_length=255, description="Optional external record ID for idempotency")

    # Optional metadata for on-the-fly metric definition registration (if enabled)
    display_name: Optional[str] = Field(None, max_length=255, description="Display name for auto-registration")
    direction: Optional[MetricDirection] = Field(None, description="Metric direction if auto-registering")
    metric_description: Optional[str] = Field(None, description="Description for auto-registration")

    @field_validator("domain")
    @classmethod
    def validate_domain_field(cls, v: MetricDomain | str) -> MetricDomain:
        if isinstance(v, MetricDomain):
            return v
        from agent72.application.services.normalization import EvidenceNormalizer
        return EvidenceNormalizer.normalize_domain(v)

    @field_validator("period")
    @classmethod
    def validate_period_format(cls, v: str) -> str:
        trimmed = v.strip()
        if not ACADEMIC_PERIOD_REGEX.match(trimmed):
            raise ValueError(
                f"Invalid academic period '{v}'. Expected format 'YYYY-YYYY' (e.g. '2024-2025'), 'YYYY-YY' (e.g. '2024-25'), 'YYYY-Q#' (e.g. '2024-Q1'), or 'YYYY'."
            )
        match_quarter = re.match(r"^\d{4}-[qQ](\d+)$", trimmed)
        if match_quarter and int(match_quarter.group(1)) > 4:
            raise ValueError(f"Invalid academic period '{v}'. Quarter must be between 1 and 4.")
        return trimmed


class EvidenceBatchIngestionDTO(BaseModel):
    """Batch ingestion boundary for bulk loading evidence from external source agents."""
    batch_id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), description="Optional batch ID for tracing")
    auto_register_metrics: bool = Field(default=False, description="Whether to auto-register unknown metrics if complete metadata provided")
    items: List[EvidenceIngestionDTO | dict] = Field(..., min_length=1, description="List of evidence records to ingest")


class IngestionErrorDTO(BaseModel):
    index: int = Field(..., description="0-indexed position in batch")
    metric_key: str = Field(..., description="Target metric key")
    error: str = Field(..., description="Reason for rejection")


class FreshnessInfoDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    status: FreshnessStatus
    age_days: int
    threshold_days: int
    as_of_date: Optional[date] = None


class EvidenceResponseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    institution_id: str
    unit_id: Optional[str]
    metric_key: str
    domain: MetricDomain
    numeric_value: Optional[float]
    text_value: Optional[str]
    unit: str
    period: str
    period_start: Optional[date]
    period_end: Optional[date]
    as_of_date: date
    captured_at: datetime
    source_type: SourceType
    source_name: str
    source_reference: Optional[str]
    confidence_score: float
    quality_tier: QualityTier
    is_stale: bool
    external_record_id: Optional[str] = None
    idempotency_key: Optional[str] = None
    ingestion_batch_id: Optional[str] = None
    freshness: Optional[FreshnessInfoDTO] = None


class EvidenceListResponseDTO(BaseModel):
    total: int
    items: List[EvidenceResponseDTO]


class BatchIngestionResultDTO(BaseModel):
    """Structured result returned for bulk evidence ingestion."""
    batch_id: str
    total: int
    inserted: int
    duplicates: int
    rejected: int
    errors: List[IngestionErrorDTO] = Field(default_factory=list)
    items: List[EvidenceResponseDTO] = Field(default_factory=list)


class HistoricalSeriesItemDTO(BaseModel):
    period: str
    numeric_value: Optional[float]
    text_value: Optional[str]
    as_of_date: date
    captured_at: datetime
    source_name: str
    confidence_score: float
    quality_tier: QualityTier
    freshness_status: FreshnessStatus


class HistoricalSeriesResponseDTO(BaseModel):
    institution_id: str
    unit_id: Optional[str]
    metric_key: str
    domain: MetricDomain
    unit: str
    total_observations: int
    series: List[HistoricalSeriesItemDTO] = Field(default_factory=list)
