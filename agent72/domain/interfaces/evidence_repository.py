"""Abstract Repository Protocol for Institutional Metrics, Evidence, and Provenance."""

from abc import ABC, abstractmethod
from datetime import date
from typing import List, Optional
from agent72.domain.models.evidence import (
    InstitutionalEvidence,
    MetricDefinition,
    MetricDomain,
    SourceType,
    QualityTier,
    IngestionBatchLog,
)


class IEvidenceRepository(ABC):
    """Abstract interface defining persistence operations for metrics, time-series evidence, and audit logs."""

    @abstractmethod
    def create_metric_definition(self, definition: MetricDefinition) -> MetricDefinition:
        pass

    @abstractmethod
    def get_metric_definition(self, metric_key: str) -> Optional[MetricDefinition]:
        pass

    @abstractmethod
    def list_metric_definitions(self, domain: Optional[MetricDomain] = None) -> List[MetricDefinition]:
        pass

    @abstractmethod
    def find_existing_evidence(self, institution_id: str, idempotency_key: str) -> Optional[InstitutionalEvidence]:
        """Find an existing evidence item matching the idempotency key for deduplication."""
        pass

    @abstractmethod
    def record_evidence(self, evidence: InstitutionalEvidence) -> InstitutionalEvidence:
        pass

    @abstractmethod
    def record_evidence_batch(self, evidence_items: List[InstitutionalEvidence]) -> List[InstitutionalEvidence]:
        """Bulk-record canonical evidence items with atomic transaction."""
        pass

    @abstractmethod
    def query_evidence(
        self,
        institution_id: str,
        unit_id: Optional[str] = None,
        metric_key: Optional[str] = None,
        domain: Optional[MetricDomain] = None,
        period: Optional[str] = None,
        as_of_date_start: Optional[date] = None,
        as_of_date_end: Optional[date] = None,
        source_type: Optional[SourceType] = None,
        source_name: Optional[str] = None,
        quality_tier: Optional[QualityTier] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> List[InstitutionalEvidence]:
        """Query time-series evidence records with multi-dimensional filtering."""
        pass

    @abstractmethod
    def get_latest_evidence(
        self,
        institution_id: str,
        metric_key: str,
        unit_id: Optional[str] = None,
    ) -> Optional[InstitutionalEvidence]:
        """Retrieve the most recent evidence observation for a metric."""
        pass

    @abstractmethod
    def get_historical_series(
        self,
        institution_id: str,
        metric_key: str,
        unit_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> List[InstitutionalEvidence]:
        """Retrieve chronological historical time-series for trajectory and scenario analysis."""
        pass

    @abstractmethod
    def get_evidence_by_domain(
        self,
        institution_id: str,
        domain: MetricDomain,
        period: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> List[InstitutionalEvidence]:
        """Retrieve all evidence observations across an institutional domain."""
        pass

    @abstractmethod
    def record_batch_log(self, batch_log: IngestionBatchLog) -> IngestionBatchLog:
        """Record an ingestion audit log entry."""
        pass

    @abstractmethod
    def get_batch_log(self, batch_id: str) -> Optional[IngestionBatchLog]:
        """Get an ingestion audit log entry by batch_id."""
        pass

    @abstractmethod
    def find_by_batch_id(self, batch_id: str) -> List[InstitutionalEvidence]:
        """Find all evidence records associated with a specific ingestion batch."""
        pass
