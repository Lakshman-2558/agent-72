"""Domain entities and value objects for Agent 72 Strategic Planning."""

from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from enum import Enum
from typing import List, Optional


class PlanStatus(str, Enum):
    DRAFT = "DRAFT"
    UNDER_REVIEW = "UNDER_REVIEW"
    APPROVED = "APPROVED"
    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ResourceIntensity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class InitiativeStatus(str, Enum):
    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    DELAYED = "DELAYED"
    BLOCKED = "BLOCKED"
    CANCELLED = "CANCELLED"


class MilestoneStatus(str, Enum):
    PENDING = "PENDING"
    ACHIEVED = "ACHIEVED"
    MISSED = "MISSED"


@dataclass
class InitiativeMilestone:
    """Measurable milestone within an initiative."""
    id: Optional[str] = None
    initiative_id: Optional[str] = None
    title: str = ""
    target_date: Optional[date] = None
    status: MilestoneStatus = MilestoneStatus.PENDING
    completion_date: Optional[date] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class PlanInitiative:
    """Actionable program or initiative executing an objective."""
    id: Optional[str] = None
    objective_id: Optional[str] = None
    title: str = ""
    description: Optional[str] = None
    owner: Optional[str] = None
    budget: Optional[float] = None
    status: InitiativeStatus = InitiativeStatus.NOT_STARTED
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    milestones: List[InitiativeMilestone] = field(default_factory=list)


@dataclass
class PlanObjective:
    """Measurable target within a strategic plan."""
    id: Optional[str] = None
    plan_id: Optional[str] = None
    title: str = ""
    description: Optional[str] = None
    target_metric: str = ""
    metric_key: Optional[str] = None  # Linkage to canonical MetricDefinition
    target_period: Optional[str] = None  # Academic period for target achievement e.g. "2027-2028"
    baseline_value: Optional[float] = None
    target_value: Optional[float] = None
    weight: float = 1.0
    owner: Optional[str] = None
    initiatives: List[PlanInitiative] = field(default_factory=list)


@dataclass
class StrategicOption:
    """Option generated with rationale and resource intensity."""
    id: Optional[str] = None
    plan_id: Optional[str] = None
    title: str = ""
    rationale: str = ""
    resource_intensity: ResourceIntensity = ResourceIntensity.MEDIUM
    estimated_cost: Optional[float] = None
    risk_level: RiskLevel = RiskLevel.MEDIUM


@dataclass
class PlanScenario:
    """Scenario model projecting outcomes based on institutional assumptions."""
    id: Optional[str] = None
    plan_id: Optional[str] = None
    name: str = ""
    description: Optional[str] = None
    assumptions: str = ""
    projected_outcome: Optional[str] = None


@dataclass
class ExecutionReview:
    """Periodic or annual review tracking strategic plan execution."""
    id: Optional[str] = None
    plan_id: Optional[str] = None
    period: str = ""  # Academic year e.g. "2026-2027"
    review_date: date = field(default_factory=lambda: datetime.now(timezone.utc).date())
    progress_summary: str = ""
    variance_notes: Optional[str] = None
    recommendations: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class StrategicPlan:
    """Aggregate Root representing an Institutional Strategic Plan."""
    id: Optional[str] = None
    institution_id: Optional[str] = None  # Linkage to canonical Institution
    title: str = ""
    institution_name: str = ""
    horizon_start_year: int = 2026
    horizon_end_year: int = 2030
    vision_statement: Optional[str] = None
    mission_statement: Optional[str] = None
    existing_commitments: Optional[str] = None  # Existing commitments/mandates
    review_period: str = "ANNUAL"  # "ANNUAL", "SEMI-ANNUAL", "QUARTERLY"
    status: PlanStatus = PlanStatus.DRAFT
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    objectives: List[PlanObjective] = field(default_factory=list)
    strategic_options: List[StrategicOption] = field(default_factory=list)
    scenarios: List[PlanScenario] = field(default_factory=list)
    execution_reviews: List[ExecutionReview] = field(default_factory=list)

    def validate_horizon(self) -> None:
        """Domain invariant: start year must not exceed end year."""
        if self.horizon_start_year > self.horizon_end_year:
            raise ValueError(
                f"Horizon start year ({self.horizon_start_year}) cannot exceed end year ({self.horizon_end_year})."
            )
