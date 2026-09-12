"""Strategic Intelligence API endpoints (Phase 6)."""

from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from agent72.api.dependencies import get_strategic_intelligence_service
from agent72.application.dtos.strategic_intelligence_dto import (
    StrategicIntelligenceListResponseDTO,
    StrategicIntelligenceRequestDTO,
    StrategicIntelligenceResponseDTO,
)
from agent72.application.services.strategic_intelligence_service import StrategicIntelligenceService
from agent72.core.config import settings

router = APIRouter(prefix="/analysis", tags=["Strategic Intelligence"])


@router.post(
    "/strategic-intelligence",
    response_model=StrategicIntelligenceResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Generate Strategic Intelligence Analysis",
    description=(
        "Executes deterministic Phase 6 Strategic Intelligence analysis for an institution. "
        "Transforms Phase 4 Current Position and Phase 5 Trajectory baselines alongside multi-domain evidence "
        "into structured strategic issues, structural multi-metric risks, physical/faculty constraints, "
        "external factors with freshness penalties, and evidence-backed opportunities. "
        "Persists an immutable snapshot."
    ),
)
def generate_strategic_intelligence_analysis(
    dto: StrategicIntelligenceRequestDTO,
    service: StrategicIntelligenceService = Depends(get_strategic_intelligence_service),
) -> StrategicIntelligenceResponseDTO:
    return service.generate_strategic_intelligence_analysis(dto)


@router.get(
    "/strategic-intelligence/{analysis_id}",
    response_model=StrategicIntelligenceResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="Get Strategic Intelligence Analysis Snapshot",
    description="Retrieves an immutable, finalized institutional strategic intelligence analysis snapshot by ID.",
)
def get_strategic_intelligence_analysis_by_id(
    analysis_id: str,
    service: StrategicIntelligenceService = Depends(get_strategic_intelligence_service),
) -> StrategicIntelligenceResponseDTO:
    return service.get_strategic_intelligence_analysis_by_id(analysis_id)


@router.get(
    "/strategic-intelligence",
    response_model=StrategicIntelligenceListResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="List Strategic Intelligence Analyses",
    description="Lists historical institutional strategic intelligence analysis snapshots with optional filters and safe pagination.",
)
def list_strategic_intelligence_analyses(
    institution_id: Optional[str] = Query(None, description="Filter by institution UUID"),
    organizational_unit_id: Optional[str] = Query(None, description="Filter by unit UUID"),
    analysis_period: Optional[str] = Query(None, description="Filter by academic period e.g. '2024-2025'"),
    skip: int = Query(0, ge=0, description="Offset for pagination"),
    limit: int = Query(settings.DEFAULT_PAGE_SIZE, ge=1, le=settings.MAX_PAGE_SIZE, description="Max items to return (max 500)"),
    service: StrategicIntelligenceService = Depends(get_strategic_intelligence_service),
) -> StrategicIntelligenceListResponseDTO:
    return service.list_strategic_intelligence_analyses(
        institution_id=institution_id,
        organizational_unit_id=organizational_unit_id,
        analysis_period=analysis_period,
        skip=skip,
        limit=limit,
    )
