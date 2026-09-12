"""Institutional Trajectory Analysis API endpoints (Phase 5)."""

from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from agent72.api.dependencies import get_trajectory_service
from agent72.application.dtos.trajectory_dto import (
    TrajectoryAnalysisListResponseDTO,
    TrajectoryAnalysisRequestDTO,
    TrajectoryAnalysisResponseDTO,
)
from agent72.application.services.trajectory_service import TrajectoryAnalysisService
from agent72.core.config import settings

router = APIRouter(prefix="/analysis", tags=["Institutional Trajectory Analysis"])


@router.post(
    "/trajectory",
    response_model=TrajectoryAnalysisResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Generate Institutional Trajectory Analysis",
    description=(
        "Executes deterministic multi-period trajectory analysis for an institution. "
        "Calculates directional movement, magnitude of change, consistency, volatility, "
        "and acceleration across canonical academic periods. Synthesizes signals with current "
        "position findings and persists an immutable snapshot."
    ),
)
def generate_trajectory_analysis(
    dto: TrajectoryAnalysisRequestDTO,
    service: TrajectoryAnalysisService = Depends(get_trajectory_service),
) -> TrajectoryAnalysisResponseDTO:
    return service.generate_trajectory_analysis(dto)


@router.get(
    "/trajectory/{analysis_id}",
    response_model=TrajectoryAnalysisResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="Get Trajectory Analysis Snapshot",
    description="Retrieves an immutable, finalized institutional trajectory analysis snapshot by ID.",
)
def get_trajectory_analysis_by_id(
    analysis_id: str,
    service: TrajectoryAnalysisService = Depends(get_trajectory_service),
) -> TrajectoryAnalysisResponseDTO:
    return service.get_trajectory_analysis_by_id(analysis_id)


@router.get(
    "/trajectory",
    response_model=TrajectoryAnalysisListResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="List Trajectory Analyses",
    description="Lists historical institutional trajectory analysis snapshots with optional filters and safe pagination.",
)
def list_trajectory_analyses(
    institution_id: Optional[str] = Query(None, description="Filter by institution UUID"),
    organizational_unit_id: Optional[str] = Query(None, description="Filter by unit UUID"),
    analysis_period: Optional[str] = Query(None, description="Filter by academic period e.g. '2024-2025'"),
    skip: int = Query(0, ge=0, description="Offset for pagination"),
    limit: int = Query(settings.DEFAULT_PAGE_SIZE, ge=1, le=settings.MAX_PAGE_SIZE, description="Max items to return (max 500)"),
    service: TrajectoryAnalysisService = Depends(get_trajectory_service),
) -> TrajectoryAnalysisListResponseDTO:
    return service.list_trajectory_analyses(
        institution_id=institution_id,
        organizational_unit_id=organizational_unit_id,
        analysis_period=analysis_period,
        skip=skip,
        limit=limit,
    )
