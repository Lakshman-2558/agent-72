"""Strategic Plan API endpoints supporting Phase 1 and Phase 8 execution framework."""

from typing import Optional, Union, Any
from fastapi import APIRouter, Depends, Query, status
from agent72.api.dependencies import (
    get_plan_service,
    get_strategic_plan_execution_service,
)
from agent72.application.dtos.plan_dto import (
    StrategicPlanCreateDTO,
    StrategicPlanUpdateDTO,
    StrategicPlanResponseDTO as Phase1StrategicPlanResponseDTO,
    StrategicPlanListResponseDTO as Phase1StrategicPlanListResponseDTO,
    ExecutionReviewCreateDTO,
    ExecutionReviewResponseDTO as Phase1ExecutionReviewResponseDTO,
)
from agent72.application.dtos.strategic_plan_dto import (
    StrategicPlanGenerationRequestDTO,
    StrategicPlanResponseDTO as Phase8StrategicPlanResponseDTO,
    StrategicPlanListResponseDTO as Phase8StrategicPlanListResponseDTO,
    ExecutionReviewRequestDTO,
    ExecutionReviewDTO as Phase8ExecutionReviewDTO,
    PlanDecisionRequestDTO,
)
from agent72.application.services.plan_service import StrategicPlanService
from agent72.application.services.strategic_plan_service import StrategicPlanExecutionService

router = APIRouter(prefix="/plans", tags=["Strategic Plans"])


# ==============================================================================
# Phase 8 Execution Endpoints
# ==============================================================================

@router.post(
    "/generate",
    response_model=Phase8StrategicPlanResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Generate Strategic Plan from Phase 7 Options",
    description="Transforms leadership-selected Phase 7 strategic options into a structured institutional strategic plan candidate.",
)
def generate_strategic_plan(
    dto: StrategicPlanGenerationRequestDTO,
    service: StrategicPlanExecutionService = Depends(get_strategic_plan_execution_service),
) -> Phase8StrategicPlanResponseDTO:
    return service.generate_plan_from_options(dto)


@router.post(
    "/{plan_id}/review",
    response_model=Phase8ExecutionReviewDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Conduct Execution Review",
    description="Performs an automated deterministic periodic or annual execution review comparing targets vs observed evidence.",
)
def execute_plan_review(
    plan_id: str,
    dto: ExecutionReviewRequestDTO,
    service: StrategicPlanExecutionService = Depends(get_strategic_plan_execution_service),
) -> Phase8ExecutionReviewDTO:
    return service.record_execution_review(plan_id, dto)


@router.get(
    "/{plan_id}/review/latest",
    response_model=Phase8ExecutionReviewDTO,
    status_code=status.HTTP_200_OK,
    summary="Get Latest Execution Review for Plan",
    description="Retrieves the most recent deterministic execution review snapshot for a strategic plan.",
)
def get_latest_plan_review(
    plan_id: str,
    service: StrategicPlanExecutionService = Depends(get_strategic_plan_execution_service),
) -> Phase8ExecutionReviewDTO:
    plan = service.get_plan(plan_id)
    if not plan.execution_reviews:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No execution reviews have been recorded yet for plan '{plan_id}'.",
        )
    return plan.execution_reviews[-1]



@router.post(
    "/{plan_id}/decision",
    response_model=Phase8StrategicPlanResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="Record Leadership Governance Decision",
    description="Records an explicit leadership decision (SELECT, DEFER, REJECT, APPROVE, ACTIVATE) on a strategic plan.",
)
def record_plan_decision(
    plan_id: str,
    dto: PlanDecisionRequestDTO,
    service: StrategicPlanExecutionService = Depends(get_strategic_plan_execution_service),
) -> Phase8StrategicPlanResponseDTO:
    return service.update_plan_decision(plan_id, dto)


# ==============================================================================
# Phase 1 & Backward Compatible Endpoints
# ==============================================================================

@router.post(
    "",
    response_model=Phase1StrategicPlanResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new Strategic Plan",
    description="Initializes and persists a new institutional strategic plan with optional objectives, scenarios, and options.",
)
def create_plan(
    dto: StrategicPlanCreateDTO,
    service: StrategicPlanService = Depends(get_plan_service),
) -> Phase1StrategicPlanResponseDTO:
    return service.create_plan(dto)


@router.get(
    "",
    response_model=Union[Phase8StrategicPlanListResponseDTO, Phase1StrategicPlanListResponseDTO],
    summary="List Strategic Plans",
    description="Retrieves a paginated list of institutional strategic plans ordered by creation date.",
)
def list_plans(
    institution_id: Optional[str] = Query(None, description="Filter by institution UUID"),
    plan_status: Optional[str] = Query(None, alias="status", description="Filter by plan status"),
    skip: int = Query(0, ge=0, description="Offset for pagination"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of plans to return"),
    exec_service: StrategicPlanExecutionService = Depends(get_strategic_plan_execution_service),
    plan_service: StrategicPlanService = Depends(get_plan_service),
) -> Any:
    # Use execution service which provides rich Phase 8 representation with Phase 1 compatibility
    return exec_service.list_plans(institution_id=institution_id, status=plan_status, skip=skip, limit=limit)


@router.get(
    "/{plan_id}",
    response_model=Union[Phase8StrategicPlanResponseDTO, Phase1StrategicPlanResponseDTO],
    summary="Get Strategic Plan by ID",
    description="Fetches detailed configuration, objectives, targets, initiatives, milestones, scenarios, and options for a specific plan.",
)
def get_plan(
    plan_id: str,
    exec_service: StrategicPlanExecutionService = Depends(get_strategic_plan_execution_service),
    plan_service: StrategicPlanService = Depends(get_plan_service),
) -> Any:
    return exec_service.get_plan(plan_id)


@router.put(
    "/{plan_id}",
    response_model=Phase1StrategicPlanResponseDTO,
    summary="Update Strategic Plan",
    description="Updates institutional metadata or workflow status of a strategic plan.",
)
def update_plan(
    plan_id: str,
    dto: StrategicPlanUpdateDTO,
    service: StrategicPlanService = Depends(get_plan_service),
) -> Phase1StrategicPlanResponseDTO:
    return service.update_plan(plan_id, dto)


@router.delete(
    "/{plan_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Strategic Plan",
    description="Permanently removes a strategic plan and cascades deletion to associated objectives and scenarios.",
)
def delete_plan(
    plan_id: str,
    service: StrategicPlanService = Depends(get_plan_service),
) -> None:
    service.delete_plan(plan_id)


@router.post(
    "/{plan_id}/reviews",
    response_model=Phase1ExecutionReviewResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Record Manual Execution Review (Phase 1)",
    description="Records a periodic or annual manual execution review assessing plan progress and variance.",
)
def add_execution_review(
    plan_id: str,
    dto: ExecutionReviewCreateDTO,
    service: StrategicPlanService = Depends(get_plan_service),
) -> Phase1ExecutionReviewResponseDTO:
    return service.add_execution_review(plan_id, dto)
