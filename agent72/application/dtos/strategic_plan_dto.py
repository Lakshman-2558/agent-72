"""Data Transfer Objects for Phase 8 Strategic Plan Generation & Execution Framework."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class StrategicPlanGenerationRequestDTO(BaseModel):
    """Request payload to generate a strategic plan from Phase 7 options."""
    institution_id: str = Field(..., description="Target institution UUID")
    title: Optional[str] = Field(None, description="Optional custom title for the strategic plan")
    horizon_start_year: int = Field(2026, description="Planning horizon start year")
    horizon_end_year: int = Field(2030, description="Planning horizon end year")
    strategic_options_analysis_id: str = Field(
        ..., description="UUID of the Phase 7 Strategic Options Analysis to consume"
    )
    selected_option_ids: Optional[List[str]] = Field(
        None, description="Explicit list of option IDs selected by leadership. If omitted, options with SELECTED_FOR_PLANNING are used."
    )
    override_selection_requirement: bool = Field(
        False, description="Whether to allow converting options that are not explicitly SELECTED_FOR_PLANNING"
    )
    include_ai_synthesis: bool = Field(
        False, description="Whether to request AI language enhancement for objectives/initiatives"
    )
    review_period: str = Field("ANNUAL", description="Review cadence (ANNUAL, SEMESTER, QUARTERLY, MONTHLY)")


class StrategicTargetDTO(BaseModel):
    """DTO for an objective's measurable strategic target."""
    id: str
    objective_id: str
    metric_key: str
    metric_definition_id: Optional[str] = None
    baseline_value: Optional[float] = None
    baseline_period: Optional[str] = None
    target_value: Optional[float] = None
    target_period: Optional[str] = None
    direction: str = "HIGHER_IS_BETTER"
    unit: str = "count"
    measurement_frequency: str = "ANNUAL"
    evidence_ids: List[str] = Field(default_factory=list)
    confidence: float = 1.0
    assumptions: List[str] = Field(default_factory=list)
    status: str = "PROPOSED_TARGET"
    gap: Optional[float] = None
    gap_unit_label: str = ""
    target_provenance: str = "DERIVED_FROM_EVIDENCE"
    agent71_linkage: Optional[Dict[str, Any]] = None


class InitiativeMilestoneDTO(BaseModel):
    """DTO for an initiative milestone."""
    id: str
    initiative_id: str
    title: str
    description: Optional[str] = None
    due_period: str
    status: str = "NOT_STARTED"
    completion_percentage: float = 0.0
    evidence_ids: List[str] = Field(default_factory=list)
    target_date: Optional[str] = None
    completion_date: Optional[str] = None


class PlanInitiativeDTO(BaseModel):
    """DTO for a strategic plan initiative."""
    id: str
    objective_id: str
    title: str
    description: Optional[str] = None
    rationale: Optional[str] = None
    owner_unit_id: str = "TO_BE_ASSIGNED"
    unit_owner: Optional[str] = None
    supporting_units: List[str] = Field(default_factory=list)
    source_option_ids: List[str] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)
    resource_requirement: str = "UNKNOWN"
    implementation_risk: str = "MEDIUM"
    start_period: str = ""
    end_period: str = ""
    status: str = "PLANNED"
    success_criteria: List[str] = Field(default_factory=list)
    evidence_ids: List[str] = Field(default_factory=list)
    milestones: List[InitiativeMilestoneDTO] = Field(default_factory=list)


class StrategicObjectiveDTO(BaseModel):
    """DTO for a strategic objective."""
    id: str
    strategic_plan_id: str
    title: str
    description: Optional[str] = None
    strategic_rationale: Optional[str] = None
    source_option_ids: List[str] = Field(default_factory=list)
    strategic_issue_ids: List[str] = Field(default_factory=list)
    related_metrics: List[str] = Field(default_factory=list)
    status: str = "PROPOSED"
    priority: str = "MEDIUM"
    owner_unit_id: str = "TO_BE_ASSIGNED"
    owner: Optional[str] = None
    target_metric: Optional[str] = None
    baseline_value: Optional[float] = None
    target_value: Optional[float] = None
    metric_key: Optional[str] = None
    target_period: Optional[str] = None
    assumptions: List[str] = Field(default_factory=list)
    confidence: float = 1.0
    targets: List[StrategicTargetDTO] = Field(default_factory=list)
    strategic_targets: List[StrategicTargetDTO] = Field(default_factory=list)
    initiatives: List[PlanInitiativeDTO] = Field(default_factory=list)



class TargetVarianceDTO(BaseModel):
    """DTO for direction-aware variance on a target indicator."""
    metric_key: str
    metric_definition_id: Optional[str] = None
    baseline_value: Optional[float] = None
    target_value: Optional[float] = None
    observed_value: Optional[float] = None
    observed_period: Optional[str] = None
    absolute_variance: Optional[float] = None
    relative_variance: Optional[float] = None
    unit: str = "count"
    is_percentage: bool = False
    variance_notation: str = ""
    direction: str = "HIGHER_IS_BETTER"
    status: str = "INSUFFICIENT_EVIDENCE"
    notes: Optional[str] = None


class CorrectiveActionCandidateDTO(BaseModel):
    """DTO for leadership-decision corrective action candidate."""
    id: str
    objective_id: Optional[str] = None
    initiative_id: Optional[str] = None
    signal_type: str
    title: str
    description: str
    suggested_action: str
    rationale: str
    requires_leadership_approval: bool = True


class ExecutionReviewDTO(BaseModel):
    """DTO for execution review output."""
    id: str
    strategic_plan_id: str
    plan_id: Optional[str] = None
    review_period: str
    period: Optional[str] = None
    review_date: str
    overall_status: str
    progress_summary: str
    variance_notes: Optional[str] = None
    recommendations: Optional[str] = None
    objective_statuses: Dict[str, str] = Field(default_factory=dict)
    initiative_statuses: Dict[str, str] = Field(default_factory=dict)
    milestone_statuses: Dict[str, str] = Field(default_factory=dict)
    metric_variances: List[TargetVarianceDTO] = Field(default_factory=list)
    target_variances: List[TargetVarianceDTO] = Field(default_factory=list)
    diagnostic_signals: List[Dict[str, Any]] = Field(default_factory=list)
    risks: List[Dict[str, Any]] = Field(default_factory=list)
    corrective_actions: List[CorrectiveActionCandidateDTO] = Field(default_factory=list)
    assumptions: List[str] = Field(default_factory=list)
    evidence_ids: List[str] = Field(default_factory=list)
    confidence: float = 1.0
    decision_support_disclaimer: str = (
        "Execution reviews generated by Agent 72 are decision-support artifacts. "
        "Corrective actions and resource allocations require explicit leadership approval."
    )
    leadership_disclaimer: Optional[str] = None
    created_at: str



class ExecutionReviewRequestDTO(BaseModel):
    """Request payload to trigger an automated execution review."""
    review_period: str = Field(..., description="Review period identifier, e.g. '2026-2027'")
    latest_evidence_ids: Optional[List[str]] = Field(
        None, description="Optional explicit evidence IDs for observed evaluation"
    )
    include_ai_synthesis: bool = Field(
        False, description="Whether to request AI executive synthesis of the review"
    )
    notes: Optional[str] = Field(None, description="Optional leadership context or notes")


class PlanDecisionRequestDTO(BaseModel):
    """Request payload to record an explicit leadership decision on a strategic plan."""
    decision: Optional[str] = Field(
        None, description="Decision action: SELECT, DEFER, REJECT, APPROVE, ACTIVATE"
    )
    status: Optional[str] = Field(None, description="Optional status alias for decision")
    notes: Optional[str] = Field(None, description="Leadership deliberation or decision rationale")
    decision_maker_notes: Optional[str] = Field(None, description="Optional notes alias")
    decided_by: Optional[str] = Field(None, description="Role or unit recording the decision")


class StrategicPlanResponseDTO(BaseModel):
    """Full strategic plan DTO."""
    id: str
    institution_id: Optional[str] = None
    institution_name: str
    title: str
    horizon_start_year: int
    horizon_end_year: int
    vision_statement: Optional[str] = None
    mission_statement: Optional[str] = None
    existing_commitments: Optional[str] = None
    review_period: Optional[str] = "ANNUAL"
    source_analysis_ids: List[str] = Field(default_factory=list)
    selected_option_ids: List[str] = Field(default_factory=list)
    objectives: List[StrategicObjectiveDTO] = Field(default_factory=list)
    ownership_summary: Dict[str, List[str]] = Field(default_factory=dict)
    assumptions: List[str] = Field(default_factory=list)
    decision_support_disclaimer: str
    leadership_disclaimer: Optional[str] = None
    status: str
    engine_version: str = "1.0.0"
    previous_version_id: Optional[str] = None
    created_at: str
    updated_at: str
    execution_reviews: List[ExecutionReviewDTO] = Field(default_factory=list)
    strategic_options: List[Dict[str, Any]] = Field(default_factory=list)
    scenarios: List[Dict[str, Any]] = Field(default_factory=list)



class StrategicPlanListResponseDTO(BaseModel):
    """Paginated list of strategic plans."""
    total: int
    items: List[StrategicPlanResponseDTO]
