"""Unit tests for Phase 8 — Strategic Plan Generation & Execution Framework."""

from datetime import datetime, timezone, date
import pytest
from typing import Any, Dict, List, Optional

from agent72.application.dtos.strategic_plan_dto import (
    StrategicPlanGenerationRequestDTO,
    ExecutionReviewRequestDTO,
    PlanDecisionRequestDTO,
)
from agent72.application.services.strategic_plan_service import StrategicPlanExecutionService
from agent72.core.exceptions import EntityNotFoundException, ValidationError
from agent72.domain.interfaces.ai_provider import IAIProvider
from agent72.domain.interfaces.evidence_repository import IEvidenceRepository
from agent72.domain.interfaces.organization_repository import IOrganizationRepository
from agent72.domain.interfaces.plan_repository import IPlanRepository
from agent72.domain.interfaces.strategic_options_repository import IStrategicOptionsRepository
from agent72.domain.models.evidence import (
    InstitutionalEvidence,
    MetricDefinition,
    MetricDirection,
    MetricDomain,
    SourceType,
    QualityTier,
)
from agent72.domain.models.organization import Institution, OrganizationalUnit, UnitType, EntityStatus
from agent72.domain.models.plan import StrategicPlan as Phase1Plan, ExecutionReview as Phase1Review
from agent72.domain.models.strategic_options import (
    FeasibilityLevel,
    OptionCategory,
    OptionStatus,
    PriorityLevel,
    StrategicOption,
    StrategicOptionsAnalysis,
)
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


class InMemoryPlanRepository(IPlanRepository):
    def __init__(self):
        self.phase1_plans: Dict[str, Phase1Plan] = {}
        self.execution_plans: Dict[str, StrategicPlan] = {}
        self.phase8_reviews: Dict[str, List[ExecutionReview]] = {}

    def get_by_id(self, plan_id: str):
        return self.phase1_plans.get(plan_id)

    def list_all(self, skip=0, limit=50):
        return list(self.phase1_plans.values())[skip : skip + limit]

    def create(self, plan: Phase1Plan):
        self.phase1_plans[plan.id] = plan
        return plan

    def update(self, plan: Phase1Plan):
        self.phase1_plans[plan.id] = plan
        return plan

    def delete(self, plan_id: str):
        return self.phase1_plans.pop(plan_id, None) is not None

    def add_execution_review(self, plan_id: str, review: Phase1Review):
        return review

    def create_execution_plan(self, plan: StrategicPlan) -> StrategicPlan:
        self.execution_plans[plan.id] = plan
        return plan

    def get_execution_plan(self, plan_id: str) -> Optional[StrategicPlan]:
        return self.execution_plans.get(plan_id)

    def list_execution_plans(self, institution_id=None, status=None, skip=0, limit=50):
        res = list(self.execution_plans.values())
        if institution_id:
            res = [p for p in res if p.institution_id == institution_id]
        if status:
            res = [p for p in res if p.status.value == status]
        return res[skip : skip + limit]

    def add_phase8_execution_review(self, plan_id: str, review: ExecutionReview) -> ExecutionReview:
        self.phase8_reviews.setdefault(plan_id, []).append(review)
        if plan_id in self.execution_plans:
            self.execution_plans[plan_id].execution_reviews.append(review)
        return review

    def update_execution_plan_status(self, plan_id: str, status: PlanStatus, notes=None):
        if plan_id not in self.execution_plans:
            return None
        self.execution_plans[plan_id].status = status
        return self.execution_plans[plan_id]


class InMemoryOptionsRepository(IStrategicOptionsRepository):
    def __init__(self):
        self.analyses: Dict[str, StrategicOptionsAnalysis] = {}

    def create_analysis(self, analysis: StrategicOptionsAnalysis):
        self.analyses[analysis.id] = analysis
        return analysis

    def get_analysis_by_id(self, analysis_id: str):
        return self.analyses.get(analysis_id)

    def list_analyses(self, institution_id=None, organizational_unit_id=None, analysis_period=None, limit=50, offset=0):
        return list(self.analyses.values())[offset : offset + limit]

    def count_analyses(self, institution_id=None, organizational_unit_id=None, analysis_period=None):
        return len(self.analyses)


class InMemoryEvidenceRepository(IEvidenceRepository):
    def __init__(self):
        self.metric_defs: Dict[str, MetricDefinition] = {}
        self.evidence: Dict[str, InstitutionalEvidence] = {}

    def list_metric_definitions(self, domain=None, **kwargs) -> List[MetricDefinition]:
        defs = list(self.metric_defs.values())
        if domain:
            defs = [d for d in defs if d.domain == domain]
        return defs

    def get_latest_evidence(self, institution_id: str, metric_key: str, unit_id=None) -> Optional[InstitutionalEvidence]:
        matching = [
            e for e in self.evidence.values()
            if e.institution_id == institution_id and e.metric_key == metric_key
        ]
        if unit_id:
            matching = [e for e in matching if e.unit_id == unit_id]
        if not matching:
            return None
        matching.sort(key=lambda x: x.period, reverse=True)
        return matching[0]

    def get_by_id(self, evidence_id: str):
        return self.evidence.get(evidence_id)

    def create_metric_definition(self, definition: MetricDefinition) -> MetricDefinition:
        self.metric_defs[definition.metric_key] = definition
        return definition

    def get_metric_definition(self, metric_key: str) -> Optional[MetricDefinition]:
        return self.metric_defs.get(metric_key)

    def find_existing_evidence(self, institution_id: str, idempotency_key: str) -> Optional[InstitutionalEvidence]:
        return None

    def record_evidence(self, evidence: InstitutionalEvidence) -> InstitutionalEvidence:
        self.evidence[evidence.id] = evidence
        return evidence

    def record_evidence_batch(self, evidence_items: List[InstitutionalEvidence]) -> List[InstitutionalEvidence]:
        for e in evidence_items:
            self.evidence[e.id] = e
        return evidence_items

    def query_evidence(self, institution_id: str, **kwargs) -> List[InstitutionalEvidence]:
        return [e for e in self.evidence.values() if e.institution_id == institution_id]

    def get_historical_series(self, institution_id: str, metric_key: str, **kwargs) -> List[InstitutionalEvidence]:
        return [e for e in self.evidence.values() if e.institution_id == institution_id and e.metric_key == metric_key]

    def get_evidence_by_domain(self, institution_id: str, domain: MetricDomain, **kwargs) -> List[InstitutionalEvidence]:
        return [e for e in self.evidence.values() if e.institution_id == institution_id]

    def record_batch_log(self, batch_log):
        return batch_log

    def get_batch_log(self, batch_id: str):
        return None

    def find_by_batch_id(self, batch_id: str) -> List[InstitutionalEvidence]:
        return []


class InMemoryOrgRepository(IOrganizationRepository):
    def __init__(self):
        self.institutions: Dict[str, Institution] = {}
        self.units: Dict[str, List[OrganizationalUnit]] = {}

    def get_institution_by_id(self, inst_id: str):
        return self.institutions.get(inst_id)

    def list_units_by_institution(self, inst_id: str):
        return self.units.get(inst_id, [])

    def create_institution(self, inst): self.institutions[inst.id] = inst; return inst
    def get_institution_by_code(self, c): return None
    def list_institutions(self, *args, **kwargs): return list(self.institutions.values())
    def update_institution(self, inst): return inst
    def delete_institution(self, id): return True
    def create_unit(self, unit): self.units.setdefault(unit.institution_id, []).append(unit); return unit
    def get_unit_by_id(self, uid): return None
    def get_unit_by_code(self, i, c): return None
    def update_unit(self, u): return u
    def delete_unit(self, uid): return True


class MockAIProvider(IAIProvider):
    def generate_completion(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 1024,
    ) -> str:
        return "Refined strategic objective narrative."

    def health_check(self) -> Dict[str, Any]:
        return {"status": "healthy", "provider": "mock"}


# ==============================================================================
# Pytest Fixtures
# ==============================================================================

@pytest.fixture
def setup_services():
    plan_repo = InMemoryPlanRepository()
    options_repo = InMemoryOptionsRepository()
    evidence_repo = InMemoryEvidenceRepository()
    org_repo = InMemoryOrgRepository()
    ai = MockAIProvider()

    # Seed Institution
    inst = Institution(
        id="inst-1",
        code="APEX",
        name="Apex University",
        institution_type="UNIVERSITY",
        status=EntityStatus.ACTIVE,
    )
    org_repo.create_institution(inst)

    # Seed Units
    org_repo.create_unit(OrganizationalUnit(
        id="unit-tp",
        institution_id="inst-1",
        code="TP",
        name="Training & Placement",
        unit_type=UnitType.DEPARTMENT,
        status=EntityStatus.ACTIVE,
    ))
    org_repo.create_unit(OrganizationalUnit(
        id="unit-res",
        institution_id="inst-1",
        code="RND",
        name="Research & Development",
        unit_type=UnitType.DEPARTMENT,
        status=EntityStatus.ACTIVE,
    ))

    # Seed Metric Definitions
    evidence_repo.create_metric_definition(MetricDefinition(
        id="md-1",
        metric_key="placement.rate",
        name="Placement Rate",
        domain=MetricDomain.PLACEMENT_EMPLOYER_DEMAND,
        default_unit="%",
        direction=MetricDirection.HIGHER_IS_BETTER,
    ))
    evidence_repo.create_metric_definition(MetricDefinition(
        id="md-2",
        metric_key="research.publications",
        name="Annual Publications",
        domain=MetricDomain.RESEARCH_PRODUCTIVITY,
        default_unit="count",
        direction=MetricDirection.HIGHER_IS_BETTER,
    ))
    evidence_repo.create_metric_definition(MetricDefinition(
        id="md-3",
        metric_key="student.dropout_rate",
        name="Student Dropout Rate",
        domain=MetricDomain.ACADEMIC_PERFORMANCE,
        default_unit="%",
        direction=MetricDirection.LOWER_IS_BETTER,
    ))

    # Seed Historical Evidence for baseline
    evidence_repo.evidence["ev-1"] = InstitutionalEvidence(
        id="ev-1",
        institution_id="inst-1",
        metric_key="placement.rate",
        domain="PLACEMENT_EMPLOYER_DEMAND",
        numeric_value=72.5,
        unit="%",
        period="2025-2026",
        as_of_date=date(2026, 1, 1),
        source_type=SourceType.MANUAL,
        source_name="Career Office",
    )
    evidence_repo.evidence["ev-2"] = InstitutionalEvidence(
        id="ev-2",
        institution_id="inst-1",
        metric_key="research.publications",
        domain="RESEARCH_PRODUCTIVITY",
        numeric_value=120.0,
        unit="count",
        period="2025-2026",
        as_of_date=date(2026, 1, 1),
        source_type=SourceType.MANUAL,
        source_name="Research Office",
    )

    # Seed Phase 7 Options Analysis
    opt1 = StrategicOption(
        id="opt-curriculum",
        institution_id="inst-1",
        category=OptionCategory.IMPROVEMENT,
        title="Industry & Curriculum Alignment",
        description="Redesign core curricula with employer advisory boards.",
        strategic_rationale="Closes graduate skills gap and raises placement rate.",
        addressed_issue_ids=["issue-curriculum-gap"],
        addressed_risk_ids=["risk-declining-hiring"],
        opportunity_ids=["opp-tech-parks"],
        related_metrics=["placement.rate"],
        evidence_ids=["ev-1"],
        expected_outcomes=["Placement rate rises to 82%"],
        assumptions=["Faculty willing to update course plans"],
        dependencies=["Employer board charter"],
        feasibility=FeasibilityLevel.HIGH,
        resource_requirement="MEDIUM",
        implementation_risk="LOW",
        confidence=0.9,
        status=OptionStatus.PROPOSED,
    )
    opt2 = StrategicOption(
        id="opt-internships",
        institution_id="inst-1",
        category=OptionCategory.PARTNERSHIP,
        title="Employer Internship Expansion",
        description="Establish mandatory semester internships with industry partners.",
        strategic_rationale="Provides practical workplace immersion.",
        addressed_issue_ids=["issue-industry-exposure"],
        addressed_risk_ids=[],
        opportunity_ids=["opp-tech-parks"],
        related_metrics=["placement.rate"],
        evidence_ids=["ev-1"],
        expected_outcomes=["90% of students complete industry internships"],
        assumptions=["Sufficient regional industry placement slots"],
        dependencies=["Corporate partnership agreements"],
        feasibility=FeasibilityLevel.HIGH,
        resource_requirement="LOW",
        implementation_risk="LOW",
        confidence=0.85,
        status=OptionStatus.PROPOSED,
    )
    opt3 = StrategicOption(
        id="opt-research",
        institution_id="inst-1",
        category=OptionCategory.GROWTH,
        title="Research Productivity Expansion",
        description="Seed funding and lab infrastructure incentives for Tier-1 publications.",
        strategic_rationale="Increases citation index and research footprint.",
        addressed_issue_ids=["issue-low-research-output"],
        addressed_risk_ids=[],
        opportunity_ids=["opp-national-grants"],
        related_metrics=["research.publications"],
        evidence_ids=["ev-2"],
        expected_outcomes=["Publications increase to 180 annual"],
        assumptions=["Seed funding approved in capital budget"],
        dependencies=["Budget allocation", "Lab equipment upgrade"],
        feasibility=FeasibilityLevel.MEDIUM,
        resource_requirement="HIGH",
        implementation_risk="MEDIUM",
        confidence=0.8,
        status=OptionStatus.PROPOSED,
    )

    analysis = StrategicOptionsAnalysis(
        id="analysis-p7",
        institution_id="inst-1",
        analysis_period="2025-2026",
        strategic_intelligence_analysis_id="intel-p6",
        options=[opt1, opt2, opt3],
        scenarios=[],
        evaluations=[],
        prioritized_option_ids=["opt-curriculum", "opt-internships", "opt-research"],
    )
    options_repo.create_analysis(analysis)

    service = StrategicPlanExecutionService(
        plan_repository=plan_repo,
        options_repository=options_repo,
        evidence_repository=evidence_repo,
        organization_repository=org_repo,
        ai_provider=ai,
    )
    return service, plan_repo, options_repo, evidence_repo, org_repo


# ==============================================================================
# Unit Tests
# ==============================================================================

def test_selected_option_to_objective_traceability(setup_services):
    service, plan_repo, options_repo, _, _ = setup_services

    req = StrategicPlanGenerationRequestDTO(
        institution_id="inst-1",
        horizon_start_year=2026,
        horizon_end_year=2030,
        strategic_options_analysis_id="analysis-p7",
        selected_option_ids=["opt-research"],
        override_selection_requirement=True,
    )
    plan_dto = service.generate_plan_from_options(req)

    assert plan_dto.id is not None
    assert plan_dto.status == "DRAFT"
    assert "decision-support" in plan_dto.decision_support_disclaimer.lower()
    assert len(plan_dto.objectives) == 1

    obj = plan_dto.objectives[0]
    assert "research" in obj.title.lower()
    assert "opt-research" in obj.source_option_ids
    assert "issue-low-research-output" in obj.strategic_issue_ids
    assert "research.publications" in obj.related_metrics


def test_multiple_related_options_combined_into_unified_objective(setup_services):
    service, _, _, _, _ = setup_services

    # opt-curriculum and opt-internships both share theme EMPLOYABILITY_AND_INDUSTRY
    req = StrategicPlanGenerationRequestDTO(
        institution_id="inst-1",
        horizon_start_year=2026,
        horizon_end_year=2030,
        strategic_options_analysis_id="analysis-p7",
        selected_option_ids=["opt-curriculum", "opt-internships"],
        override_selection_requirement=True,
    )
    plan_dto = service.generate_plan_from_options(req)

    # Should cluster into 1 coherent objective instead of 2 duplicate ones
    assert len(plan_dto.objectives) == 1
    obj = plan_dto.objectives[0]
    assert "employab" in obj.title.lower() or "industry" in obj.title.lower()
    assert "opt-curriculum" in obj.source_option_ids
    assert "opt-internships" in obj.source_option_ids
    assert "issue-curriculum-gap" in obj.strategic_issue_ids
    assert "issue-industry-exposure" in obj.strategic_issue_ids


def test_objective_target_anchoring_and_agent71_linkage(setup_services):
    service, _, _, _, _ = setup_services

    req = StrategicPlanGenerationRequestDTO(
        institution_id="inst-1",
        horizon_start_year=2026,
        horizon_end_year=2030,
        strategic_options_analysis_id="analysis-p7",
        selected_option_ids=["opt-curriculum"],
        override_selection_requirement=True,
    )
    plan_dto = service.generate_plan_from_options(req)
    obj = plan_dto.objectives[0]
    assert len(obj.targets) == 1

    target = obj.targets[0]
    assert target.metric_key == "placement.rate"
    assert target.direction == "HIGHER_IS_BETTER"
    assert target.baseline_value == 72.5
    assert target.baseline_period == "2025-2026"
    assert target.status == "PROPOSED_TARGET"
    assert target.target_value == 82.5  # 72.5 + 10 percentage points proposed
    assert target.gap == 10.0
    assert target.gap_unit_label == "percentage points"

    # Verify Agent 71 Canonical Linkage
    linkage = target.agent71_linkage
    assert linkage is not None
    assert linkage["metric_key"] == "placement.rate"
    assert linkage["metric_definition_id"] == "md-1"
    assert linkage["direction"] == "HIGHER_IS_BETTER"
    assert linkage["measurement_frequency"] == "ANNUAL"


def test_missing_metric_definition_flagged_without_fabrication(setup_services):
    service, _, options_repo, _, _ = setup_services

    # Add option with unregistered metric
    analysis = options_repo.get_analysis_by_id("analysis-p7")
    unregistered_opt = StrategicOption(
        id="opt-unregistered",
        institution_id="inst-1",
        category=OptionCategory.DIFFERENTIATION,
        title="Alumni Giving Expansion",
        description="Establish alumni endowment matching program.",
        strategic_rationale="Enhances non-tuition revenue stream.",
        addressed_issue_ids=[],
        addressed_risk_ids=[],
        opportunity_ids=[],
        related_metrics=["alumni.endowment_giving"],  # Not in MetricDefinitions!
        evidence_ids=[],
        expected_outcomes=[],
        assumptions=[],
        dependencies=[],
        feasibility=FeasibilityLevel.MEDIUM,
        resource_requirement="LOW",
        implementation_risk="LOW",
        confidence=0.7,
        status=OptionStatus.PROPOSED,
    )
    analysis.options.append(unregistered_opt)

    req = StrategicPlanGenerationRequestDTO(
        institution_id="inst-1",
        horizon_start_year=2026,
        horizon_end_year=2030,
        strategic_options_analysis_id="analysis-p7",
        selected_option_ids=["opt-unregistered"],
        override_selection_requirement=True,
    )
    plan_dto = service.generate_plan_from_options(req)
    target = plan_dto.objectives[0].targets[0]

    assert target.metric_key == "alumni.endowment_giving"
    assert target.status == "REQUIRING_METRIC_DEFINITION"
    assert target.metric_definition_id is None
    assert any("not formally registered" in a for a in plan_dto.assumptions)


def test_initiative_generation_and_unit_ownership(setup_services):
    service, _, _, _, _ = setup_services

    req = StrategicPlanGenerationRequestDTO(
        institution_id="inst-1",
        horizon_start_year=2026,
        horizon_end_year=2030,
        strategic_options_analysis_id="analysis-p7",
        selected_option_ids=["opt-curriculum"],
        override_selection_requirement=True,
    )
    plan_dto = service.generate_plan_from_options(req)
    inits = plan_dto.objectives[0].initiatives

    assert len(inits) >= 2
    # Ensure owner is an organizational unit, not an invented person
    for init in inits:
        assert init.owner_unit_id in ("Training & Placement", "Career Services", "Academic Affairs")
        assert not any(title in init.owner_unit_id for title in ("Dr.", "Prof.", "John", "Alice"))
        assert len(init.milestones) >= 2


def test_milestones_and_dependencies_carried_forward(setup_services):
    service, _, _, _, _ = setup_services

    req = StrategicPlanGenerationRequestDTO(
        institution_id="inst-1",
        horizon_start_year=2026,
        horizon_end_year=2030,
        strategic_options_analysis_id="analysis-p7",
        selected_option_ids=["opt-research"],
        override_selection_requirement=True,
    )
    plan_dto = service.generate_plan_from_options(req)
    inits = plan_dto.objectives[0].initiatives

    # Dependencies carried forward from opt-research
    all_dependencies = [d for init in inits for d in init.dependencies]
    assert any("Budget allocation" in d for d in all_dependencies)
    assert any("Lab equipment upgrade" in d for d in all_dependencies)

    # Milestones have due periods across planning horizon
    milestones = [m for init in inits for m in init.milestones]
    due_periods = [m.due_period for m in milestones]
    assert any("2026" in dp for dp in due_periods)
    assert any("2027" in dp or "2028" in dp for dp in due_periods)


def test_resource_uncertainty_without_invented_budgets(setup_services):
    service, _, _, _, _ = setup_services

    req = StrategicPlanGenerationRequestDTO(
        institution_id="inst-1",
        horizon_start_year=2026,
        horizon_end_year=2030,
        strategic_options_analysis_id="analysis-p7",
        selected_option_ids=["opt-research"],
        override_selection_requirement=True,
    )
    plan_dto = service.generate_plan_from_options(req)
    init = plan_dto.objectives[0].initiatives[0]

    assert init.resource_requirement in ("HIGH", "MEDIUM", "LOW", "UNKNOWN")


def test_plan_lifecycle_and_leadership_decision_governance(setup_services):
    service, _, _, _, _ = setup_services

    # 1. Generation initial status is strictly DRAFT
    req = StrategicPlanGenerationRequestDTO(
        institution_id="inst-1",
        horizon_start_year=2026,
        horizon_end_year=2030,
        strategic_options_analysis_id="analysis-p7",
        selected_option_ids=["opt-curriculum"],
        override_selection_requirement=True,
    )
    plan_dto = service.generate_plan_from_options(req)
    assert plan_dto.status == "DRAFT"

    # 2. Leadership APPROVE
    approved = service.update_plan_decision(
        plan_dto.id, PlanDecisionRequestDTO(decision="APPROVE", notes="Approved by Board of Governors")
    )
    assert approved.status == "APPROVED"

    # 3. Leadership ACTIVATE
    activated = service.update_plan_decision(
        plan_dto.id, PlanDecisionRequestDTO(decision="ACTIVATE", notes="Activated for Year 1 operational rollout")
    )
    assert activated.status == "ACTIVE"


def test_option_selection_enforcement_prevents_unselected_options(setup_services):
    service, _, options_repo, _, _ = setup_services

    analysis = options_repo.get_analysis_by_id("analysis-p7")
    analysis.options[0].status = "REJECTED"

    # Attempting to generate from REJECTED option without override should fail
    req = StrategicPlanGenerationRequestDTO(
        institution_id="inst-1",
        horizon_start_year=2026,
        horizon_end_year=2030,
        strategic_options_analysis_id="analysis-p7",
        selected_option_ids=["opt-curriculum"],
        override_selection_requirement=False,
    )
    with pytest.raises(ValidationError) as exc:
        service.generate_plan_from_options(req)
    assert "REJECTED" in str(exc.value)


def test_execution_review_direction_aware_target_variance(setup_services):
    service, plan_repo, _, evidence_repo, _ = setup_services

    # Create plan
    req = StrategicPlanGenerationRequestDTO(
        institution_id="inst-1",
        horizon_start_year=2026,
        horizon_end_year=2030,
        strategic_options_analysis_id="analysis-p7",
        selected_option_ids=["opt-curriculum", "opt-research"],
        override_selection_requirement=True,
    )
    plan = service.generate_plan_from_options(req)

    # Ingest new evidence for execution review period 2027
    # placement.rate target is 82.5% (HIGHER_IS_BETTER). Observed is 84.0% -> ON_TRACK
    evidence_repo.evidence["ev-rev-1"] = InstitutionalEvidence(
        id="ev-rev-1",
        institution_id="inst-1",
        metric_key="placement.rate",
        domain="STUDENT_OUTCOMES",
        numeric_value=84.0,
        unit="%",
        period="2027",
        as_of_date=date(2027, 4, 1),
        source_type=SourceType.MANUAL,
        source_name="Placement Audit",
    )

    # research.publications target is 150.0 (HIGHER_IS_BETTER). Observed is 110.0 -> OFF_TRACK
    evidence_repo.evidence["ev-rev-2"] = InstitutionalEvidence(
        id="ev-rev-2",
        institution_id="inst-1",
        metric_key="research.publications",
        domain="RESEARCH",
        numeric_value=110.0,
        unit="count",
        period="2027",
        as_of_date=date(2027, 4, 1),
        source_type=SourceType.MANUAL,
        source_name="Research Audit",
    )

    review_dto = service.record_execution_review(
        plan.id,
        ExecutionReviewRequestDTO(
            review_period="2027",
            latest_evidence_ids=["ev-rev-1", "ev-rev-2"],
        ),
    )

    assert review_dto.strategic_plan_id == plan.id
    assert len(review_dto.metric_variances) >= 2

    # Placement variance check
    placement_var = next(v for v in review_dto.metric_variances if v.metric_key == "placement.rate")
    assert placement_var.status == "ON_TRACK"
    assert placement_var.observed_value == 84.0
    assert "percentage points" in placement_var.variance_notation

    # Research variance check
    res_var = next(v for v in review_dto.metric_variances if v.metric_key == "research.publications")
    assert res_var.status == "OFF_TRACK"
    assert res_var.observed_value == 110.0

    # Diagnostic signal emitted
    assert any(s["signal_type"] == "TARGET_OFF_TRACK" for s in review_dto.diagnostic_signals)
    # Candidate corrective action generated
    assert any("research.publications" in ca.title or "remediate" in ca.title.lower() for ca in review_dto.corrective_actions)


def test_execution_review_missing_evidence_not_failure(setup_services):
    service, _, _, evidence_repo, _ = setup_services

    req = StrategicPlanGenerationRequestDTO(
        institution_id="inst-1",
        horizon_start_year=2026,
        horizon_end_year=2030,
        strategic_options_analysis_id="analysis-p7",
        selected_option_ids=["opt-curriculum"],
        override_selection_requirement=True,
    )
    plan = service.generate_plan_from_options(req)

    # Clear evidence to simulate data gap
    evidence_repo.evidence.clear()

    review_dto = service.record_execution_review(
        plan.id,
        ExecutionReviewRequestDTO(review_period="2027", latest_evidence_ids=[]),
    )

    # Must be INSUFFICIENT_EVIDENCE, not OFF_TRACK
    var = review_dto.metric_variances[0]
    assert var.status == "INSUFFICIENT_EVIDENCE"
    assert var.observed_value is None
    assert any(s["signal_type"] == "EVIDENCE_STALE" for s in review_dto.diagnostic_signals)


def test_execution_review_delayed_milestone_detection(setup_services):
    service, plan_repo, _, _, _ = setup_services

    req = StrategicPlanGenerationRequestDTO(
        institution_id="inst-1",
        horizon_start_year=2026,
        horizon_end_year=2030,
        strategic_options_analysis_id="analysis-p7",
        selected_option_ids=["opt-curriculum"],
        override_selection_requirement=True,
    )
    plan = service.generate_plan_from_options(req)

    # In the plan, milestone is due 2026-H1 with completion 0.0. Review period is 2027.
    review_dto = service.record_execution_review(
        plan.id,
        ExecutionReviewRequestDTO(review_period="2027"),
    )

    # Milestone should be detected as delayed
    assert any(s["signal_type"] == "MILESTONE_DELAYED" for s in review_dto.diagnostic_signals)
    assert any(ca.signal_type == "MILESTONE_DELAYED" for ca in review_dto.corrective_actions)


def test_execution_review_is_immutable_snapshot(setup_services):
    service, plan_repo, _, _, _ = setup_services

    req = StrategicPlanGenerationRequestDTO(
        institution_id="inst-1",
        horizon_start_year=2026,
        horizon_end_year=2030,
        strategic_options_analysis_id="analysis-p7",
        selected_option_ids=["opt-curriculum"],
        override_selection_requirement=True,
    )
    plan = service.generate_plan_from_options(req)

    # Run review 1
    rev1 = service.record_execution_review(plan.id, ExecutionReviewRequestDTO(review_period="2026-H2"))
    # Run review 2
    rev2 = service.record_execution_review(plan.id, ExecutionReviewRequestDTO(review_period="2027-H1"))

    # Both reviews exist in repository history without overwriting
    plan_refetched = service.get_plan(plan.id)
    assert len(plan_refetched.execution_reviews) == 2
    assert rev1.id != rev2.id
    assert plan_refetched.status == "DRAFT"  # Plan status was NOT altered by reviews
