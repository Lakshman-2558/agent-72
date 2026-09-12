"""Domain entities for Institutional Metrics, Evidence, Provenance, and Freshness."""

from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from enum import Enum
from typing import Optional


class MetricDomain(str, Enum):
    ACADEMIC_PERFORMANCE = "ACADEMIC_PERFORMANCE"
    ADMISSIONS_MARKET = "ADMISSIONS_MARKET"
    PLACEMENT_EMPLOYER_DEMAND = "PLACEMENT_EMPLOYER_DEMAND"
    RESEARCH_PRODUCTIVITY = "RESEARCH_PRODUCTIVITY"
    FACULTY_CAPABILITY = "FACULTY_CAPABILITY"
    INFRASTRUCTURE = "INFRASTRUCTURE"
    FINANCE_RESOURCES = "FINANCE_RESOURCES"
    EXTERNAL_REGULATORY = "EXTERNAL_REGULATORY"
    PEER_COMPETITOR = "PEER_COMPETITOR"


class SourceType(str, Enum):
    AGENT = "AGENT"
    EXTERNAL = "EXTERNAL"
    MANUAL = "MANUAL"


class QualityTier(str, Enum):
    VERIFIED = "VERIFIED"
    ESTIMATED = "ESTIMATED"
    PROVISIONAL = "PROVISIONAL"


class FreshnessStatus(str, Enum):
    FRESH = "FRESH"
    AGING = "AGING"
    STALE = "STALE"


class MetricDirection(str, Enum):
    """Specifies the polarity/directionality of a metric for performance interpretation."""
    HIGHER_IS_BETTER = "HIGHER_IS_BETTER"
    LOWER_IS_BETTER = "LOWER_IS_BETTER"
    TARGET_RANGE = "TARGET_RANGE"
    NEUTRAL = "NEUTRAL"


@dataclass
class FreshnessMetadata:
    """Dynamically evaluated freshness metadata."""
    status: FreshnessStatus = FreshnessStatus.FRESH
    age_days: int = 0
    threshold_days: int = 180
    as_of_date: Optional[date] = None


@dataclass
class MetricDefinition:
    """Canonical catalogue entry defining an institutional indicator/metric."""
    id: Optional[str] = None
    metric_key: str = ""
    name: str = ""
    domain: MetricDomain = MetricDomain.ACADEMIC_PERFORMANCE
    direction: MetricDirection = MetricDirection.HIGHER_IS_BETTER
    default_unit: str = "count"
    description: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class InstitutionalEvidence:
    """
    Time-series evidence record with immutable provenance.
    Answers: Where did it come from? When captured? What period? Stale/current? Confidence?
    """
    id: Optional[str] = None
    institution_id: str = ""
    unit_id: Optional[str] = None
    metric_key: str = ""
    domain: MetricDomain = MetricDomain.ACADEMIC_PERFORMANCE
    numeric_value: Optional[float] = None
    text_value: Optional[str] = None
    unit: str = ""
    period: str = ""  # Academic year e.g. "2024-2025" or period "2024-Q1"
    period_start: Optional[date] = None
    period_end: Optional[date] = None
    as_of_date: date = field(default_factory=lambda: datetime.now(timezone.utc).date())
    captured_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    source_type: SourceType = SourceType.MANUAL
    source_name: str = "Manual Entry"  # e.g., "Agent 20", "Agent 38", "NIRF Report"
    source_reference: Optional[str] = None  # Reference run ID, citation, or document ID
    confidence_score: float = 1.0  # 0.0 to 1.0
    quality_tier: QualityTier = QualityTier.VERIFIED
    is_stale: bool = False

    # Ingestion & Idempotency Metadata
    external_record_id: Optional[str] = None
    idempotency_key: Optional[str] = None
    ingestion_batch_id: Optional[str] = None

    # Dynamically calculated freshness (evaluated at query time)
    freshness: Optional[FreshnessMetadata] = None

    def validate_provenance(self) -> None:
        """Domain invariant check for evidence provenance."""
        if not (0.0 <= self.confidence_score <= 1.0):
            raise ValueError(f"Confidence score ({self.confidence_score}) must be between 0.0 and 1.0.")
        if not self.metric_key.strip():
            raise ValueError("metric_key is required for institutional evidence.")
        if not self.period.strip():
            raise ValueError("period is required for institutional evidence.")


@dataclass
class IngestionBatchLog:
    """Audit log for ingestion runs, tracing source, volume, and result status."""
    id: Optional[str] = None
    batch_id: str = ""
    source_name: str = ""
    received_count: int = 0
    inserted_count: int = 0
    duplicate_count: int = 0
    rejected_count: int = 0
    error_summary: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
