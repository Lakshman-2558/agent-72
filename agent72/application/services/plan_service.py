"""Strategic Plan Application Service."""

from typing import List, Optional
from agent72.domain.interfaces.plan_repository import IPlanRepository
from agent72.domain.interfaces.ai_provider import IAIProvider
from agent72.domain.models.plan import (
    StrategicPlan,
    PlanObjective,
    PlanInitiative,
    InitiativeMilestone,
    StrategicOption,
    PlanScenario,
    ExecutionReview,
    PlanStatus,
)
from agent72.application.dtos.plan_dto import (
    StrategicPlanCreateDTO,
    StrategicPlanUpdateDTO,
    StrategicPlanResponseDTO,
    StrategicPlanListResponseDTO,
    ObjectiveResponseDTO,
    PlanInitiativeResponseDTO,
    InitiativeMilestoneResponseDTO,
    StrategicOptionResponseDTO,
    ScenarioResponseDTO,
    ExecutionReviewCreateDTO,
    ExecutionReviewResponseDTO,
)
from agent72.core.exceptions import EntityNotFoundException, ValidationError
from agent72.core.logging import get_logger

logger = get_logger(__name__)


class StrategicPlanService:
    """Orchestrates strategic planning business workflows."""

    def __init__(self, repository: IPlanRepository, ai_provider: IAIProvider) -> None:
        self.repository = repository
        self.ai_provider = ai_provider

    def _to_response_dto(self, plan: StrategicPlan) -> StrategicPlanResponseDTO:
        return StrategicPlanResponseDTO(
            id=plan.id or "",
            institution_id=plan.institution_id,
            title=plan.title,
            institution_name=plan.institution_name,
            horizon_start_year=plan.horizon_start_year,
            horizon_end_year=plan.horizon_end_year,
            vision_statement=plan.vision_statement,
            mission_statement=plan.mission_statement,
            existing_commitments=plan.existing_commitments,
            review_period=plan.review_period,
            status=plan.status,
            created_at=plan.created_at,
            updated_at=plan.updated_at,
            objectives=[
                ObjectiveResponseDTO(
                    id=obj.id or "",
                    plan_id=obj.plan_id or "",
                    title=obj.title,
                    description=obj.description,
                    target_metric=obj.target_metric,
                    metric_key=obj.metric_key,
                    target_period=obj.target_period,
                    baseline_value=obj.baseline_value,
                    target_value=obj.target_value,
                    weight=obj.weight,
                    owner=obj.owner,
                    initiatives=[
                        PlanInitiativeResponseDTO(
                            id=init.id or "",
                            objective_id=init.objective_id or "",
                            title=init.title,
                            description=init.description,
                            owner=init.owner,
                            budget=init.budget,
                            status=init.status,
                            start_date=init.start_date,
                            end_date=init.end_date,
                            created_at=init.created_at,
                            updated_at=init.updated_at,
                            milestones=[
                                InitiativeMilestoneResponseDTO(
                                    id=m.id or "",
                                    initiative_id=m.initiative_id or "",
                                    title=m.title,
                                    target_date=m.target_date,
                                    status=m.status,
                                    completion_date=m.completion_date,
                                    created_at=m.created_at,
                                )
                                for m in init.milestones
                            ],
                        )
                        for init in obj.initiatives
                    ],
                )
                for obj in plan.objectives
            ],
            strategic_options=[
                StrategicOptionResponseDTO(
                    id=opt.id or "",
                    plan_id=opt.plan_id or "",
                    title=opt.title,
                    rationale=opt.rationale,
                    resource_intensity=opt.resource_intensity,
                    estimated_cost=opt.estimated_cost,
                    risk_level=opt.risk_level,
                )
                for opt in plan.strategic_options
            ],
            scenarios=[
                ScenarioResponseDTO(
                    id=scn.id or "",
                    plan_id=scn.plan_id or "",
                    name=scn.name,
                    description=scn.description,
                    assumptions=scn.assumptions,
                    projected_outcome=scn.projected_outcome,
                )
                for scn in plan.scenarios
            ],
            execution_reviews=[
                ExecutionReviewResponseDTO(
                    id=rev.id or "",
                    plan_id=rev.plan_id or "",
                    period=rev.period,
                    review_date=rev.review_date,
                    progress_summary=rev.progress_summary,
                    variance_notes=rev.variance_notes,
                    recommendations=rev.recommendations,
                    created_at=rev.created_at,
                )
                for rev in plan.execution_reviews
            ],
        )

    def create_plan(self, dto: StrategicPlanCreateDTO) -> StrategicPlanResponseDTO:
        logger.info(f"Creating strategic plan for institution '{dto.institution_name}': {dto.title}")

        if dto.horizon_start_year > dto.horizon_end_year:
            raise ValidationError(
                f"Horizon start year ({dto.horizon_start_year}) cannot exceed end year ({dto.horizon_end_year})."
            )

        domain_plan = StrategicPlan(
            institution_id=dto.institution_id,
            title=dto.title,
            institution_name=dto.institution_name,
            horizon_start_year=dto.horizon_start_year,
            horizon_end_year=dto.horizon_end_year,
            vision_statement=dto.vision_statement,
            mission_statement=dto.mission_statement,
            existing_commitments=dto.existing_commitments,
            review_period=dto.review_period,
            status=PlanStatus.DRAFT,
            objectives=[
                PlanObjective(
                    title=obj.title,
                    description=obj.description,
                    target_metric=obj.target_metric,
                    metric_key=obj.metric_key,
                    target_period=obj.target_period,
                    baseline_value=obj.baseline_value,
                    target_value=obj.target_value,
                    weight=obj.weight,
                    owner=obj.owner,
                    initiatives=[
                        PlanInitiative(
                            title=init.title,
                            description=init.description,
                            owner=init.owner,
                            budget=init.budget,
                            status=init.status,
                            start_date=init.start_date,
                            end_date=init.end_date,
                            milestones=[
                                InitiativeMilestone(
                                    title=m.title,
                                    target_date=m.target_date,
                                    status=m.status,
                                    completion_date=m.completion_date,
                                )
                                for m in init.milestones
                            ],
                        )
                        for init in obj.initiatives
                    ],
                )
                for obj in dto.objectives
            ],
            strategic_options=[
                StrategicOption(
                    title=opt.title,
                    rationale=opt.rationale,
                    resource_intensity=opt.resource_intensity,
                    estimated_cost=opt.estimated_cost,
                    risk_level=opt.risk_level,
                )
                for opt in dto.strategic_options
            ],
            scenarios=[
                PlanScenario(
                    name=scn.name,
                    description=scn.description,
                    assumptions=scn.assumptions,
                    projected_outcome=scn.projected_outcome,
                )
                for scn in dto.scenarios
            ],
        )

        domain_plan.validate_horizon()
        created_plan = self.repository.create(domain_plan)
        return self._to_response_dto(created_plan)

    def get_plan(self, plan_id: str) -> StrategicPlanResponseDTO:
        plan = self.repository.get_by_id(plan_id)
        if not plan:
            raise EntityNotFoundException("StrategicPlan", plan_id)
        return self._to_response_dto(plan)

    def list_plans(self, skip: int = 0, limit: int = 50) -> StrategicPlanListResponseDTO:
        plans = self.repository.list_all(skip=skip, limit=limit)
        items = [self._to_response_dto(p) for p in plans]
        return StrategicPlanListResponseDTO(total=len(items), items=items)

    def update_plan(self, plan_id: str, dto: StrategicPlanUpdateDTO) -> StrategicPlanResponseDTO:
        existing = self.repository.get_by_id(plan_id)
        if not existing:
            raise EntityNotFoundException("StrategicPlan", plan_id)

        if dto.title is not None:
            existing.title = dto.title
        if dto.institution_name is not None:
            existing.institution_name = dto.institution_name
        if dto.horizon_start_year is not None:
            existing.horizon_start_year = dto.horizon_start_year
        if dto.horizon_end_year is not None:
            existing.horizon_end_year = dto.horizon_end_year
        if dto.vision_statement is not None:
            existing.vision_statement = dto.vision_statement
        if dto.mission_statement is not None:
            existing.mission_statement = dto.mission_statement
        if dto.existing_commitments is not None:
            existing.existing_commitments = dto.existing_commitments
        if dto.review_period is not None:
            existing.review_period = dto.review_period
        if dto.status is not None:
            existing.status = dto.status

        existing.validate_horizon()
        updated = self.repository.update(existing)
        return self._to_response_dto(updated)

    def delete_plan(self, plan_id: str) -> bool:
        success = self.repository.delete(plan_id)
        if not success:
            raise EntityNotFoundException("StrategicPlan", plan_id)
        return True

    def add_execution_review(self, plan_id: str, dto: ExecutionReviewCreateDTO) -> ExecutionReviewResponseDTO:
        existing = self.repository.get_by_id(plan_id)
        if not existing:
            raise EntityNotFoundException("StrategicPlan", plan_id)

        review = ExecutionReview(
            plan_id=plan_id,
            period=dto.period,
            review_date=dto.review_date,
            progress_summary=dto.progress_summary,
            variance_notes=dto.variance_notes,
            recommendations=dto.recommendations,
        )
        saved = self.repository.add_execution_review(plan_id, review)
        return ExecutionReviewResponseDTO(
            id=saved.id or "",
            plan_id=saved.plan_id or "",
            period=saved.period,
            review_date=saved.review_date,
            progress_summary=saved.progress_summary,
            variance_notes=saved.variance_notes,
            recommendations=saved.recommendations,
            created_at=saved.created_at,
        )
