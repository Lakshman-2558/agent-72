"""Pydantic Data Transfer Objects (DTOs) for Strategic Plans and Execution."""

from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field
from agent72.domain.models.plan import (
    PlanStatus,
    ResourceIntensity,
    RiskLevel,
    InitiativeStatus,
    MilestoneStatus,
)


class InitiativeMilestoneBaseDTO(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="Milestone title")
    target_date: Optional[date] = Field(None, description="Expected completion date")
    status: MilestoneStatus = Field(default=MilestoneStatus.PENDING)
    completion_date: Optional[date] = None


class InitiativeMilestoneCreateDTO(InitiativeMilestoneBaseDTO):
    pass


class InitiativeMilestoneResponseDTO(InitiativeMilestoneBaseDTO):
    model_config = ConfigDict(from_attributes=True)
    id: str
    initiative_id: str
    created_at: datetime


class PlanInitiativeBaseDTO(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="Initiative title")
    description: Optional[str] = None
    owner: Optional[str] = Field(None, max_length=255)
    budget: Optional[float] = Field(None, ge=0.0)
    status: InitiativeStatus = Field(default=InitiativeStatus.NOT_STARTED)
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class PlanInitiativeCreateDTO(PlanInitiativeBaseDTO):
    milestones: List[InitiativeMilestoneCreateDTO] = Field(default_factory=list)


class PlanInitiativeResponseDTO(PlanInitiativeBaseDTO):
    model_config = ConfigDict(from_attributes=True)
    id: str
    objective_id: str
    created_at: datetime
    updated_at: datetime
    milestones: List[InitiativeMilestoneResponseDTO] = Field(default_factory=list)


class ObjectiveBaseDTO(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="Objective title")
    description: Optional[str] = Field(None, description="Detailed description")
    target_metric: str = Field(..., min_length=1, max_length=255, description="Key performance indicator or metric")
    metric_key: Optional[str] = Field(None, max_length=100, description="Canonical metric linkage, e.g. 'research.publications.q1'")
    target_period: Optional[str] = Field(None, max_length=50, description="Target achievement period e.g. '2027-2028'")
    baseline_value: Optional[float] = Field(None, description="Starting historical baseline")
    target_value: Optional[float] = Field(None, description="Target numeric value")
    weight: float = Field(default=1.0, ge=0.0, le=10.0, description="Priority weight")
    owner: Optional[str] = Field(None, max_length=255, description="Designated initiative owner")


class ObjectiveCreateDTO(ObjectiveBaseDTO):
    initiatives: List[PlanInitiativeCreateDTO] = Field(default_factory=list)


class ObjectiveResponseDTO(ObjectiveBaseDTO):
    model_config = ConfigDict(from_attributes=True)
    id: str
    plan_id: str
    initiatives: List[PlanInitiativeResponseDTO] = Field(default_factory=list)


class StrategicOptionBaseDTO(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    rationale: str = Field(..., min_length=1)
    resource_intensity: ResourceIntensity = Field(default=ResourceIntensity.MEDIUM)
    estimated_cost: Optional[float] = Field(None, ge=0.0)
    risk_level: RiskLevel = Field(default=RiskLevel.MEDIUM)


class StrategicOptionCreateDTO(StrategicOptionBaseDTO):
    pass


class StrategicOptionResponseDTO(StrategicOptionBaseDTO):
    model_config = ConfigDict(from_attributes=True)
    id: str
    plan_id: str


class ScenarioBaseDTO(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    assumptions: str = Field(..., min_length=1)
    projected_outcome: Optional[str] = None


class ScenarioCreateDTO(ScenarioBaseDTO):
    pass


class ScenarioResponseDTO(ScenarioBaseDTO):
    model_config = ConfigDict(from_attributes=True)
    id: str
    plan_id: str


class ExecutionReviewCreateDTO(BaseModel):
    period: str = Field(..., min_length=4, max_length=50, description="Academic year e.g. '2026-2027'")
    review_date: date = Field(default_factory=lambda: datetime.now().date())
    progress_summary: str = Field(..., min_length=5, description="Executive review summary")
    variance_notes: Optional[str] = None
    recommendations: Optional[str] = None


class ExecutionReviewResponseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    plan_id: str
    period: str
    review_date: date
    progress_summary: str
    variance_notes: Optional[str]
    recommendations: Optional[str]
    created_at: datetime


class StrategicPlanCreateDTO(BaseModel):
    institution_id: Optional[str] = Field(None, description="Optional canonical Institution ID")
    title: str = Field(..., min_length=3, max_length=255, description="Institutional Plan Title")
    institution_name: str = Field(..., min_length=2, max_length=255, description="Name of University or College")
    horizon_start_year: int = Field(default=2026, ge=2000, le=2100)
    horizon_end_year: int = Field(default=2030, ge=2000, le=2100)
    vision_statement: Optional[str] = None
    mission_statement: Optional[str] = None
    existing_commitments: Optional[str] = None
    review_period: str = Field(default="ANNUAL", max_length=50)
    objectives: List[ObjectiveCreateDTO] = Field(default_factory=list)
    strategic_options: List[StrategicOptionCreateDTO] = Field(default_factory=list)
    scenarios: List[ScenarioCreateDTO] = Field(default_factory=list)


class StrategicPlanUpdateDTO(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=255)
    institution_name: Optional[str] = Field(None, min_length=2, max_length=255)
    horizon_start_year: Optional[int] = Field(None, ge=2000, le=2100)
    horizon_end_year: Optional[int] = Field(None, ge=2000, le=2100)
    vision_statement: Optional[str] = None
    mission_statement: Optional[str] = None
    existing_commitments: Optional[str] = None
    review_period: Optional[str] = None
    status: Optional[PlanStatus] = None


class StrategicPlanResponseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    institution_id: Optional[str]
    title: str
    institution_name: str
    horizon_start_year: int
    horizon_end_year: int
    vision_statement: Optional[str]
    mission_statement: Optional[str]
    existing_commitments: Optional[str]
    review_period: str
    status: PlanStatus
    created_at: datetime
    updated_at: datetime
    objectives: List[ObjectiveResponseDTO] = Field(default_factory=list)
    strategic_options: List[StrategicOptionResponseDTO] = Field(default_factory=list)
    scenarios: List[ScenarioResponseDTO] = Field(default_factory=list)
    execution_reviews: List[ExecutionReviewResponseDTO] = Field(default_factory=list)


class StrategicPlanListResponseDTO(BaseModel):
    total: int
    items: List[StrategicPlanResponseDTO]
