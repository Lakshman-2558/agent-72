"""Strategic Options, Scenarios & Prioritization API endpoints (Phase 7)."""

from typing import Optional
from fastapi import APIRouter, Depends, Query, status

from agent72.api.dependencies import get_strategic_options_service
from agent72.application.dtos.strategic_options_dto import (
    StrategicOptionsListResponseDTO,
    StrategicOptionsRequestDTO,
    StrategicOptionsResponseDTO,
)
from agent72.application.services.strategic_options_service import StrategicOptionsService
from agent72.core.config import settings

router = APIRouter(prefix="/analysis", tags=["Strategic Options"])


@router.post(
    "/strategic-options",
    response_model=StrategicOptionsResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Generate Strategic Options Analysis",
    description=(
        "Executes deterministic Phase 7 Strategic Options generation, scenario analysis, "
        "and 7-dimension option evaluation for leadership consideration. "
        "Transforms Phase 6 Strategic Intelligence into evidence-grounded strategic choices, "
        "formulates conditional qualitative scenarios (Baseline, Upside, Downside, Stress), "
        "evaluates options deterministically, and ranks them by priority."
    ),
)
def generate_strategic_options_analysis(
    dto: StrategicOptionsRequestDTO,
    service: StrategicOptionsService = Depends(get_strategic_options_service),
) -> StrategicOptionsResponseDTO:
    return service.generate_strategic_options_analysis(dto)


@router.get(
    "/strategic-options/{analysis_id}",
    response_model=StrategicOptionsResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="Get Strategic Options Analysis Snapshot",
    description="Retrieves an immutable, finalized institutional strategic options snapshot by ID.",
)
def get_strategic_options_analysis_by_id(
    analysis_id: str,
    service: StrategicOptionsService = Depends(get_strategic_options_service),
) -> StrategicOptionsResponseDTO:
    return service.get_analysis_by_id(analysis_id)


@router.get(
    "/strategic-options",
    response_model=StrategicOptionsListResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="List Strategic Options Analyses",
    description="Lists historical institutional strategic options snapshots with optional filters and safe pagination.",
)
def list_strategic_options_analyses(
    institution_id: Optional[str] = Query(None, description="Filter by institution UUID"),
    organizational_unit_id: Optional[str] = Query(None, description="Filter by unit UUID"),
    analysis_period: Optional[str] = Query(None, description="Filter by academic period e.g. '2024-2025'"),
    skip: int = Query(0, ge=0, description="Offset for pagination"),
    limit: int = Query(settings.DEFAULT_PAGE_SIZE, ge=1, le=settings.MAX_PAGE_SIZE, description="Max items to return (max 500)"),
    service: StrategicOptionsService = Depends(get_strategic_options_service),
) -> StrategicOptionsListResponseDTO:
    return service.list_analyses(
        institution_id=institution_id,
        organizational_unit_id=organizational_unit_id,
        analysis_period=analysis_period,
        skip=skip,
        limit=limit,
    )
