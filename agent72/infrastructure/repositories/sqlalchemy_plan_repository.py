"""SQLAlchemy implementation of IPlanRepository."""

import uuid
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session

from agent72.domain.interfaces.plan_repository import IPlanRepository
from agent72.domain.models.plan import (
    StrategicPlan,
    PlanObjective,
    PlanInitiative,
    InitiativeMilestone,
    StrategicOption,
    PlanScenario,
    ExecutionReview,
    PlanStatus,
    ResourceIntensity,
    RiskLevel,
    InitiativeStatus,
    MilestoneStatus,
)
from agent72.infrastructure.database.models import (
    StrategicPlanModel,
    PlanObjectiveModel,
    PlanInitiativeModel,
    InitiativeMilestoneModel,
    StrategicOptionModel,
    PlanScenarioModel,
    ExecutionReviewModel,
    StrategicTargetModel,
)
from agent72.domain.models.strategic_plan_execution import (
    StrategicPlan as ExecutionStrategicPlan,
    StrategicObjective as ExecutionObjective,
    StrategicTarget as ExecutionTarget,
    PlanInitiative as ExecutionInitiative,
    InitiativeMilestone as ExecutionMilestone,
    ExecutionReview as Phase8ExecutionReview,
    PlanStatus as ExecutionPlanStatus,
    ObjectiveStatus as ExecutionObjectiveStatus,
    InitiativeStatus as ExecutionInitiativeStatus,
    MilestoneStatus as ExecutionMilestoneStatus,
    ReviewStatus as ExecutionReviewStatus,
    TargetDirection as ExecutionTargetDirection,
    TargetStatus as ExecutionTargetStatus,
    ResourceRequirement as ExecutionResourceRequirement,
    TargetVariance,
    CorrectiveActionCandidate,
    DiagnosticSignalType,
    LEADERSHIP_DECISION_SUPPORT_DISCLAIMER,
)



class SQLAlchemyPlanRepository(IPlanRepository):
    """Data-access repository implementing IPlanRepository with SQLAlchemy 2.0."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def _to_domain(self, model: StrategicPlanModel) -> StrategicPlan:
        """Convert ORM model to pure Domain entity."""
        return StrategicPlan(
            id=model.id,
            institution_id=model.institution_id,
            title=model.title,
            institution_name=model.institution_name,
            horizon_start_year=model.horizon_start_year,
            horizon_end_year=model.horizon_end_year,
            vision_statement=model.vision_statement,
            mission_statement=model.mission_statement,
            existing_commitments=model.existing_commitments,
            review_period=model.review_period,
            status=PlanStatus(model.status),
            created_at=model.created_at,
            updated_at=model.updated_at,
            objectives=[
                PlanObjective(
                    id=obj.id,
                    plan_id=obj.plan_id,
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
                            id=init.id,
                            objective_id=init.objective_id,
                            title=init.title,
                            description=init.description,
                            owner=init.owner,
                            budget=init.budget,
                            status=InitiativeStatus(init.status),
                            start_date=init.start_date,
                            end_date=init.end_date,
                            created_at=init.created_at,
                            updated_at=init.updated_at,
                            milestones=[
                                InitiativeMilestone(
                                    id=m.id,
                                    initiative_id=m.initiative_id,
                                    title=m.title,
                                    target_date=m.target_date,
                                    status=MilestoneStatus(m.status),
                                    completion_date=m.completion_date,
                                    created_at=m.created_at,
                                )
                                for m in init.milestones
                            ],
                        )
                        for init in obj.initiatives
                    ],
                )
                for obj in model.objectives
            ],
            strategic_options=[
                StrategicOption(
                    id=opt.id,
                    plan_id=opt.plan_id,
                    title=opt.title,
                    rationale=opt.rationale,
                    resource_intensity=ResourceIntensity(opt.resource_intensity),
                    estimated_cost=opt.estimated_cost,
                    risk_level=RiskLevel(opt.risk_level),
                )
                for opt in model.strategic_options
            ],
            scenarios=[
                PlanScenario(
                    id=scn.id,
                    plan_id=scn.plan_id,
                    name=scn.name,
                    description=scn.description,
                    assumptions=scn.assumptions,
                    projected_outcome=scn.projected_outcome,
                )
                for scn in model.scenarios
            ],
            execution_reviews=[
                ExecutionReview(
                    id=rev.id,
                    plan_id=rev.plan_id,
                    period=rev.period,
                    review_date=rev.review_date,
                    progress_summary=rev.progress_summary,
                    variance_notes=rev.variance_notes,
                    recommendations=rev.recommendations,
                    created_at=rev.created_at,
                )
                for rev in model.execution_reviews
            ],
        )

    def get_by_id(self, plan_id: str) -> Optional[StrategicPlan]:
        stmt = select(StrategicPlanModel).where(StrategicPlanModel.id == plan_id)
        model = self.session.execute(stmt).scalar_one_or_none()
        if not model:
            return None
        return self._to_domain(model)

    def list_all(self, skip: int = 0, limit: int = 50) -> List[StrategicPlan]:
        stmt = (
            select(StrategicPlanModel)
            .order_by(StrategicPlanModel.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        models = self.session.execute(stmt).scalars().all()
        return [self._to_domain(m) for m in models]

    def create(self, plan: StrategicPlan) -> StrategicPlan:
        plan_id = plan.id or str(uuid.uuid4())
        model = StrategicPlanModel(
            id=plan_id,
            institution_id=plan.institution_id,
            title=plan.title,
            institution_name=plan.institution_name,
            horizon_start_year=plan.horizon_start_year,
            horizon_end_year=plan.horizon_end_year,
            vision_statement=plan.vision_statement,
            mission_statement=plan.mission_statement,
            existing_commitments=plan.existing_commitments,
            review_period=plan.review_period,
            status=plan.status.value,
        )

        for obj in plan.objectives:
            obj_id = obj.id or str(uuid.uuid4())
            obj_model = PlanObjectiveModel(
                id=obj_id,
                plan_id=plan_id,
                title=obj.title,
                description=obj.description,
                target_metric=obj.target_metric,
                metric_key=obj.metric_key,
                target_period=obj.target_period,
                baseline_value=obj.baseline_value,
                target_value=obj.target_value,
                weight=obj.weight,
                owner=obj.owner,
            )

            for init in obj.initiatives:
                init_id = init.id or str(uuid.uuid4())
                init_model = PlanInitiativeModel(
                    id=init_id,
                    objective_id=obj_id,
                    title=init.title,
                    description=init.description,
                    owner=init.owner,
                    budget=init.budget,
                    status=init.status.value,
                    start_date=init.start_date,
                    end_date=init.end_date,
                )
                for m in init.milestones:
                    init_model.milestones.append(
                        InitiativeMilestoneModel(
                            id=m.id or str(uuid.uuid4()),
                            initiative_id=init_id,
                            title=m.title,
                            target_date=m.target_date,
                            status=m.status.value,
                            completion_date=m.completion_date,
                        )
                    )
                obj_model.initiatives.append(init_model)

            model.objectives.append(obj_model)

        for opt in plan.strategic_options:
            model.strategic_options.append(
                StrategicOptionModel(
                    id=opt.id or str(uuid.uuid4()),
                    plan_id=plan_id,
                    title=opt.title,
                    rationale=opt.rationale,
                    resource_intensity=opt.resource_intensity.value,
                    estimated_cost=opt.estimated_cost,
                    risk_level=opt.risk_level.value,
                )
            )

        for scn in plan.scenarios:
            model.scenarios.append(
                PlanScenarioModel(
                    id=scn.id or str(uuid.uuid4()),
                    plan_id=plan_id,
                    name=scn.name,
                    description=scn.description,
                    assumptions=scn.assumptions,
                    projected_outcome=scn.projected_outcome,
                )
            )

        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return self._to_domain(model)

    def update(self, plan: StrategicPlan) -> StrategicPlan:
        stmt = select(StrategicPlanModel).where(StrategicPlanModel.id == plan.id)
        model = self.session.execute(stmt).scalar_one_or_none()
        if not model:
            raise ValueError(f"Plan with id {plan.id} does not exist.")

        model.institution_id = plan.institution_id
        model.title = plan.title
        model.institution_name = plan.institution_name
        model.horizon_start_year = plan.horizon_start_year
        model.horizon_end_year = plan.horizon_end_year
        model.vision_statement = plan.vision_statement
        model.mission_statement = plan.mission_statement
        model.existing_commitments = plan.existing_commitments
        model.review_period = plan.review_period
        model.status = plan.status.value

        self.session.commit()
        self.session.refresh(model)
        return self._to_domain(model)

    def delete(self, plan_id: str) -> bool:
        stmt = select(StrategicPlanModel).where(StrategicPlanModel.id == plan_id)
        model = self.session.execute(stmt).scalar_one_or_none()
        if not model:
            return False
        self.session.delete(model)
        self.session.commit()
        return True

    def add_execution_review(self, plan_id: str, review: ExecutionReview) -> ExecutionReview:
        stmt = select(StrategicPlanModel).where(StrategicPlanModel.id == plan_id)
        model = self.session.execute(stmt).scalar_one_or_none()
        if not model:
            raise ValueError(f"Plan with id {plan_id} does not exist.")

        rev_id = review.id or str(uuid.uuid4())
        rev_model = ExecutionReviewModel(
            id=rev_id,
            plan_id=plan_id,
            period=review.period,
            review_date=review.review_date,
            progress_summary=review.progress_summary,
            variance_notes=review.variance_notes,
            recommendations=review.recommendations,
        )
        self.session.add(rev_model)
        self.session.commit()
        self.session.refresh(rev_model)
        return ExecutionReview(
            id=rev_model.id,
            plan_id=rev_model.plan_id,
            period=rev_model.period,
            review_date=rev_model.review_date,
            progress_summary=rev_model.progress_summary,
            variance_notes=rev_model.variance_notes,
            recommendations=rev_model.recommendations,
            created_at=rev_model.created_at,
        )

    def _execution_model_to_domain(self, model: StrategicPlanModel) -> ExecutionStrategicPlan:
        """Convert ORM model to Phase 8 ExecutionStrategicPlan domain entity."""
        objectives: List[ExecutionObjective] = []
        for obj in model.objectives:
            targets: List[ExecutionTarget] = []
            for tgt in obj.targets:
                dir_val = ExecutionTargetDirection.HIGHER_IS_BETTER
                if tgt.direction in ExecutionTargetDirection.__members__:
                    dir_val = ExecutionTargetDirection(tgt.direction)
                status_val = ExecutionTargetStatus.PROPOSED_TARGET
                if tgt.status in ExecutionTargetStatus.__members__:
                    status_val = ExecutionTargetStatus(tgt.status)
                targets.append(
                    ExecutionTarget(
                        id=tgt.id,
                        objective_id=tgt.objective_id,
                        metric_key=tgt.metric_key,
                        metric_definition_id=tgt.metric_definition_id,
                        baseline_value=tgt.baseline_value,
                        baseline_period=tgt.baseline_period,
                        target_value=tgt.target_value,
                        target_period=tgt.target_period,
                        direction=dir_val,
                        unit=tgt.unit,
                        measurement_frequency=tgt.measurement_frequency,
                        evidence_ids=tgt.evidence_ids or [],
                        confidence=tgt.confidence,
                        assumptions=tgt.assumptions or [],
                        status=status_val,
                        gap=tgt.gap,
                        gap_unit_label=tgt.gap_unit_label or "",
                        target_provenance=tgt.target_provenance or "DERIVED_FROM_EVIDENCE",
                    )
                )

            if not targets and obj.target_metric:
                targets.append(
                    ExecutionTarget(
                        id=str(uuid.uuid4()),
                        objective_id=obj.id,
                        metric_key=obj.metric_key or obj.target_metric,
                        baseline_value=obj.baseline_value,
                        target_value=obj.target_value,
                        target_period=obj.target_period,
                        direction=ExecutionTargetDirection.HIGHER_IS_BETTER,
                        status=ExecutionTargetStatus.PROPOSED_TARGET,
                    )
                )

            initiatives: List[ExecutionInitiative] = []
            for init in obj.initiatives:
                milestones: List[ExecutionMilestone] = []
                for m in init.milestones:
                    m_status = ExecutionMilestoneStatus.NOT_STARTED
                    if m.status in ExecutionMilestoneStatus.__members__:
                        m_status = ExecutionMilestoneStatus(m.status)
                    elif m.status == "ACHIEVED":
                        m_status = ExecutionMilestoneStatus.COMPLETED
                    elif m.status == "PENDING":
                        m_status = ExecutionMilestoneStatus.NOT_STARTED
                    milestones.append(
                        ExecutionMilestone(
                            id=m.id,
                            initiative_id=m.initiative_id,
                            title=m.title,
                            description=m.description,
                            due_period=m.due_period or (str(m.target_date) if m.target_date else ""),
                            status=m_status,
                            completion_percentage=m.completion_percentage or (100.0 if m.status == "ACHIEVED" else 0.0),
                            evidence_ids=m.evidence_ids or [],
                            target_date=m.target_date,
                            completion_date=m.completion_date,
                        )
                    )


                init_status = ExecutionInitiativeStatus.PLANNED
                if init.status in ExecutionInitiativeStatus.__members__:
                    init_status = ExecutionInitiativeStatus(init.status)
                elif init.status in ("NOT_STARTED", "PENDING"):
                    init_status = ExecutionInitiativeStatus.PLANNED
                elif init.status in ("IN_PROGRESS", "ON_TRACK"):
                    init_status = ExecutionInitiativeStatus.ACTIVE
                res_req = ExecutionResourceRequirement.UNKNOWN
                if init.resource_requirement in ExecutionResourceRequirement.__members__:
                    res_req = ExecutionResourceRequirement(init.resource_requirement)


                initiatives.append(
                    ExecutionInitiative(
                        id=init.id,
                        objective_id=init.objective_id,
                        title=init.title,
                        description=init.description,
                        rationale=init.description,
                        owner_unit_id=init.owner_unit_id or init.owner or "TO_BE_ASSIGNED",
                        supporting_units=init.supporting_units or [],
                        source_option_ids=init.source_option_ids or [],
                        dependencies=init.dependencies or [],
                        resource_requirement=res_req,
                        implementation_risk=init.implementation_risk or "MEDIUM",
                        start_period=init.start_period or (str(init.start_date) if init.start_date else ""),
                        end_period=init.end_period or (str(init.end_date) if init.end_date else ""),
                        status=init_status,
                        success_criteria=init.success_criteria or [],
                        evidence_ids=init.evidence_ids or [],
                        milestones=milestones,
                    )
                )

            obj_status = ExecutionObjectiveStatus.PROPOSED
            if obj.status in ExecutionObjectiveStatus.__members__:
                obj_status = ExecutionObjectiveStatus(obj.status)

            exec_obj = ExecutionObjective(
                id=obj.id,
                strategic_plan_id=obj.plan_id,
                title=obj.title,
                description=obj.description,
                strategic_rationale=obj.description,
                source_option_ids=obj.source_option_ids or [],
                strategic_issue_ids=obj.strategic_issue_ids or [],
                related_metrics=obj.related_metrics or ([obj.metric_key] if obj.metric_key else []),
                status=obj_status,
                priority=obj.priority or "MEDIUM",
                owner_unit_id=obj.owner_unit_id or obj.owner or "TO_BE_ASSIGNED",
                assumptions=obj.assumptions or [],
                confidence=obj.confidence or 1.0,
                targets=targets,
                initiatives=initiatives,
            )
            # Attach Phase 1 attributes for backward compatibility
            exec_obj.target_metric = obj.target_metric
            exec_obj.baseline_value = obj.baseline_value
            exec_obj.target_value = obj.target_value
            exec_obj.metric_key = obj.metric_key
            exec_obj.target_period = obj.target_period
            exec_obj.owner = obj.owner
            objectives.append(exec_obj)


        reviews: List[Phase8ExecutionReview] = []
        for rev in model.execution_reviews:
            variances: List[TargetVariance] = []
            if rev.metric_variances:
                for v in rev.metric_variances:
                    dir_val = ExecutionTargetDirection.HIGHER_IS_BETTER
                    if v.get("direction") in ExecutionTargetDirection.__members__:
                        dir_val = ExecutionTargetDirection(v["direction"])
                    st_val = ExecutionReviewStatus.INSUFFICIENT_EVIDENCE
                    if v.get("status") in ExecutionReviewStatus.__members__:
                        st_val = ExecutionReviewStatus(v["status"])
                    variances.append(
                        TargetVariance(
                            metric_key=v.get("metric_key", ""),
                            metric_definition_id=v.get("metric_definition_id"),
                            baseline_value=v.get("baseline_value"),
                            target_value=v.get("target_value"),
                            observed_value=v.get("observed_value"),
                            observed_period=v.get("observed_period"),
                            absolute_variance=v.get("absolute_variance"),
                            relative_variance=v.get("relative_variance"),
                            unit=v.get("unit", "count"),
                            is_percentage=v.get("is_percentage", False),
                            variance_notation=v.get("variance_notation", ""),
                            direction=dir_val,
                            status=st_val,
                            notes=v.get("notes"),
                        )
                    )

            actions: List[CorrectiveActionCandidate] = []
            if rev.corrective_actions:
                for c in rev.corrective_actions:
                    sig_val = DiagnosticSignalType.TARGET_OFF_TRACK
                    if c.get("signal_type") in DiagnosticSignalType.__members__:
                        sig_val = DiagnosticSignalType(c["signal_type"])
                    actions.append(
                        CorrectiveActionCandidate(
                            id=c.get("id", str(uuid.uuid4())),
                            objective_id=c.get("objective_id"),
                            initiative_id=c.get("initiative_id"),
                            signal_type=sig_val,
                            title=c.get("title", ""),
                            description=c.get("description", ""),
                            suggested_action=c.get("suggested_action", ""),
                            rationale=c.get("rationale", ""),
                            requires_leadership_approval=c.get("requires_leadership_approval", True),
                        )
                    )

            overall_st = ExecutionReviewStatus.ON_TRACK
            if rev.overall_status in ExecutionReviewStatus.__members__:
                overall_st = ExecutionReviewStatus(rev.overall_status)

            reviews.append(
                Phase8ExecutionReview(
                    id=rev.id,
                    strategic_plan_id=rev.plan_id,
                    review_period=rev.period,
                    review_date=rev.review_date,
                    overall_status=overall_st,
                    progress_summary=rev.progress_summary,
                    objective_statuses=rev.objective_statuses or {},
                    initiative_statuses=rev.initiative_statuses or {},
                    milestone_statuses=rev.milestone_statuses or {},
                    metric_variances=variances,
                    diagnostic_signals=rev.diagnostic_signals or [],
                    risks=rev.risks or [],
                    corrective_actions=actions,
                    assumptions=rev.assumptions or [],
                    evidence_ids=rev.evidence_ids or [],
                    confidence=rev.confidence or 1.0,
                    created_at=rev.created_at,
                )
            )

        plan_st = ExecutionPlanStatus.DRAFT
        if model.status in ExecutionPlanStatus.__members__:
            plan_st = ExecutionPlanStatus(model.status)

        # Build ownership summary
        ownership_map: Dict[str, List[str]] = {}
        for obj in objectives:
            if obj.owner_unit_id:
                ownership_map.setdefault(obj.owner_unit_id, []).append(f"Objective: {obj.title}")
            for init in obj.initiatives:
                if init.owner_unit_id:
                    ownership_map.setdefault(init.owner_unit_id, []).append(f"Initiative: {init.title}")

        return ExecutionStrategicPlan(
            id=model.id,
            institution_id=model.institution_id,
            institution_name=model.institution_name,
            title=model.title,
            horizon_start_year=model.horizon_start_year,
            horizon_end_year=model.horizon_end_year,
            source_analysis_ids=model.source_analysis_ids or [],
            selected_option_ids=model.selected_option_ids or [],
            objectives=objectives,
            ownership_summary=ownership_map,
            assumptions=model.assumptions or [],
            vision_statement=model.vision_statement,
            mission_statement=model.mission_statement,
            existing_commitments=model.existing_commitments,
            review_period=model.review_period or "ANNUAL",
            decision_support_disclaimer=model.decision_support_disclaimer or LEADERSHIP_DECISION_SUPPORT_DISCLAIMER,
            status=plan_st,
            engine_version=model.engine_version or "1.0.0",
            previous_version_id=model.previous_version_id,
            created_at=model.created_at,
            updated_at=model.updated_at,
            execution_reviews=reviews,
            strategic_options=[
                {
                    "id": opt.id,
                    "title": opt.title,
                    "rationale": opt.rationale,
                    "resource_intensity": opt.resource_intensity,
                    "estimated_cost": opt.estimated_cost,
                    "risk_level": opt.risk_level,
                }
                for opt in model.strategic_options
            ],
            scenarios=[
                {
                    "id": scn.id,
                    "name": scn.name,
                    "description": scn.description,
                    "assumptions": scn.assumptions,
                    "projected_outcome": scn.projected_outcome,
                }
                for scn in model.scenarios
            ],
        )


    def create_execution_plan(self, plan: ExecutionStrategicPlan) -> ExecutionStrategicPlan:
        """Persist a Phase 8 execution plan with targets and initiatives."""
        plan_id = plan.id or str(uuid.uuid4())
        model = StrategicPlanModel(
            id=plan_id,
            institution_id=plan.institution_id,
            title=plan.title,
            institution_name=plan.institution_name,
            horizon_start_year=plan.horizon_start_year,
            horizon_end_year=plan.horizon_end_year,
            review_period="ANNUAL",
            status=plan.status.value,
            source_analysis_ids=plan.source_analysis_ids,
            selected_option_ids=plan.selected_option_ids,
            assumptions=plan.assumptions,
            decision_support_disclaimer=plan.decision_support_disclaimer,
            engine_version=plan.engine_version,
            previous_version_id=plan.previous_version_id,
        )

        for obj in plan.objectives:
            obj_id = obj.id or str(uuid.uuid4())
            primary_target = obj.targets[0] if obj.targets else None
            obj_model = PlanObjectiveModel(
                id=obj_id,
                plan_id=plan_id,
                title=obj.title,
                description=obj.description,
                target_metric=primary_target.metric_key if primary_target else (obj.title or "Target"),
                metric_key=primary_target.metric_key if primary_target else None,
                target_period=primary_target.target_period if primary_target else None,
                baseline_value=primary_target.baseline_value if primary_target else None,
                target_value=primary_target.target_value if primary_target else None,
                weight=1.0,
                owner=obj.owner_unit_id,
                source_option_ids=obj.source_option_ids,
                strategic_issue_ids=obj.strategic_issue_ids,
                related_metrics=obj.related_metrics,
                status=obj.status.value,
                priority=obj.priority,
                owner_unit_id=obj.owner_unit_id,
                assumptions=obj.assumptions,
                confidence=obj.confidence,
            )

            for tgt in obj.targets:
                tgt_id = tgt.id or str(uuid.uuid4())
                obj_model.targets.append(
                    StrategicTargetModel(
                        id=tgt_id,
                        objective_id=obj_id,
                        metric_key=tgt.metric_key,
                        metric_definition_id=tgt.metric_definition_id,
                        baseline_value=tgt.baseline_value,
                        baseline_period=tgt.baseline_period,
                        target_value=tgt.target_value,
                        target_period=tgt.target_period,
                        direction=tgt.direction.value,
                        unit=tgt.unit,
                        measurement_frequency=tgt.measurement_frequency,
                        evidence_ids=tgt.evidence_ids,
                        confidence=tgt.confidence,
                        assumptions=tgt.assumptions,
                        status=tgt.status.value,
                        gap=tgt.gap,
                        gap_unit_label=tgt.gap_unit_label,
                        target_provenance=tgt.target_provenance,
                    )
                )

            for init in obj.initiatives:
                init_id = init.id or str(uuid.uuid4())
                init_model = PlanInitiativeModel(
                    id=init_id,
                    objective_id=obj_id,
                    title=init.title,
                    description=init.description,
                    owner=init.owner_unit_id,
                    status=init.status.value,
                    owner_unit_id=init.owner_unit_id,
                    supporting_units=init.supporting_units,
                    source_option_ids=init.source_option_ids,
                    dependencies=init.dependencies,
                    resource_requirement=init.resource_requirement.value,
                    implementation_risk=init.implementation_risk,
                    start_period=init.start_period,
                    end_period=init.end_period,
                    success_criteria=init.success_criteria,
                    evidence_ids=init.evidence_ids,
                )

                for m in init.milestones:
                    m_id = m.id or str(uuid.uuid4())
                    init_model.milestones.append(
                        InitiativeMilestoneModel(
                            id=m_id,
                            initiative_id=init_id,
                            title=m.title,
                            description=m.description,
                            due_period=m.due_period,
                            status=m.status.value,
                            completion_percentage=m.completion_percentage,
                            evidence_ids=m.evidence_ids,
                            target_date=m.target_date,
                            completion_date=m.completion_date,
                        )
                    )

                obj_model.initiatives.append(init_model)

            model.objectives.append(obj_model)

        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return self._execution_model_to_domain(model)

    def get_execution_plan(self, plan_id: str) -> Optional[ExecutionStrategicPlan]:
        """Retrieve a Phase 8 execution plan by ID."""
        stmt = select(StrategicPlanModel).where(StrategicPlanModel.id == plan_id)
        model = self.session.execute(stmt).scalar_one_or_none()
        if not model:
            return None
        return self._execution_model_to_domain(model)

    def list_execution_plans(
        self,
        institution_id: Optional[str] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> List[ExecutionStrategicPlan]:
        """List Phase 8 execution plans with pagination and filtering."""
        stmt = select(StrategicPlanModel)
        if institution_id:
            stmt = stmt.where(StrategicPlanModel.institution_id == institution_id)
        if status:
            stmt = stmt.where(StrategicPlanModel.status == status)
        stmt = stmt.order_by(StrategicPlanModel.created_at.desc()).offset(skip).limit(limit)

        models = self.session.execute(stmt).scalars().all()
        return [self._execution_model_to_domain(m) for m in models]

    def add_phase8_execution_review(
        self, plan_id: str, review: Phase8ExecutionReview
    ) -> Phase8ExecutionReview:
        """Add a Phase 8 deterministic execution review to a strategic plan."""
        stmt = select(StrategicPlanModel).where(StrategicPlanModel.id == plan_id)
        model = self.session.execute(stmt).scalar_one_or_none()
        if not model:
            raise ValueError(f"Plan with id {plan_id} does not exist.")

        rev_id = review.id or str(uuid.uuid4())
        rev_model = ExecutionReviewModel(
            id=rev_id,
            plan_id=plan_id,
            period=review.review_period,
            review_date=review.review_date,
            progress_summary=review.progress_summary,
            variance_notes=None,
            recommendations=None,
            overall_status=review.overall_status.value,
            objective_statuses=review.objective_statuses,
            initiative_statuses=review.initiative_statuses,
            milestone_statuses=review.milestone_statuses,
            metric_variances=[
                {
                    "metric_key": v.metric_key,
                    "metric_definition_id": v.metric_definition_id,
                    "baseline_value": v.baseline_value,
                    "target_value": v.target_value,
                    "observed_value": v.observed_value,
                    "observed_period": v.observed_period,
                    "absolute_variance": v.absolute_variance,
                    "relative_variance": v.relative_variance,
                    "unit": v.unit,
                    "is_percentage": v.is_percentage,
                    "variance_notation": v.variance_notation,
                    "direction": v.direction.value,
                    "status": v.status.value,
                    "notes": v.notes,
                }
                for v in review.metric_variances
            ],
            diagnostic_signals=review.diagnostic_signals,
            risks=review.risks,
            corrective_actions=[
                {
                    "id": c.id,
                    "objective_id": c.objective_id,
                    "initiative_id": c.initiative_id,
                    "signal_type": c.signal_type.value if hasattr(c.signal_type, "value") else str(c.signal_type),
                    "title": c.title,
                    "description": c.description,
                    "suggested_action": c.suggested_action,
                    "rationale": c.rationale,
                    "requires_leadership_approval": c.requires_leadership_approval,
                }
                for c in review.corrective_actions
            ],
            assumptions=review.assumptions,
            evidence_ids=review.evidence_ids,
            confidence=review.confidence,
        )
        self.session.add(rev_model)
        self.session.commit()
        self.session.refresh(rev_model)

        review.id = rev_model.id
        review.created_at = rev_model.created_at
        return review

    def update_execution_plan_status(
        self, plan_id: str, status: ExecutionPlanStatus, notes: Optional[str] = None
    ) -> Optional[ExecutionStrategicPlan]:
        """Update status of an execution plan."""
        stmt = select(StrategicPlanModel).where(StrategicPlanModel.id == plan_id)
        model = self.session.execute(stmt).scalar_one_or_none()
        if not model:
            return None
        model.status = status.value
        self.session.commit()
        self.session.refresh(model)
        return self._execution_model_to_domain(model)

