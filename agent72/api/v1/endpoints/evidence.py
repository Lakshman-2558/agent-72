"""Evidence, Metrics Catalog, Provenance, and Time-Series API endpoints."""

from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from agent72.api.dependencies import get_evidence_service
from agent72.domain.models.evidence import MetricDomain, QualityTier, SourceType
from agent72.application.dtos.evidence_dto import (
    EvidenceIngestionDTO,
    EvidenceBatchIngestionDTO,
    EvidenceResponseDTO,
    EvidenceListResponseDTO,
    BatchIngestionResultDTO,
    HistoricalSeriesResponseDTO,
    MetricDefinitionCreateDTO,
    MetricDefinitionResponseDTO,
    MetricDefinitionListResponseDTO,
)
from agent72.application.services.evidence_service import EvidenceService

router = APIRouter(prefix="/evidence", tags=["Institutional Evidence & Metrics"])


@router.post(
    "/metrics",
    response_model=MetricDefinitionResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Register Metric Definition",
    description="Registers an indicator/metric in the canonical metrics catalog.",
)
def create_metric_definition(
    dto: MetricDefinitionCreateDTO,
    service: EvidenceService = Depends(get_evidence_service),
) -> MetricDefinitionResponseDTO:
    return service.create_metric_definition(dto)


@router.get(
    "/metrics",
    response_model=MetricDefinitionListResponseDTO,
    summary="List Metric Definitions",
    description="Lists all registered canonical metric definitions with optional domain filter.",
)
def list_metric_definitions(
    domain: Optional[MetricDomain] = Query(None, description="Optional domain filter"),
    service: EvidenceService = Depends(get_evidence_service),
) -> MetricDefinitionListResponseDTO:
    return service.list_metric_definitions(domain=domain)


@router.get(
    "/metrics/{metric_key}",
    response_model=MetricDefinitionResponseDTO,
    summary="Get Metric Definition by Key",
    description="Fetches specification and metadata for a registered canonical metric.",
)
def get_metric_definition(
    metric_key: str,
    service: EvidenceService = Depends(get_evidence_service),
) -> MetricDefinitionResponseDTO:
    return service.get_metric_definition(metric_key)


@router.post(
    "/ingest",
    response_model=EvidenceResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Ingest Canonical Evidence (Single)",
    description=(
        "Canonical ingestion boundary for a single time-series evidence item. "
        "Normalizes keys, domains, units, and periods. Safely idempotent if re-submitted."
    ),
)
def ingest_evidence(
    dto: EvidenceIngestionDTO,
    auto_register: bool = Query(False, description="Whether to auto-register metric definition if complete metadata provided"),
    service: EvidenceService = Depends(get_evidence_service),
) -> EvidenceResponseDTO:
    return service.ingest_evidence(dto, auto_register_metrics=auto_register)


@router.post(
    "/ingest/batch",
    response_model=BatchIngestionResultDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Ingest Canonical Evidence (Batch)",
    description=(
        "Batch ingestion boundary for bulk-loading evidence from external source agents. "
        "Handles partial-batch failures gracefully, deduplicates repeated items, and creates an audit record."
    ),
)
def ingest_batch_evidence(
    dto: EvidenceBatchIngestionDTO,
    service: EvidenceService = Depends(get_evidence_service),
) -> BatchIngestionResultDTO:
    return service.ingest_batch(dto)


@router.get(
    "",
    response_model=EvidenceListResponseDTO,
    summary="Query Time-Series Evidence",
    description="Queries historical and current institutional measurements with multi-attribute filtering and pagination.",
)
def query_evidence(
    institution_id: str = Query(..., description="Target Institution ID"),
    unit_id: Optional[str] = Query(None, description="Optional Department/Unit filter"),
    metric_key: Optional[str] = Query(None, description="Optional canonical metric key"),
    domain: Optional[MetricDomain] = Query(None, description="Optional domain filter"),
    period: Optional[str] = Query(None, description="Academic period filter, e.g. '2024-2025'"),
    as_of_date_start: Optional[date] = Query(None, description="Filter measurements fresh as of this date or later"),
    as_of_date_end: Optional[date] = Query(None, description="Filter measurements fresh as of this date or earlier"),
    source_type: Optional[SourceType] = Query(None, description="AGENT, EXTERNAL, or MANUAL"),
    source_name: Optional[str] = Query(None, description="Source provider name"),
    quality_tier: Optional[QualityTier] = Query(None, description="VERIFIED, ESTIMATED, or PROVISIONAL"),
    skip: int = Query(0, ge=0, description="Offset for pagination"),
    limit: int = Query(50, ge=1, le=500, description="Page size (max 500)"),
    service: EvidenceService = Depends(get_evidence_service),
) -> EvidenceListResponseDTO:
    return service.query_evidence(
        institution_id=institution_id,
        unit_id=unit_id,
        metric_key=metric_key,
        domain=domain,
        period=period,
        as_of_date_start=as_of_date_start,
        as_of_date_end=as_of_date_end,
        source_type=source_type,
        source_name=source_name,
        quality_tier=quality_tier,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/latest",
    response_model=EvidenceResponseDTO,
    summary="Get Latest Evidence Observation",
    description="Retrieves the most recent observation for a specific metric and scope, enriched with dynamic freshness.",
)
def get_latest_evidence(
    institution_id: str = Query(..., description="Target Institution ID"),
    metric_key: str = Query(..., description="Canonical metric key"),
    unit_id: Optional[str] = Query(None, description="Optional Department/Unit filter"),
    service: EvidenceService = Depends(get_evidence_service),
) -> EvidenceResponseDTO:
    return service.get_latest_evidence(
        institution_id=institution_id,
        metric_key=metric_key,
        unit_id=unit_id,
    )


@router.get(
    "/series",
    response_model=HistoricalSeriesResponseDTO,
    summary="Get Historical Chronological Series",
    description="Retrieves chronological time-series observations for trajectory and scenario analysis.",
)
def get_historical_series(
    institution_id: str = Query(..., description="Target Institution ID"),
    metric_key: str = Query(..., description="Canonical metric key"),
    unit_id: Optional[str] = Query(None, description="Optional Department/Unit filter"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    service: EvidenceService = Depends(get_evidence_service),
) -> HistoricalSeriesResponseDTO:
    return service.get_historical_series(
        institution_id=institution_id,
        metric_key=metric_key,
        unit_id=unit_id,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/batches/{batch_id}",
    summary="Get Ingestion Batch Audit Record",
    description="Inspects audit metadata and all evidence items associated with an ingestion batch run.",
)
def get_batch_audit(
    batch_id: str,
    service: EvidenceService = Depends(get_evidence_service),
) -> dict:
    return service.get_batch_audit(batch_id)
