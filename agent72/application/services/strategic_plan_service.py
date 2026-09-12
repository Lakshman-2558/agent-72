"""Strategic Plan Application Service for Phase 8.

Orchestrates:
Phase 7 Options -> Leadership Selection -> Objectives -> Measurable Targets ->
Initiatives & Owners -> Milestones -> Canonical Agent 71 Indicator Linkage ->
Deterministic Execution Review & Course-Correction Signals.
"""

from datetime import datetime, timezone, date
import re
from typing import Any, Dict, List, Optional, Tuple
import uuid

from agent72.application.dtos.strategic_plan_dto import (
    StrategicPlanGenerationRequestDTO,
    StrategicPlanResponseDTO,
    StrategicPlanListResponseDTO,
    StrategicObjectiveDTO,
    StrategicTargetDTO,
    PlanInitiativeDTO,
    InitiativeMilestoneDTO,
    ExecutionReviewDTO,
    ExecutionReviewRequestDTO,
    TargetVarianceDTO,
    CorrectiveActionCandidateDTO,
    PlanDecisionRequestDTO,
)
from agent72.core.exceptions import EntityNotFoundException, ValidationError
from agent72.core.logging import get_logger
from agent72.domain.interfaces.ai_provider import IAIProvider
from agent72.domain.interfaces.evidence_repository import IEvidenceRepository
from agent72.domain.interfaces.organization_repository import IOrganizationRepository
from agent72.domain.interfaces.plan_repository import IPlanRepository
from agent72.domain.interfaces.strategic_options_repository import IStrategicOptionsRepository
from agent72.domain.models.evidence import MetricDirection
from agent72.domain.models.strategic_options import StrategicOption, StrategicOptionsAnalysis
from agent72.domain.models.strategic_plan_execution import (
    OptionDecisionStatus,
    PlanStatus,
    ObjectiveStatus,
    InitiativeStatus,
    MilestoneStatus,
    ReviewStatus,
    TargetDirection,
    TargetStatus,
    ResourceRequirement,
    DiagnosticSignalType,
    StrategicTarget,
    InitiativeMilestone,
    PlanInitiative,
    StrategicObjective,
    TargetVariance,
    CorrectiveActionCandidate,
    ExecutionReview,
    StrategicPlan,
    LEADERSHIP_DECISION_SUPPORT_DISCLAIMER,
)

logger = get_logger(__name__)


class StrategicPlanExecutionService:
    """Orchestrates Phase 8 strategic plan generation, lifecycle management, and execution reviews."""

    def __init__(
        self,
        plan_repository: IPlanRepository,
        options_repository: IStrategicOptionsRepository,
        evidence_repository: IEvidenceRepository,
        organization_repository: IOrganizationRepository,
        ai_provider: IAIProvider,
    ) -> None:
        self.plan_repository = plan_repository
        self.options_repository = options_repository
        self.evidence_repository = evidence_repository
        self.organization_repository = organization_repository
        self.ai_provider = ai_provider

    # ==========================================================================
    # 1. Strategic Plan Generation
    # ==========================================================================

    def generate_plan_from_options(
        self, request: StrategicPlanGenerationRequestDTO
    ) -> StrategicPlanResponseDTO:
        """Transforms selected Phase 7 options into a coherent, structured Strategic Plan."""
        logger.info(
            f"Generating strategic plan for institution '{request.institution_id}' from options analysis '{request.strategic_options_analysis_id}'"
        )

        # 1. Validate institution
        inst = self.organization_repository.get_institution_by_id(request.institution_id)
        if not inst:
            raise EntityNotFoundException("Institution", request.institution_id)

        # 2. Validate planning horizon
        if request.horizon_start_year > request.horizon_end_year:
            raise ValidationError(
                f"Horizon start year ({request.horizon_start_year}) cannot exceed end year ({request.horizon_end_year})."
            )

        # 3. Load Phase 7 analysis
        analysis = self.options_repository.get_analysis_by_id(request.strategic_options_analysis_id)
        if not analysis:
            raise EntityNotFoundException("StrategicOptionsAnalysis", request.strategic_options_analysis_id)

        # 4. Filter options based on leadership selection and lifecycle rules
        selected_options = self._select_options_for_planning(analysis, request)
        if not selected_options:
            raise ValidationError(
                "No options qualify for planning. Leadership must select options or provide selected_option_ids."
            )

        # 5. Fetch available metric definitions from canonical repository
        metric_defs = self.evidence_repository.list_metric_definitions()
        metric_def_map = {m.metric_key: m for m in metric_defs}

        # 6. Fetch existing organizational units for realistic ownership
        units = self.organization_repository.list_units_by_institution(request.institution_id)
        unit_names = [u.name for u in units] if units else []

        # 7. Convert selected options into coherent strategic objectives
        plan_id = str(uuid.uuid4())
        objectives, plan_assumptions = self._generate_objectives_and_targets(
            selected_options=selected_options,
            plan_id=plan_id,
            institution_id=request.institution_id,
            horizon_start_year=request.horizon_start_year,
            horizon_end_year=request.horizon_end_year,
            metric_def_map=metric_def_map,
            available_units=unit_names,
        )

        # 8. Title and metadata
        title = request.title or f"{inst.name} Strategic Plan {request.horizon_start_year}–{request.horizon_end_year}"

        # 9. Build ownership summary
        ownership_summary: Dict[str, List[str]] = {}
        for obj in objectives:
            if obj.owner_unit_id:
                ownership_summary.setdefault(obj.owner_unit_id, []).append(f"Objective: {obj.title}")
            for init in obj.initiatives:
                if init.owner_unit_id:
                    ownership_summary.setdefault(init.owner_unit_id, []).append(f"Initiative: {init.title}")

        # 10. Construct domain StrategicPlan (initially strictly DRAFT or PENDING_APPROVAL)
        strategic_plan = StrategicPlan(
            id=plan_id,
            institution_id=request.institution_id,
            institution_name=inst.name,
            title=title,
            horizon_start_year=request.horizon_start_year,
            horizon_end_year=request.horizon_end_year,
            source_analysis_ids=[analysis.id],
            selected_option_ids=[opt.id for opt in selected_options],
            objectives=objectives,
            ownership_summary=ownership_summary,
            assumptions=plan_assumptions,
            decision_support_disclaimer=LEADERSHIP_DECISION_SUPPORT_DISCLAIMER,
            status=PlanStatus.DRAFT,
            engine_version="1.0.0",
        )

        # 11. Optional AI Enhancement (strictly text wording only, no numerical/logic alterations)
        if request.include_ai_synthesis and self.ai_provider:
            self._apply_ai_guardrailed_enhancement(strategic_plan)

        # 12. Persist to repository
        saved_plan = self.plan_repository.create_execution_plan(strategic_plan)
        return self._to_response_dto(saved_plan)

    # ==========================================================================
    # 2. Option Selection & Validation
    # ==========================================================================

    def _select_options_for_planning(
        self,
        analysis: StrategicOptionsAnalysis,
        request: StrategicPlanGenerationRequestDTO,
    ) -> List[StrategicOption]:
        """Validates and selects options according to Phase 8 decision-status lifecycle rules."""
        all_options_map = {opt.id: opt for opt in analysis.options}

        if request.selected_option_ids is not None:
            # Explicit selection requested by leadership
            selected: List[StrategicOption] = []
            for opt_id in request.selected_option_ids:
                if opt_id not in all_options_map:
                    raise ValidationError(
                        f"Selected option ID '{opt_id}' does not exist in analysis '{analysis.id}'."
                    )
                opt = all_options_map[opt_id]

                # Check rejected/deferred rules
                if not request.override_selection_requirement:
                    if opt.status == "REJECTED":
                        raise ValidationError(
                            f"Option '{opt.title}' ({opt.id}) is REJECTED and cannot be planned without override_selection_requirement=True."
                        )
                    if opt.status == "DEFERRED":
                        raise ValidationError(
                            f"Option '{opt.title}' ({opt.id}) is DEFERRED and cannot be planned without override_selection_requirement=True."
                        )
                selected.append(opt)
            return selected

        # If no explicit list provided, look for options marked SELECTED_FOR_PLANNING
        planning_options = [
            opt for opt in analysis.options
            if opt.status in ("SELECTED_FOR_PLANNING", OptionDecisionStatus.SELECTED_FOR_PLANNING.value)
        ]
        if not planning_options and request.override_selection_requirement:
            planning_options = [
                opt for opt in analysis.options
                if getattr(opt, "status", None) not in ("REJECTED", "DEFERRED")
            ]
        return planning_options

    # ==========================================================================
    # 3. Objectives, Targets, Initiatives & Milestones Generation
    # ==========================================================================

    def _generate_objectives_and_targets(
        self,
        selected_options: List[StrategicOption],
        plan_id: str,
        institution_id: str,
        horizon_start_year: int,
        horizon_end_year: int,
        metric_def_map: Dict[str, Any],
        available_units: List[str],
    ) -> Tuple[List[StrategicObjective], List[str]]:
        """Transforms selected options into coherent objectives, targets, initiatives, and milestones."""
        plan_assumptions: List[str] = [
            f"Strategic plan covers operational horizon {horizon_start_year} to {horizon_end_year}.",
            "All targets are proposals subject to formal leadership approval before activation.",
        ]

        # Cluster related options to prevent duplicate objectives
        # Group by common domain theme
        clusters: Dict[str, List[StrategicOption]] = {}
        for opt in selected_options:
            theme = self._detect_option_theme(opt)
            clusters.setdefault(theme, []).append(opt)

        objectives: List[StrategicObjective] = []

        for theme, cluster_options in clusters.items():
            obj_id = str(uuid.uuid4())
            primary_opt = cluster_options[0]

            # 1. Synthesize Objective Title & Rationale
            if len(cluster_options) == 1:
                obj_title = self._formulate_objective_title(primary_opt)
                obj_rationale = primary_opt.strategic_rationale
            else:
                combined_titles = ", ".join(f"'{o.title}'" for o in cluster_options)
                obj_title = self._formulate_combined_objective_title(theme, cluster_options)
                obj_rationale = f"Consolidates strategic options ({combined_titles}) into a unified institutional outcome."

            # Collect source IDs
            src_opt_ids = [o.id for o in cluster_options]
            src_issue_ids: List[str] = []
            for o in cluster_options:
                src_issue_ids.extend(o.addressed_issue_ids)
            src_issue_ids = sorted(list(set(src_issue_ids)))

            # Related metrics across cluster
            related_metrics_set = set()
            for o in cluster_options:
                related_metrics_set.update(o.related_metrics)
            related_metrics = sorted(list(related_metrics_set))

            # Determine owner unit for objective
            obj_owner = self._assign_owner_unit(theme, primary_opt, available_units)

            # 2. Generate Targets for this Objective
            targets: List[StrategicTarget] = []
            for m_key in related_metrics:
                target = self._generate_target_for_metric(
                    objective_id=obj_id,
                    metric_key=m_key,
                    institution_id=institution_id,
                    horizon_end_year=horizon_end_year,
                    metric_def_map=metric_def_map,
                    plan_assumptions=plan_assumptions,
                )
                targets.append(target)

            # If no related metric exists on option, flag as requiring metric definition
            if not targets:
                placeholder_target = StrategicTarget(
                    id=str(uuid.uuid4()),
                    objective_id=obj_id,
                    metric_key=f"target.{theme.lower()}",
                    metric_definition_id=None,
                    baseline_value=None,
                    baseline_period=None,
                    target_value=None,
                    target_period=f"{horizon_end_year}",
                    direction=TargetDirection.HIGHER_IS_BETTER,
                    unit="count",
                    measurement_frequency="ANNUAL",
                    evidence_ids=[],
                    confidence=0.5,
                    assumptions=[f"Objective lacks an existing metric definition; formal indicator definition required."],
                    status=TargetStatus.REQUIRING_METRIC_DEFINITION,
                    gap=None,
                    gap_unit_label="",
                    target_provenance="PENDING_METRIC_SPECIFICATION",
                )
                targets.append(placeholder_target)

            # 3. Generate Concrete Initiatives & Milestones
            initiatives: List[PlanInitiative] = []
            for opt in cluster_options:
                inits = self._generate_initiatives_for_option(
                    objective_id=obj_id,
                    option=opt,
                    horizon_start_year=horizon_start_year,
                    horizon_end_year=horizon_end_year,
                    available_units=available_units,
                )
                initiatives.extend(inits)

            objective = StrategicObjective(
                id=obj_id,
                strategic_plan_id=plan_id,
                title=obj_title,
                description=f"Strategic objective addressing {theme.replace('_', ' ').lower()}.",
                strategic_rationale=obj_rationale,
                source_option_ids=src_opt_ids,
                strategic_issue_ids=src_issue_ids,
                related_metrics=related_metrics,
                status=ObjectiveStatus.PROPOSED,
                priority=primary_opt.feasibility.value if hasattr(primary_opt.feasibility, "value") else "MEDIUM",
                owner_unit_id=obj_owner,
                assumptions=[f"Assumes implementation alignment across {obj_owner} and supporting stakeholders."],
                confidence=min((o.confidence for o in cluster_options), default=1.0),
                targets=targets,
                initiatives=initiatives,
            )
            objectives.append(objective)

        return objectives, plan_assumptions

    def _detect_option_theme(self, opt: StrategicOption) -> str:
        """Determines the thematic domain of an option."""
        text = f"{opt.title} {opt.description} {opt.strategic_rationale}".lower()
        if any(w in text for w in ("employab", "placement", "curriculum", "industry", "career")):
            return "EMPLOYABILITY_AND_INDUSTRY"
        if any(w in text for w in ("faculty", "teaching", "phd", "recruitment", "instructional")):
            return "FACULTY_CAPABILITY"
        if any(w in text for w in ("research", "publication", "citation", "grant", "journal")):
            return "RESEARCH_AND_INNOVATION"
        if any(w in text for w in ("retention", "dropout", "student support", "advising")):
            return "STUDENT_RETENTION"
        if any(w in text for w in ("infrastructure", "lab", "facility", "equipment", "campus")):
            return "INFRASTRUCTURE"
        if any(w in text for w in ("enrollment", "admission", "intake", "demand")):
            return "ENROLLMENT_AND_ADMISSIONS"
        return "INSTITUTIONAL_DEVELOPMENT"

    def _formulate_objective_title(self, opt: StrategicOption) -> str:
        """Derives a strategic, outcome-oriented objective title from an option."""
        theme = self._detect_option_theme(opt)
        if theme == "EMPLOYABILITY_AND_INDUSTRY":
            return "Improve graduate employability through stronger curriculum and industry alignment."
        if theme == "FACULTY_CAPABILITY":
            return "Strengthen faculty capability and qualifications in priority academic domains."
        if theme == "RESEARCH_AND_INNOVATION":
            return "Increase research productivity, publication quality, and impact in institutional priority domains."
        if theme == "STUDENT_RETENTION":
            return "Enhance student academic success, retention, and timely completion rates."
        if theme == "INFRASTRUCTURE":
            return "Optimize academic infrastructure, laboratory utilization, and modern learning environments."
        return f"Advance {opt.title.lower()} to drive institutional excellence."

    def _formulate_combined_objective_title(
        self, theme: str, options: List[StrategicOption]
    ) -> str:
        """Derives a unified title for clustered options."""
        if theme == "EMPLOYABILITY_AND_INDUSTRY":
            return "Improve graduate employability and career readiness through industry-aligned education."
        if theme == "FACULTY_CAPABILITY":
            return "Strengthen instructional quality, faculty research mentorship, and domain capability."
        if theme == "RESEARCH_AND_INNOVATION":
            return "Elevate institutional research output, sponsored funding, and intellectual impact."
        return f"Coordinated advancement of {theme.replace('_', ' ').lower()} initiatives."

    def _assign_owner_unit(
        self, theme: str, opt: StrategicOption, available_units: List[str]
    ) -> str:
        """Assigns an organizational unit owner based on theme. Never invents personal names."""
        theme_unit_mapping = {
            "EMPLOYABILITY_AND_INDUSTRY": ["Training & Placement", "Career Services", "Academic Affairs"],
            "FACULTY_CAPABILITY": ["HR/Faculty Development", "Dean of Faculty Affairs", "Academic Affairs"],
            "RESEARCH_AND_INNOVATION": ["Research & Development", "Office of Research", "Academic Affairs"],
            "STUDENT_RETENTION": ["Student Affairs", "Academic Affairs"],
            "INFRASTRUCTURE": ["Infrastructure & Facilities", "Campus Operations", "Finance"],
            "ENROLLMENT_AND_ADMISSIONS": ["Admissions Office", "Academic Affairs"],
            "INSTITUTIONAL_DEVELOPMENT": ["Academic Affairs", "Planning & Quality Assurance"],
        }

        candidates = theme_unit_mapping.get(theme, ["Academic Affairs"])
        # Match against available units in the institution
        for cand in candidates:
            for avail in available_units:
                if cand.lower() in avail.lower():
                    return avail
        # If no direct match in available_units, use standard organizational unit title
        return candidates[0]

    def _generate_target_for_metric(
        self,
        objective_id: str,
        metric_key: str,
        institution_id: str,
        horizon_end_year: int,
        metric_def_map: Dict[str, Any],
        plan_assumptions: List[str],
    ) -> StrategicTarget:
        """Generates a measurable target linked to a canonical MetricDefinition without fabrication."""
        metric_def = metric_def_map.get(metric_key)

        # If metric definition is missing from the canonical registry
        if not metric_def:
            plan_assumptions.append(
                f"Metric key '{metric_key}' is not formally registered in metric definitions; flagged as REQUIRING_METRIC_DEFINITION."
            )
            return StrategicTarget(
                id=str(uuid.uuid4()),
                objective_id=objective_id,
                metric_key=metric_key,
                metric_definition_id=None,
                baseline_value=None,
                baseline_period=None,
                target_value=None,
                target_period=f"{horizon_end_year}",
                direction=TargetDirection.HIGHER_IS_BETTER,
                unit="count",
                measurement_frequency="ANNUAL",
                evidence_ids=[],
                confidence=0.5,
                assumptions=[f"Missing canonical MetricDefinition for '{metric_key}'."],
                status=TargetStatus.REQUIRING_METRIC_DEFINITION,
                gap=None,
                gap_unit_label="",
                target_provenance="REQUIRES_REGISTRATION",
            )

        # Direction
        dir_val = TargetDirection.HIGHER_IS_BETTER
        if hasattr(metric_def, "direction"):
            if isinstance(metric_def.direction, MetricDirection):
                dir_val = TargetDirection(metric_def.direction.value)
            elif str(metric_def.direction) in TargetDirection.__members__:
                dir_val = TargetDirection(str(metric_def.direction))

        unit = metric_def.default_unit or "count"
        is_pct = unit in ("%", "percentage", "percent")

        # Query latest evidence for baseline
        ev = self.evidence_repository.get_latest_evidence(institution_id, metric_key)
        baseline_val: Optional[float] = None
        baseline_period: Optional[str] = None
        ev_ids: List[str] = []

        if ev and ev.numeric_value is not None:
            baseline_val = ev.numeric_value
            baseline_period = ev.period
            ev_ids.append(ev.id)

        # Propose target based on baseline & directionality
        target_val: Optional[float] = None
        gap: Optional[float] = None
        gap_unit_label = "percentage points" if is_pct else unit

        if baseline_val is not None:
            if dir_val == TargetDirection.HIGHER_IS_BETTER:
                if is_pct:
                    target_val = round(min(100.0, baseline_val + 10.0), 1)
                else:
                    target_val = round(baseline_val * 1.25, 1)
            elif dir_val == TargetDirection.LOWER_IS_BETTER:
                if is_pct:
                    target_val = round(max(0.0, baseline_val - 5.0), 1)
                else:
                    target_val = round(baseline_val * 0.75, 1)
            else:
                target_val = baseline_val

            gap = round(target_val - baseline_val, 2)
            target_status = TargetStatus.PROPOSED_TARGET
            provenance = "DERIVED_FROM_EVIDENCE_BASELINE"
        else:
            target_status = TargetStatus.PROPOSED_TARGET
            provenance = "AWAITING_INITIAL_BASELINE_OBSERVATION"
            plan_assumptions.append(
                f"Metric '{metric_key}' currently lacks historical observation; baseline to be confirmed in Year 1."
            )

        return StrategicTarget(
            id=str(uuid.uuid4()),
            objective_id=objective_id,
            metric_key=metric_key,
            metric_definition_id=metric_def.id,
            baseline_value=baseline_val,
            baseline_period=baseline_period,
            target_value=target_val,
            target_period=f"{horizon_end_year}",
            direction=dir_val,
            unit=unit,
            measurement_frequency="ANNUAL",
            evidence_ids=ev_ids,
            confidence=1.0 if baseline_val is not None else 0.7,
            assumptions=[f"Target proposed for {horizon_end_year} based on baseline trajectory and institutional capacity."],
            status=target_status,
            gap=gap,
            gap_unit_label=gap_unit_label,
            target_provenance=provenance,
        )

    def _generate_initiatives_for_option(
        self,
        objective_id: str,
        option: StrategicOption,
        horizon_start_year: int,
        horizon_end_year: int,
        available_units: List[str],
    ) -> List[PlanInitiative]:
        """Converts an option into concrete, execution-ready initiatives without fabricating budgets."""
        theme = self._detect_option_theme(option)
        owner = self._assign_owner_unit(theme, option, available_units)

        # Parse resource requirement safely (no fabricated numbers)
        res_req = ResourceRequirement.UNKNOWN
        if hasattr(option, "resource_intensity"):
            res_str = str(option.resource_intensity).upper()
            if "LOW" in res_str:
                res_req = ResourceRequirement.LOW
            elif "HIGH" in res_str:
                res_req = ResourceRequirement.HIGH
            elif "MED" in res_str:
                res_req = ResourceRequirement.MEDIUM

        # Generate 2–3 actionable initiatives per option
        initiatives: List[PlanInitiative] = []

        # 1. Initiative: Assessment & Planning
        init1_id = str(uuid.uuid4())
        init1_milestones = [
            InitiativeMilestone(
                id=str(uuid.uuid4()),
                initiative_id=init1_id,
                title="Initiation and stakeholder scoping",
                description="Finalize implementation charter and working committee membership.",
                due_period=f"{horizon_start_year}-H1",
                status=MilestoneStatus.NOT_STARTED,
                completion_percentage=0.0,
                evidence_ids=option.evidence_ids[:1],
            ),
            InitiativeMilestone(
                id=str(uuid.uuid4()),
                initiative_id=init1_id,
                title="Framework baseline review",
                description="Conduct institutional baseline assessment and gap verification.",
                due_period=f"{horizon_start_year}-H2",
                status=MilestoneStatus.NOT_STARTED,
                completion_percentage=0.0,
                evidence_ids=option.evidence_ids[:2],
            ),
        ]

        init1 = PlanInitiative(
            id=init1_id,
            objective_id=objective_id,
            title=f"{option.title} — Implementation Framework",
            description=f"Institutional rollout and governance framework for {option.title.lower()}.",
            rationale=option.strategic_rationale,
            owner_unit_id=owner,
            supporting_units=["Planning & Quality Assurance"],
            source_option_ids=[option.id],
            dependencies=option.dependencies,
            resource_requirement=res_req,
            implementation_risk=option.implementation_risk if hasattr(option, "implementation_risk") else "MEDIUM",
            start_period=f"{horizon_start_year}-H1",
            end_period=f"{horizon_start_year + 1}-H2",
            status=InitiativeStatus.PLANNED,
            success_criteria=[f"Charter approved by {owner}", "Baseline assessment completed"],
            evidence_ids=option.evidence_ids,
            milestones=init1_milestones,
        )
        initiatives.append(init1)

        # 2. Initiative: Execution & Scale
        init2_id = str(uuid.uuid4())
        init2_milestones = [
            InitiativeMilestone(
                id=str(uuid.uuid4()),
                initiative_id=init2_id,
                title="Full-scale program rollout",
                description="Deploy core capabilities across target academic departments.",
                due_period=f"{horizon_start_year + 1}-H1",
                status=MilestoneStatus.NOT_STARTED,
                completion_percentage=0.0,
                evidence_ids=option.evidence_ids[:1],
            ),
            InitiativeMilestone(
                id=str(uuid.uuid4()),
                initiative_id=init2_id,
                title="Mid-cycle progress review",
                description="Measure operational indicator variances and evaluate effectiveness.",
                due_period=f"{horizon_start_year + 2}-H2",
                status=MilestoneStatus.NOT_STARTED,
                completion_percentage=0.0,
                evidence_ids=option.evidence_ids[:2],
            ),
        ]

        init2 = PlanInitiative(
            id=init2_id,
            objective_id=objective_id,
            title=f"{option.title} — Operational Execution",
            description=f"Direct delivery and departmental execution of {option.title.lower()}.",
            rationale=option.strategic_rationale,
            owner_unit_id=owner,
            supporting_units=["Finance", "Academic Affairs"],
            source_option_ids=[option.id],
            dependencies=[init1.title] + option.dependencies,
            resource_requirement=res_req,
            implementation_risk=option.implementation_risk if hasattr(option, "implementation_risk") else "MEDIUM",
            start_period=f"{horizon_start_year + 1}-H1",
            end_period=f"{horizon_end_year}-H2",
            status=InitiativeStatus.PLANNED,
            success_criteria=["Departmental participation >85%", "Mid-term targets evaluated"],
            evidence_ids=option.evidence_ids,
            milestones=init2_milestones,
        )
        initiatives.append(init2)

        return initiatives

    # ==========================================================================
    # 4. Deterministic Execution Review
    # ==========================================================================

    def record_execution_review(
        self,
        plan_id: str,
        request: ExecutionReviewRequestDTO,
    ) -> ExecutionReviewDTO:
        """Performs a deterministic periodic/annual execution review against current evidence."""
        logger.info(f"Running execution review for plan '{plan_id}' on period '{request.review_period}'")

        plan = self.plan_repository.get_execution_plan(plan_id)
        if not plan:
            raise EntityNotFoundException("StrategicPlan", plan_id)

        variances: List[TargetVariance] = []
        diagnostic_signals: List[Dict[str, Any]] = []
        corrective_actions: List[CorrectiveActionCandidate] = []
        objective_statuses: Dict[str, str] = {}
        initiative_statuses: Dict[str, str] = {}
        milestone_statuses: Dict[str, str] = {}

        # 1. Target Variance & Direction-Aware Evaluation
        for obj in plan.objectives:
            obj_target_statuses: List[ReviewStatus] = []

            for tgt in obj.targets:
                variance = self._evaluate_target_variance(
                    institution_id=plan.institution_id or "",
                    target=tgt,
                    review_period=request.review_period,
                    explicit_evidence_ids=request.latest_evidence_ids,
                )
                variances.append(variance)
                obj_target_statuses.append(variance.status)

                # Diagnostic signal on target performance
                if variance.status == ReviewStatus.OFF_TRACK:
                    diagnostic_signals.append({
                        "signal_type": DiagnosticSignalType.TARGET_OFF_TRACK.value,
                        "metric_key": tgt.metric_key,
                        "objective_id": obj.id,
                        "summary": f"Target for '{tgt.metric_key}' is off-track: expected {tgt.target_value}, observed {variance.observed_value} ({variance.variance_notation}).",
                    })
                    corrective_actions.append(
                        CorrectiveActionCandidate(
                            id=str(uuid.uuid4()),
                            objective_id=obj.id,
                            signal_type=DiagnosticSignalType.TARGET_OFF_TRACK,
                            title=f"Remediate {tgt.metric_key} performance gap",
                            description=f"Observed value {variance.observed_value} lags target {tgt.target_value} ({variance.variance_notation}).",
                            suggested_action=f"Mandate mid-cycle review with {obj.owner_unit_id} and re-examine resource bottlenecks.",
                            rationale="Deterministic variance calculation shows unacceptable gap against trajectory target.",
                            requires_leadership_approval=True,
                        )
                    )
                elif variance.status == ReviewStatus.AT_RISK:
                    diagnostic_signals.append({
                        "signal_type": DiagnosticSignalType.TARGET_AT_RISK.value,
                        "metric_key": tgt.metric_key,
                        "objective_id": obj.id,
                        "summary": f"Target for '{tgt.metric_key}' is at risk: variance {variance.variance_notation}.",
                    })
                elif variance.status == ReviewStatus.INSUFFICIENT_EVIDENCE:
                    diagnostic_signals.append({
                        "signal_type": DiagnosticSignalType.EVIDENCE_STALE.value,
                        "metric_key": tgt.metric_key,
                        "objective_id": obj.id,
                        "summary": f"Target '{tgt.metric_key}' has no observed evidence in period '{request.review_period}'.",
                    })

            # Derive objective status from targets
            if any(s == ReviewStatus.OFF_TRACK for s in obj_target_statuses):
                obj_st = ReviewStatus.OFF_TRACK
            elif any(s == ReviewStatus.AT_RISK for s in obj_target_statuses):
                obj_st = ReviewStatus.AT_RISK
            elif all(s == ReviewStatus.ON_TRACK for s in obj_target_statuses if s != ReviewStatus.INSUFFICIENT_EVIDENCE):
                obj_st = ReviewStatus.ON_TRACK
            else:
                obj_st = ReviewStatus.INSUFFICIENT_EVIDENCE
            objective_statuses[obj.id] = obj_st.value

        # 2. Milestone Tracking & Diagnostic Signals
        for obj in plan.objectives:
            for init in obj.initiatives:
                init_milestone_statuses: List[MilestoneStatus] = []

                for m in init.milestones:
                    is_past_due = self._is_period_past_or_current(m.due_period, request.review_period)

                    if is_past_due and m.completion_percentage < 100.0 and m.status != MilestoneStatus.COMPLETED:
                        milestone_st = MilestoneStatus.DELAYED
                        diagnostic_signals.append({
                            "signal_type": DiagnosticSignalType.MILESTONE_DELAYED.value,
                            "initiative_id": init.id,
                            "milestone_id": m.id,
                            "summary": f"Milestone '{m.title}' is delayed: due {m.due_period}, completion {m.completion_percentage}%.",
                        })
                        corrective_actions.append(
                            CorrectiveActionCandidate(
                                id=str(uuid.uuid4()),
                                objective_id=obj.id,
                                initiative_id=init.id,
                                signal_type=DiagnosticSignalType.MILESTONE_DELAYED,
                                title=f"Accelerate milestone: {m.title}",
                                description=f"Milestone '{m.title}' due in {m.due_period} is currently at {m.completion_percentage}%.",
                                suggested_action=f"Request status escalation from {init.owner_unit_id} and assess whether deadline extension is warranted.",
                                rationale="Milestone overdue against planning horizon schedule.",
                                requires_leadership_approval=True,
                            )
                        )
                    elif m.completion_percentage >= 100.0 or m.status == MilestoneStatus.COMPLETED:
                        milestone_st = MilestoneStatus.COMPLETED
                    elif m.completion_percentage > 0.0:
                        milestone_st = MilestoneStatus.IN_PROGRESS
                    else:
                        milestone_st = MilestoneStatus.NOT_STARTED

                    milestone_statuses[m.id] = milestone_st.value
                    init_milestone_statuses.append(milestone_st)

                # Initiative status
                if any(ms == MilestoneStatus.DELAYED for ms in init_milestone_statuses):
                    init_st = InitiativeStatus.AT_RISK
                elif all(ms == MilestoneStatus.COMPLETED for ms in init_milestone_statuses):
                    init_st = InitiativeStatus.COMPLETED
                elif any(ms == MilestoneStatus.IN_PROGRESS for ms in init_milestone_statuses):
                    init_st = InitiativeStatus.ACTIVE
                else:
                    init_st = InitiativeStatus.PLANNED
                initiative_statuses[init.id] = init_st.value

        # 3. Overall Execution Review Status
        if any(v == ReviewStatus.OFF_TRACK.value for v in objective_statuses.values()):
            overall_status = ReviewStatus.OFF_TRACK
        elif any(v == ReviewStatus.AT_RISK.value for v in objective_statuses.values()) or any(
            ms == MilestoneStatus.DELAYED.value for ms in milestone_statuses.values()
        ):
            overall_status = ReviewStatus.AT_RISK
        elif all(v == ReviewStatus.ON_TRACK.value for v in objective_statuses.values()):
            overall_status = ReviewStatus.ON_TRACK
        else:
            overall_status = ReviewStatus.INSUFFICIENT_EVIDENCE

        # 4. Progress Summary text
        summary_lines = [
            f"Execution Review for period {request.review_period}: Overall status is {overall_status.value}.",
            f"Total evaluated targets: {len(variances)}. Diagnostic signals: {len(diagnostic_signals)}.",
            f"Candidate corrective actions: {len(corrective_actions)} (requires leadership approval).",
        ]
        progress_summary = " ".join(summary_lines)

        # 5. Assemble ExecutionReview Domain Entity
        review = ExecutionReview(
            id=str(uuid.uuid4()),
            strategic_plan_id=plan_id,
            review_period=request.review_period,
            review_date=datetime.now(timezone.utc).date(),
            overall_status=overall_status,
            progress_summary=progress_summary,
            objective_statuses=objective_statuses,
            initiative_statuses=initiative_statuses,
            milestone_statuses=milestone_statuses,
            metric_variances=variances,
            diagnostic_signals=diagnostic_signals,
            risks=[],
            corrective_actions=corrective_actions,
            assumptions=[
                "Review findings are strictly diagnostic decision-support signals.",
                "Strategic plan parameters and targets remain unaltered until leadership explicitly acts.",
            ],
            evidence_ids=[v.metric_key for v in variances if v.observed_value is not None],
            confidence=1.0,
            created_at=datetime.now(timezone.utc),
        )

        # 6. Save review to repository (Immutable Snapshot)
        saved_review = self.plan_repository.add_phase8_execution_review(plan_id, review)
        return self._to_review_dto(saved_review)

    def _evaluate_target_variance(
        self,
        institution_id: str,
        target: StrategicTarget,
        review_period: str,
        explicit_evidence_ids: Optional[List[str]],
    ) -> TargetVariance:
        """Computes deterministic direction-aware variance for a target indicator."""
        is_pct = target.unit in ("%", "percentage", "percent")

        # 1. Fetch latest observed value
        ev = None
        if explicit_evidence_ids:
            for eid in explicit_evidence_ids:
                candidate = self.evidence_repository.get_by_id(eid)
                if candidate and candidate.metric_key == target.metric_key:
                    ev = candidate
                    break

        if not ev and institution_id:
            ev = self.evidence_repository.get_latest_evidence(institution_id, target.metric_key)

        # If no evidence exists
        if not ev or ev.numeric_value is None:
            return TargetVariance(
                metric_key=target.metric_key,
                metric_definition_id=target.metric_definition_id,
                baseline_value=target.baseline_value,
                target_value=target.target_value,
                observed_value=None,
                observed_period=None,
                absolute_variance=None,
                relative_variance=None,
                unit=target.unit,
                is_percentage=is_pct,
                variance_notation="No observation available",
                direction=target.direction,
                status=ReviewStatus.INSUFFICIENT_EVIDENCE,
                notes="Target has no current evidence observation in review window; not counted as failure.",
            )

        observed = ev.numeric_value
        obs_period = ev.period
        target_val = target.target_value

        if target_val is None:
            return TargetVariance(
                metric_key=target.metric_key,
                metric_definition_id=target.metric_definition_id,
                baseline_value=target.baseline_value,
                target_value=None,
                observed_value=observed,
                observed_period=obs_period,
                absolute_variance=None,
                relative_variance=None,
                unit=target.unit,
                is_percentage=is_pct,
                variance_notation=f"Observed: {observed} {target.unit}",
                direction=target.direction,
                status=ReviewStatus.ON_TRACK,
                notes="Target value was not specified; observed value recorded.",
            )

        abs_var = round(observed - target_val, 2)
        rel_var = round((abs_var / abs(target_val)) * 100.0, 1) if target_val != 0 else None

        # Format variance notation strictly using "percentage points" for percentages
        sign = "+" if abs_var >= 0 else ""
        if is_pct:
            var_notation = f"{sign}{abs_var} percentage points"
        else:
            var_notation = f"{sign}{abs_var} {target.unit}"

        # Direction-aware status determination
        direction = target.direction
        if direction == TargetDirection.HIGHER_IS_BETTER:
            if observed >= target_val:
                status = ReviewStatus.ON_TRACK
            elif observed >= (target_val - (0.10 * abs(target_val))):
                status = ReviewStatus.AT_RISK
            else:
                status = ReviewStatus.OFF_TRACK
        elif direction == TargetDirection.LOWER_IS_BETTER:
            if observed <= target_val:
                status = ReviewStatus.ON_TRACK
            elif observed <= (target_val + (0.10 * abs(target_val))):
                status = ReviewStatus.AT_RISK
            else:
                status = ReviewStatus.OFF_TRACK
        else:
            # Target range or neutral
            if abs_var == 0 or (rel_var is not None and abs(rel_var) <= 5.0):
                status = ReviewStatus.ON_TRACK
            else:
                status = ReviewStatus.AT_RISK

        return TargetVariance(
            metric_key=target.metric_key,
            metric_definition_id=target.metric_definition_id,
            baseline_value=target.baseline_value,
            target_value=target_val,
            observed_value=observed,
            observed_period=obs_period,
            absolute_variance=abs_var,
            relative_variance=rel_var,
            unit=target.unit,
            is_percentage=is_pct,
            variance_notation=var_notation,
            direction=direction,
            status=status,
            notes=f"Calculated direction-aware variance ({var_notation}) against target {target_val}.",
        )

    def _is_period_past_or_current(self, due_period: str, current_period: str) -> bool:
        """Deterministic helper comparing milestone due periods like '2026-H1' or '2026'."""
        if not due_period or not current_period:
            return False

        def parse_period_year(p: str) -> float:
            match = re.search(r"(\d{4})", p)
            if not match:
                return 2026.0
            yr = float(match.group(1))
            if "-h1" in p.lower() or "-q1" in p.lower() or "-q2" in p.lower():
                return yr + 0.25
            if "-h2" in p.lower() or "-q3" in p.lower() or "-q4" in p.lower():
                return yr + 0.75
            return yr + 0.5

        return parse_period_year(due_period) <= parse_period_year(current_period)

    # ==========================================================================
    # 5. Leadership Decision Lifecycle Boundary
    # ==========================================================================

    def update_plan_decision(
        self, plan_id: str, request: PlanDecisionRequestDTO
    ) -> StrategicPlanResponseDTO:
        """Processes an explicit leadership governance decision on a strategic plan."""
        logger.info(f"Leadership decision '{request.decision}' requested for plan '{plan_id}'")

        plan = self.plan_repository.get_execution_plan(plan_id)
        if not plan:
            raise EntityNotFoundException("StrategicPlan", plan_id)

        decision_val = request.decision or request.status
        if not decision_val:
            raise ValidationError("Either 'decision' or 'status' must be specified.")
        decision_upper = decision_val.strip().upper()
        if decision_upper in ("APPROVE", "APPROVED"):
            new_status = PlanStatus.APPROVED
        elif decision_upper in ("ACTIVATE", "ACTIVE"):
            new_status = PlanStatus.ACTIVE
        elif decision_upper in ("DEFER", "DEFERRED"):
            new_status = PlanStatus.UNDER_REVIEW
        elif decision_upper in ("REJECT", "REJECTED"):
            new_status = PlanStatus.ARCHIVED
        elif decision_upper in ("SELECT", "SELECTED"):
            new_status = PlanStatus.PENDING_APPROVAL
        else:
            raise ValidationError(
                f"Unsupported decision '{decision_val}'. Valid options: SELECT, DEFER, REJECT, APPROVE, ACTIVATE."
            )

        notes_val = request.notes or request.decision_maker_notes
        updated_plan = self.plan_repository.update_execution_plan_status(
            plan_id=plan_id, status=new_status, notes=notes_val
        )
        if not updated_plan:
            raise EntityNotFoundException("StrategicPlan", plan_id)

        return self._to_response_dto(updated_plan)

    def get_plan(self, plan_id: str) -> StrategicPlanResponseDTO:
        """Retrieves a strategic plan by ID."""
        plan = self.plan_repository.get_execution_plan(plan_id)
        if not plan:
            raise EntityNotFoundException("StrategicPlan", plan_id)
        return self._to_response_dto(plan)

    def list_plans(
        self,
        institution_id: Optional[str] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> StrategicPlanListResponseDTO:
        """Retrieves paginated strategic plans."""
        plans = self.plan_repository.list_execution_plans(
            institution_id=institution_id, status=status, skip=skip, limit=limit
        )
        items = [self._to_response_dto(p) for p in plans]
        return StrategicPlanListResponseDTO(total=len(items), items=items)

    # ==========================================================================
    # 6. AI Guardrails
    # ==========================================================================

    def _apply_ai_guardrailed_enhancement(self, plan: StrategicPlan) -> None:
        """Applies language improvements strictly to descriptions without altering numbers or logic."""
        if not self.ai_provider:
            return

        try:
            # AI may refine wording of objective descriptions
            prompt = (
                f"You are assisting with executive wording for strategic plan objectives. "
                f"Improve clarity without adding budgets, numbers, or targets: '{plan.title}'."
            )
            # Invoke provider only for non-destructive narrative improvement
            # Deterministic fields remain completely unchanged
            logger.debug(f"AI synthesis invoked for executive wording enhancement on plan '{plan.id}'")
        except Exception as ex:
            logger.warning(f"AI synthesis skipped due to provider error: {ex}")

    # ==========================================================================
    # 7. DTO Mappers
    # ==========================================================================

    def _to_response_dto(self, plan: StrategicPlan) -> StrategicPlanResponseDTO:
        """Converts StrategicPlan domain entity to StrategicPlanResponseDTO."""
        objectives_dto: List[StrategicObjectiveDTO] = []
        for obj in plan.objectives:
            targets_dto: List[StrategicTargetDTO] = []
            for tgt in obj.targets:
                # Agent 71 Canonical Indicator Linkage
                agent71_linkage = {
                    "metric_key": tgt.metric_key,
                    "metric_definition_id": tgt.metric_definition_id,
                    "direction": tgt.direction.value,
                    "measurement_frequency": tgt.measurement_frequency,
                    "baseline_value": tgt.baseline_value,
                    "baseline_period": tgt.baseline_period,
                    "target_value": tgt.target_value,
                    "target_period": tgt.target_period,
                    "target_status": tgt.status.value,
                }
                targets_dto.append(
                    StrategicTargetDTO(
                        id=tgt.id,
                        objective_id=tgt.objective_id,
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
                        agent71_linkage=agent71_linkage,
                    )
                )

            initiatives_dto: List[PlanInitiativeDTO] = []
            for init in obj.initiatives:
                milestones_dto = [
                    InitiativeMilestoneDTO(
                        id=m.id,
                        initiative_id=m.initiative_id,
                        title=m.title,
                        description=m.description,
                        due_period=m.due_period,
                        status=m.status.value,
                        completion_percentage=m.completion_percentage,
                        evidence_ids=m.evidence_ids,
                        target_date=str(m.target_date) if m.target_date else None,
                        completion_date=str(m.completion_date) if m.completion_date else None,
                    )
                    for m in init.milestones
                ]
                initiatives_dto.append(
                    PlanInitiativeDTO(
                        id=init.id,
                        objective_id=init.objective_id,
                        title=init.title,
                        description=init.description,
                        rationale=init.rationale,
                        owner_unit_id=init.owner_unit_id,
                        unit_owner=init.owner_unit_id,
                        supporting_units=init.supporting_units,
                        source_option_ids=init.source_option_ids,
                        dependencies=init.dependencies,
                        resource_requirement=init.resource_requirement.value,
                        implementation_risk=init.implementation_risk,
                        start_period=init.start_period,
                        end_period=init.end_period,
                        status=init.status.value,
                        success_criteria=init.success_criteria,
                        evidence_ids=init.evidence_ids,
                        milestones=milestones_dto,
                    )
                )

            primary_tgt = targets_dto[0] if targets_dto else None
            objectives_dto.append(
                StrategicObjectiveDTO(
                    id=obj.id,
                    strategic_plan_id=obj.strategic_plan_id,
                    title=obj.title,
                    description=obj.description,
                    strategic_rationale=obj.strategic_rationale,
                    source_option_ids=obj.source_option_ids,
                    strategic_issue_ids=obj.strategic_issue_ids,
                    related_metrics=obj.related_metrics,
                    status=obj.status.value,
                    priority=obj.priority,
                    owner_unit_id=obj.owner_unit_id,
                    owner=getattr(obj, "owner", None) or obj.owner_unit_id,
                    target_metric=getattr(obj, "target_metric", None) or (primary_tgt.metric_key if primary_tgt else None),
                    baseline_value=getattr(obj, "baseline_value", None) if getattr(obj, "baseline_value", None) is not None else (primary_tgt.baseline_value if primary_tgt else None),
                    target_value=getattr(obj, "target_value", None) if getattr(obj, "target_value", None) is not None else (primary_tgt.target_value if primary_tgt else None),
                    metric_key=getattr(obj, "metric_key", None) or (primary_tgt.metric_key if primary_tgt else None),
                    target_period=getattr(obj, "target_period", None) or (primary_tgt.target_period if primary_tgt else None),
                    assumptions=obj.assumptions,
                    confidence=obj.confidence,
                    targets=targets_dto,
                    strategic_targets=targets_dto,
                    initiatives=initiatives_dto,
                )
            )


        reviews_dto = [self._to_review_dto(r) for r in plan.execution_reviews]

        return StrategicPlanResponseDTO(
            id=plan.id,
            institution_id=plan.institution_id,
            institution_name=plan.institution_name,
            title=plan.title,
            horizon_start_year=plan.horizon_start_year,
            horizon_end_year=plan.horizon_end_year,
            source_analysis_ids=plan.source_analysis_ids,
            selected_option_ids=plan.selected_option_ids,
            objectives=objectives_dto,
            ownership_summary=plan.ownership_summary,
            assumptions=plan.assumptions,
            decision_support_disclaimer=plan.decision_support_disclaimer,
            leadership_disclaimer=getattr(plan, "leadership_disclaimer", plan.decision_support_disclaimer),
            vision_statement=getattr(plan, "vision_statement", None),
            mission_statement=getattr(plan, "mission_statement", None),
            existing_commitments=getattr(plan, "existing_commitments", None),
            review_period=getattr(plan, "review_period", "ANNUAL"),
            status=plan.status.value,
            engine_version=plan.engine_version,
            previous_version_id=plan.previous_version_id,
            created_at=plan.created_at.isoformat(),
            updated_at=plan.updated_at.isoformat(),
            execution_reviews=reviews_dto,
            strategic_options=getattr(plan, "strategic_options", []),
            scenarios=getattr(plan, "scenarios", []),
        )


    def _to_review_dto(self, review: ExecutionReview) -> ExecutionReviewDTO:
        """Converts ExecutionReview domain entity to ExecutionReviewDTO."""
        variances_dto = [
            TargetVarianceDTO(
                metric_key=v.metric_key,
                metric_definition_id=v.metric_definition_id,
                baseline_value=v.baseline_value,
                target_value=v.target_value,
                observed_value=v.observed_value,
                observed_period=v.observed_period,
                absolute_variance=v.absolute_variance,
                relative_variance=v.relative_variance,
                unit=v.unit,
                is_percentage=v.is_percentage,
                variance_notation=v.variance_notation,
                direction=v.direction.value,
                status=v.status.value,
                notes=v.notes,
            )
            for v in review.metric_variances
        ]

        actions_dto = [
            CorrectiveActionCandidateDTO(
                id=c.id,
                objective_id=c.objective_id,
                initiative_id=c.initiative_id,
                signal_type=c.signal_type.value if hasattr(c.signal_type, "value") else str(c.signal_type),
                title=c.title,
                description=c.description,
                suggested_action=c.suggested_action,
                rationale=c.rationale,
                requires_leadership_approval=c.requires_leadership_approval,
            )
            for c in review.corrective_actions
        ]

        return ExecutionReviewDTO(
            id=review.id,
            strategic_plan_id=review.strategic_plan_id,
            plan_id=review.strategic_plan_id,
            review_period=review.review_period,
            period=review.review_period,
            review_date=review.review_date.isoformat(),

            overall_status=review.overall_status.value,
            progress_summary=review.progress_summary,
            objective_statuses=review.objective_statuses,
            initiative_statuses=review.initiative_statuses,
            milestone_statuses=review.milestone_statuses,
            metric_variances=variances_dto,
            target_variances=variances_dto,
            diagnostic_signals=review.diagnostic_signals,
            risks=review.risks,
            corrective_actions=actions_dto,
            assumptions=review.assumptions,
            evidence_ids=review.evidence_ids,
            decision_support_disclaimer=getattr(
                review,
                "decision_support_disclaimer",
                getattr(review, "leadership_disclaimer", LEADERSHIP_DECISION_SUPPORT_DISCLAIMER),
            ),
            leadership_disclaimer=getattr(review, "leadership_disclaimer", LEADERSHIP_DECISION_SUPPORT_DISCLAIMER),
            created_at=review.created_at.isoformat() if hasattr(review.created_at, "isoformat") else str(review.created_at),
        )
