"""
Domain models for Strategic Options, Scenarios & Prioritization (Phase 7).

Transforms:
Strategic Intelligence (Phase 6) -> Strategic Options -> Scenario Analysis -> Option Evaluation -> Prioritized Options

Answers:
"What strategic choices are available, what could happen under different conditions,
and which options appear most suitable for leadership consideration?"

Strict architectural guardrails:
- Leadership remains the final decision-maker. Agent 72 provides decision support only.
- Scenarios are conditional qualitative/directional projections, NOT predictions or fabricated budgets.
- All options are strictly traceable to Phase 6 issues, risks, opportunities, and canonical evidence.
- Deterministic 7-dimension evaluation formula with configurable weights.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class OptionCategory(str, Enum):
    """Classification of strategic options."""
    GROWTH = "GROWTH"
    IMPROVEMENT = "IMPROVEMENT"
    CAPABILITY = "CAPABILITY"
    RISK_MITIGATION = "RISK_MITIGATION"
    EFFICIENCY = "EFFICIENCY"
    DIFFERENTIATION = "DIFFERENTIATION"
    PARTNERSHIP = "PARTNERSHIP"
    TRANSFORMATION = "TRANSFORMATION"


class OptionStatus(str, Enum):
    """Lifecycle status of a strategic option."""
    PROPOSED = "PROPOSED"
    EVALUATED = "EVALUATED"
    PRIORITIZED = "PRIORITIZED"
    DEFERRED = "DEFERRED"
    REJECTED = "REJECTED"


class ScenarioType(str, Enum):
    """Conditional scenario archetypes."""
    BASELINE = "BASELINE"
    UPSIDE = "UPSIDE"
    DOWNSIDE = "DOWNSIDE"
    STRESS = "STRESS"


class FeasibilityLevel(str, Enum):
    """Operational and technical feasibility assessment."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class PriorityLevel(str, Enum):
    """Recommended leadership priority classification."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class EvaluationDimension(str, Enum):
    """The 7 exact dimensions used for deterministic option evaluation."""
    STRATEGIC_ALIGNMENT = "STRATEGIC_ALIGNMENT"
    IMPACT = "IMPACT"
    FEASIBILITY = "FEASIBILITY"
    RESOURCE_EFFICIENCY = "RESOURCE_EFFICIENCY"
    IMPLEMENTATION_RISK = "IMPLEMENTATION_RISK"
    URGENCY = "URGENCY"
    EVIDENCE_STRENGTH = "EVIDENCE_STRENGTH"


class StrategicOption(BaseModel):
    """
    Evidence-grounded strategic choice derived directly from Phase 6 intelligence.
    """
    id: str
    institution_id: str
    organizational_unit_id: Optional[str] = None
    category: OptionCategory
    title: str
    description: str
    strategic_rationale: str
    addressed_issue_ids: List[str] = Field(default_factory=list)
    addressed_risk_ids: List[str] = Field(default_factory=list)
    opportunity_ids: List[str] = Field(default_factory=list)
    related_metrics: List[str] = Field(default_factory=list)
    evidence_ids: List[str] = Field(default_factory=list)
    expected_outcomes: List[str] = Field(default_factory=list)
    assumptions: List[str] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)
    feasibility: FeasibilityLevel = FeasibilityLevel.MEDIUM
    resource_requirement: str = "MEDIUM"  # LOW, MEDIUM, HIGH, UNCERTAIN
    implementation_risk: str = "MEDIUM"   # LOW, MEDIUM, HIGH
    confidence: float = 0.8
    status: OptionStatus = OptionStatus.PROPOSED
    trade_offs: List[str] = Field(default_factory=list)


class Scenario(BaseModel):
    """
    Conditional qualitative/directional projection under specific external and execution conditions.
    Explicitly NOT an autonomous numerical forecast or prediction.
    """
    id: str
    option_id: str
    scenario_type: ScenarioType
    title: str
    description: str
    assumptions: List[str] = Field(default_factory=list)
    expected_effects: List[str] = Field(default_factory=list)
    risks: List[str] = Field(default_factory=list)
    opportunities: List[str] = Field(default_factory=list)
    uncertainty: str = "MEDIUM"  # LOW, MEDIUM, HIGH
    confidence: float = 0.8
    evidence_ids: List[str] = Field(default_factory=list)


class OptionEvaluation(BaseModel):
    """
    Deterministic multi-dimensional evaluation of a strategic option across all 7 dimensions.
    All dimension scores and total score are on a transparent 0-100 scale.
    """
    option_id: str
    strategic_alignment_score: float
    impact_score: float
    feasibility_score: float
    resource_efficiency_score: float
    implementation_risk_score: float  # Higher score = lower implementation risk / better risk profile
    urgency_score: float
    evidence_strength_score: float
    total_score: float
    priority_level: PriorityLevel
    trade_offs: List[str] = Field(default_factory=list)
    rationale: str


class StrategicOptionsAnalysis(BaseModel):
    """
    Immutable versioned snapshot aggregate containing strategic options, scenarios,
    evaluations, and prioritized recommendations for institutional leadership consideration.
    """
    id: Optional[str] = None
    institution_id: str
    organizational_unit_id: Optional[str] = None
    analysis_period: str
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    strategic_intelligence_analysis_id: str
    options: List[StrategicOption] = Field(default_factory=list)
    scenarios: List[Scenario] = Field(default_factory=list)
    evaluations: List[OptionEvaluation] = Field(default_factory=list)
    prioritized_option_ids: List[str] = Field(default_factory=list)
    assumptions: List[str] = Field(default_factory=list)
    uncertainty: Dict[str, Any] = Field(default_factory=dict)
    data_limitations: List[str] = Field(default_factory=list)
    decision_support_disclaimer: str = (
        "Strategic options and priority signals are decision-support outputs. "
        "Final strategic decisions remain with institutional leadership/governing bodies."
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    engine_version: str = "1.0.0"
    ai_synthesis_notes: Optional[str] = None
    status: str = "FINALIZED"
