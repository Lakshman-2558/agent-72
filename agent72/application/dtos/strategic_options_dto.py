"""
Data Transfer Objects for Strategic Options, Scenarios & Prioritization (Phase 7).
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from agent72.domain.models.strategic_options import (
    FeasibilityLevel,
    OptionCategory,
    OptionStatus,
    PriorityLevel,
    ScenarioType,
)


class StrategicOptionsRequestDTO(BaseModel):
    """Input payload to trigger deterministic strategic options generation and evaluation."""
    institution_id: str = Field(..., description="Target institution ID")
    organizational_unit_id: Optional[str] = Field(None, description="Optional organizational unit scope")
    analysis_period: str = Field(..., description="Target academic period (e.g., '2024-2025')")
    strategic_intelligence_analysis_id: Optional[str] = Field(
        None, description="Optional ID of Strategic Intelligence Analysis to use as input"
    )
    include_ai_synthesis: bool = Field(
        default=False,
        description="Whether to generate natural-language option/trade-off summaries (never alters deterministic scores)",
    )


class StrategicOptionDTO(BaseModel):
    """Structured strategic choice derived from strategic intelligence."""
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
    feasibility: FeasibilityLevel
    resource_requirement: str  # LOW, MEDIUM, HIGH, UNCERTAIN
    implementation_risk: str   # LOW, MEDIUM, HIGH
    confidence: float
    status: OptionStatus
    trade_offs: List[str] = Field(default_factory=list)


class ScenarioDTO(BaseModel):
    """Conditional scenario projection for a strategic option."""
    id: str
    option_id: str
    scenario_type: ScenarioType
    title: str
    description: str
    assumptions: List[str] = Field(default_factory=list)
    expected_effects: List[str] = Field(default_factory=list)
    risks: List[str] = Field(default_factory=list)
    opportunities: List[str] = Field(default_factory=list)
    uncertainty: str
    confidence: float
    evidence_ids: List[str] = Field(default_factory=list)


class OptionEvaluationDTO(BaseModel):
    """Deterministic multi-dimensional evaluation across 7 dimensions."""
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


class StrategicOptionsResponseDTO(BaseModel):
    """Response payload for a complete strategic options analysis snapshot."""
    id: str
    institution_id: str
    organizational_unit_id: Optional[str] = None
    analysis_period: str
    generated_at: datetime
    strategic_intelligence_analysis_id: str
    options: List[StrategicOptionDTO] = Field(default_factory=list)
    scenarios: List[ScenarioDTO] = Field(default_factory=list)
    evaluations: List[OptionEvaluationDTO] = Field(default_factory=list)
    prioritized_option_ids: List[str] = Field(default_factory=list)
    assumptions: List[str] = Field(default_factory=list)
    uncertainty: Dict[str, Any] = Field(default_factory=dict)
    data_limitations: List[str] = Field(default_factory=list)
    decision_support_disclaimer: str
    engine_version: str
    ai_synthesis_notes: Optional[str] = None
    status: str


class StrategicOptionsListResponseDTO(BaseModel):
    """Paginated collection response of strategic options analyses."""
    total: int
    skip: int
    limit: int
    items: List[StrategicOptionsResponseDTO]
