"""Current Institutional Position Analysis API endpoints."""

from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from agent72.api.dependencies import get_analysis_service
from agent72.application.dtos.analysis_dto import (
    AnalysisListResponseDTO,
    CurrentPositionAnalysisRequestDTO,
    CurrentPositionAnalysisResponseDTO,
)
from agent72.application.services.analysis_service import CurrentPositionAnalysisService
from agent72.core.config import settings

router = APIRouter(prefix="/analysis", tags=["Current Institutional Position Analysis"])


@router.post(
    "/current-position",
    response_model=CurrentPositionAnalysisResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Generate Current Position Analysis",
    description=(
        "Executes a deterministic, evidence-based current position analysis for an institution. "
        "Evaluates polarity-aware metric performance, compares against preceding observations and targets, "
        "isolates data quality gaps, computes transparent confidence, and persists an immutable snapshot."
    ),
)
def generate_current_position_analysis(
    dto: CurrentPositionAnalysisRequestDTO,
    service: CurrentPositionAnalysisService = Depends(get_analysis_service),
) -> CurrentPositionAnalysisResponseDTO:
    return service.generate_current_position_analysis(dto)


@router.get(
    "/current-position/{analysis_id}",
    response_model=CurrentPositionAnalysisResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="Get Current Position Analysis Snapshot",
    description="Retrieves an immutable, finalized current position analysis snapshot by ID.",
)
def get_analysis_by_id(
    analysis_id: str,
    service: CurrentPositionAnalysisService = Depends(get_analysis_service),
) -> CurrentPositionAnalysisResponseDTO:
    return service.get_analysis_by_id(analysis_id)


@router.get(
    "/current-position",
    response_model=AnalysisListResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="List Current Position Analyses",
    description="Lists historical current position analysis snapshots with optional filters and safe pagination.",
)
def list_analyses(
    institution_id: Optional[str] = Query(None, description="Filter by institution UUID"),
    organizational_unit_id: Optional[str] = Query(None, description="Filter by unit UUID"),
    analysis_period: Optional[str] = Query(None, description="Filter by academic period e.g. '2024-2025'"),
    skip: int = Query(0, ge=0, description="Offset for pagination"),
    limit: int = Query(settings.DEFAULT_PAGE_SIZE, ge=1, le=settings.MAX_PAGE_SIZE, description="Max items to return (max 500)"),
    service: CurrentPositionAnalysisService = Depends(get_analysis_service),
) -> AnalysisListResponseDTO:
    return service.list_analyses(
        institution_id=institution_id,
        organizational_unit_id=organizational_unit_id,
        analysis_period=analysis_period,
        skip=skip,
        limit=limit,
    )


from agent72.application.dtos.agent_query_dto import AgentQueryRequestDTO, AgentQueryResponseDTO
from agent72.application.services.agent_query_service import AgentQueryService
from agent72.api.dependencies import get_agent_query_service


@router.post(
    "/ask",
    response_model=AgentQueryResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="Ask Agent 72 Grounded Strategic Inquiry",
    description=(
        "Processes an evidence-grounded strategic inquiry from institutional leadership. "
        "Draws strictly from verified Current Position, Trajectory, Strategic Intelligence, "
        "Strategic Options, and Execution Review data. Never hallucinates metrics or recommendations."
    ),
)
def ask_agent_72(
    dto: AgentQueryRequestDTO,
    query_service: AgentQueryService = Depends(get_agent_query_service),
) -> AgentQueryResponseDTO:
    return query_service.answer_query(dto)

