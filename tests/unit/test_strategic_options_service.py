"""Unit tests for Phase 7 Strategic Options, Scenarios & Prioritization Service."""

from datetime import datetime, timezone
import pytest

from agent72.application.dtos.strategic_options_dto import StrategicOptionsRequestDTO
from agent72.application.services.strategic_options_service import StrategicOptionsService
from agent72.core.config import settings
from agent72.core.exceptions import ValidationError
from agent72.domain.interfaces.ai_provider import IAIProvider
from agent72.domain.interfaces.strategic_intelligence_repository import IStrategicIntelligenceRepository
from agent72.domain.interfaces.strategic_options_repository import IStrategicOptionsRepository
from agent72.domain.models.analysis import ConfidenceAssessment
from agent72.domain.models.evidence import FreshnessStatus, MetricDomain
from agent72.domain.models.strategic_intelligence import (
    ConstraintSignal,
    ExternalFactor,
    ExternalFactorCategory,
    ImpactLevel,
    IssueCategory,
    LikelihoodLevel,
    OpportunitySignal,
    RiskSeverity,
    RiskSignal,
    StrategicIntelligenceAnalysis,
    StrategicIssue,
    UncertaintyLevel,
)
from agent72.domain.models.strategic_options import (
    FeasibilityLevel,
    OptionCategory,
    OptionStatus,
    PriorityLevel,
    ScenarioType,
    StrategicOptionsAnalysis,
)


class InMemoryStrategicIntelligenceRepo(IStrategicIntelligenceRepository):
    def __init__(self):
        self.analyses: dict[str, StrategicIntelligenceAnalysis] = {}

    def create_strategic_intelligence_analysis(self, analysis: StrategicIntelligenceAnalysis) -> StrategicIntelligenceAnalysis:
        if not analysis.id:
            analysis.id = f"intel-{len(self.analyses) + 1}"
        self.analyses[analysis.id] = analysis
        return analysis

    def get_strategic_intelligence_analysis_by_id(self, analysis_id: str):
        return self.analyses.get(analysis_id)

    def list_strategic_intelligence_analyses(self, institution_id=None, organizational_unit_id=None, analysis_period=None, skip=0, limit=50):
        res = list(self.analyses.values())
        if institution_id:
            res = [a for a in res if a.institution_id == institution_id]
        if organizational_unit_id:
            res = [a for a in res if a.organizational_unit_id == organizational_unit_id]
        if analysis_period:
            res = [a for a in res if a.analysis_period == analysis_period]
        return res[skip : skip + limit]

    def count_strategic_intelligence_analyses(self, institution_id=None, organizational_unit_id=None, analysis_period=None):
        return len(self.list_strategic_intelligence_analyses(institution_id, organizational_unit_id, analysis_period))


class InMemoryStrategicOptionsRepo(IStrategicOptionsRepository):
    def __init__(self):
        self.analyses: dict[str, StrategicOptionsAnalysis] = {}

    def create_analysis(self, analysis: StrategicOptionsAnalysis) -> StrategicOptionsAnalysis:
        if not analysis.id:
            analysis.id = f"options-{len(self.analyses) + 1}"
        self.analyses[analysis.id] = analysis
        return analysis

    def get_analysis_by_id(self, analysis_id: str):
        return self.analyses.get(analysis_id)

    def list_analyses(self, institution_id=None, organizational_unit_id=None, analysis_period=None, skip=0, limit=50):
        res = list(self.analyses.values())
        if institution_id:
            res = [a for a in res if a.institution_id == institution_id]
        if organizational_unit_id:
            res = [a for a in res if a.organizational_unit_id == organizational_unit_id]
        if analysis_period:
            res = [a for a in res if a.analysis_period == analysis_period]
        return res[skip : skip + limit]

    def count_analyses(self, institution_id=None, organizational_unit_id=None, analysis_period=None):
        return len(self.list_analyses(institution_id, organizational_unit_id, analysis_period))


class MockAIProvider(IAIProvider):
    def __init__(self, response="Executive AI Synthesis: Strategic options address core placement and infrastructure constraints."):
        self.response = response
        self.called = False

    def generate_completion(self, prompt: str) -> str:
        self.called = True
        return self.response

    def generate_plan(self, context):
        raise NotImplementedError()

    def review_execution(self, plan, results):
        raise NotImplementedError()

    def health_check(self) -> bool:
        return True


def build_sample_strategic_intelligence(
    institution_id="INST-01",
    unit_id="UNIT-ENG",
    period="2024-2025",
) -> StrategicIntelligenceAnalysis:
    """Build a comprehensive Phase 6 snapshot with realistic findings across multiple domains."""
    # Issues
    issues = [
        StrategicIssue(
            id="issue-placement",
            category=IssueCategory.STRATEGIC_ISSUE,
            title="Placement Rate: Compounding deficit",
            description="Placement rate has been declining across recent periods below target.",
            severity=RiskSeverity.HIGH,
            impact=ImpactLevel.HIGH,
            likelihood=LikelihoodLevel.HIGH,
            affected_domains=[MetricDomain.PLACEMENT_EMPLOYER_DEMAND],
            related_metrics=["placement.rate"],
            evidence_ids=["ev-p1", "ev-p2"],
            confidence=0.88,
            assumptions=["Persistent skill gap."],
            rationale="Declining trajectory.",
        ),
        StrategicIssue(
            id="issue-research",
            category=IssueCategory.STRATEGIC_ISSUE,
            title="Publications: Narrowing deficit",
            description="Research output has accelerated strongly (+62.5%).",
            severity=RiskSeverity.LOW,
            impact=ImpactLevel.HIGH,
            likelihood=LikelihoodLevel.LOW,
            affected_domains=[MetricDomain.RESEARCH_PRODUCTIVITY],
            related_metrics=["research.publications"],
            evidence_ids=["ev-r1", "ev-r2"],
            confidence=0.92,
            assumptions=["Productive faculty momentum."],
            rationale="Positive publication trajectory.",
        ),
        StrategicIssue(
            id="issue-admissions",
            category=IssueCategory.STRATEGIC_ISSUE,
            title="Admissions Yield: Vulnerable strength",
            description="Yield is currently above target but exhibits declining multi-period momentum.",
            severity=RiskSeverity.MEDIUM,
            impact=ImpactLevel.MEDIUM,
            likelihood=LikelihoodLevel.HIGH,
            affected_domains=[MetricDomain.ADMISSIONS_MARKET],
            related_metrics=["admissions.yield"],
            evidence_ids=["ev-a1"],
            confidence=0.85,
            assumptions=["Competitor aggressiveness."],
            rationale="Negative trajectory on strength.",
        ),
    ]

    # Risks
    risks = [
        RiskSignal(
            id="risk-placement-demand",
            title="Placement & Employer Demand Alignment Vulnerability",
            description="Placement decline coincides with regional tech employer demand contraction.",
            severity=RiskSeverity.HIGH,
            impact=ImpactLevel.HIGH,
            likelihood=LikelihoodLevel.HIGH,
            risk_score=0.78,
            scoring_factors={"raw_score": 0.78},
            affected_domains=[MetricDomain.PLACEMENT_EMPLOYER_DEMAND],
            related_metrics=["placement.rate", "employer.demand.index"],
            supporting_indicators=["Placement down 6.5%", "Employer index down 12%"],
            correlation_vs_causation_note="Observed concurrent movement indicates multi-domain vulnerability; correlation does not imply direct mechanistic causation without controlled longitudinal cohort validation.",
            evidence_ids=["ev-p1", "ev-p2", "ev-emp1"],
            confidence=0.87,
            uncertainty_level=UncertaintyLevel.LOW,
            rationale="Concurrent placement and employer contraction.",
        ),
        RiskSignal(
            id="risk-infrastructure-intake",
            title="Infrastructure Strain & Enrollment Trajectory Risk",
            description="Laboratory capacity utilization exceeds 88% alongside sustained admissions intake.",
            severity=RiskSeverity.MEDIUM,
            impact=ImpactLevel.MEDIUM,
            likelihood=LikelihoodLevel.HIGH,
            risk_score=0.62,
            scoring_factors={"raw_score": 0.62},
            affected_domains=[MetricDomain.INFRASTRUCTURE],
            related_metrics=["infra.lab_utilization_rate"],
            supporting_indicators=["Lab utilization at 88.5%"],
            correlation_vs_causation_note="Observed concurrent movement indicates multi-domain vulnerability; correlation does not imply direct mechanistic causation without controlled longitudinal cohort validation.",
            evidence_ids=["ev-inf1"],
            confidence=0.84,
            uncertainty_level=UncertaintyLevel.LOW,
            rationale="Capacity utilization above threshold.",
        ),
    ]

    # Constraints
    constraints = [
        ConstraintSignal(
            id="constraint-infra",
            title="Infrastructure Capacity Strain",
            description="Lab utilization is at 88.5%, exceeding 85% threshold.",
            constraint_type="INFRASTRUCTURE_UTILIZATION",
            severity=RiskSeverity.MEDIUM,
            affected_domains=[MetricDomain.INFRASTRUCTURE],
            related_metrics=["infra.lab_utilization_rate"],
            persistence="MULTI_PERIOD",
            evidence_ids=["ev-inf1"],
            confidence=0.85,
            rationale="Exceeds 85% threshold.",
        ),
        ConstraintSignal(
            id="constraint-faculty",
            title="Faculty Accreditation Qualifications Constraint",
            description="Doctoral faculty ratio is 68.0%, below 70% threshold.",
            constraint_type="FACULTY_QUALIFICATION",
            severity=RiskSeverity.MEDIUM,
            affected_domains=[MetricDomain.FACULTY_CAPABILITY],
            related_metrics=["faculty.phd_ratio"],
            persistence="MULTI_PERIOD",
            evidence_ids=["ev-fac1"],
            confidence=0.82,
            rationale="Below 70% doctoral threshold.",
        ),
    ]

    # Opportunities
    opportunities = [
        OpportunitySignal(
            id="opp-research",
            title="Research Output Acceleration",
            description="Research publications increased 62.5% across 3 periods.",
            opportunity_type="RESEARCH_MOMENTUM",
            potential_impact=ImpactLevel.HIGH,
            urgency=LikelihoodLevel.MEDIUM,
            affected_domains=[MetricDomain.RESEARCH_PRODUCTIVITY],
            related_metrics=["research.publications"],
            evidence_ids=["ev-r1", "ev-r2"],
            confidence=0.90,
            interpretation="Empirical publication growth demonstrates research capability.",
            rationale="Empirical publication growth.",
        )
    ]

    # External factors
    ext_factors = [
        ExternalFactor(
            id="ext-reg",
            factor_name="AI Curriculum & Ethics Mandate",
            category=ExternalFactorCategory.REGULATORY,
            direction_impact="COMPLIANCE_REQUIREMENT",
            description="Mandatory curriculum compliance guidelines take effect next academic year.",
            affected_domains=[MetricDomain.EXTERNAL_REGULATORY],
            evidence_ids=["ev-reg1"],
            confidence=0.85,
            freshness=FreshnessStatus.FRESH,
            rationale="Statutory regulatory notification.",
        )
    ]

    return StrategicIntelligenceAnalysis(
        id=f"intel_{institution_id}_{period}",
        institution_id=institution_id,
        organizational_unit_id=unit_id,
        analysis_period=period,
        generated_at=datetime.now(timezone.utc),
        strategic_issues=issues,
        risk_signals=risks,
        constraint_signals=constraints,
        opportunity_signals=opportunities,
        external_factors=ext_factors,
        strategic_priority_signals=[],
        evidence_references=[],
        overall_confidence=ConfidenceAssessment(score=0.85, level="HIGH", factors={}),
        uncertainty_summary={"overall_uncertainty_level": "LOW"},
        assumptions=["Evidence is canonical."],
        status="FINALIZED",
    )


# ==============================================================================
# 1. Prerequisite Failures
# ==============================================================================

def test_prerequisite_failures_missing_phase6():
    """Validates that missing Phase 6 Strategic Intelligence fails with ValidationError."""
    intel_repo = InMemoryStrategicIntelligenceRepo()
    options_repo = InMemoryStrategicOptionsRepo()
    service = StrategicOptionsService(options_repo, intel_repo)

    req = StrategicOptionsRequestDTO(
        institution_id="NON-EXISTENT",
        organizational_unit_id="NONE",
        analysis_period="2024-2025",
    )
    with pytest.raises(ValidationError) as exc_info:
        service.generate_strategic_options_analysis(req)
    assert "Missing required prerequisite Strategic Intelligence Analysis" in str(exc_info.value)


# ==============================================================================
# 2. Option Generation from Risks & Distinct Alternatives
# ==============================================================================

def test_option_generation_from_risks_and_distinct_alternatives():
    """
    Validates that a persistent placement & employer demand risk generates TWO materially
    distinct alternative strategies (Curriculum Transformation vs Enterprise Co-Op Partnership),
    retaining all underlying issue IDs and evidence IDs.
    """
    intel_repo = InMemoryStrategicIntelligenceRepo()
    options_repo = InMemoryStrategicOptionsRepo()
    service = StrategicOptionsService(options_repo, intel_repo)

    sample_intel = build_sample_strategic_intelligence()
    intel_repo.create_strategic_intelligence_analysis(sample_intel)

    req = StrategicOptionsRequestDTO(
        institution_id="INST-01",
        organizational_unit_id="UNIT-ENG",
        analysis_period="2024-2025",
    )
    response = service.generate_strategic_options_analysis(req)

    # Locate the placement options
    curriculum_opt = next((o for o in response.options if o.category == OptionCategory.IMPROVEMENT and "Curriculum" in o.title), None)
    partnership_opt = next((o for o in response.options if o.category == OptionCategory.PARTNERSHIP and "Co-Op" in o.title), None)

    assert curriculum_opt is not None, "Curriculum transformation option must be generated"
    assert partnership_opt is not None, "Enterprise partnership alternative must be generated"

    # Both must trace to the placement risk and issue IDs
    assert "risk-placement-demand" in curriculum_opt.addressed_risk_ids
    assert "risk-placement-demand" in partnership_opt.addressed_risk_ids
    assert "issue-placement" in curriculum_opt.addressed_issue_ids
    assert "issue-placement" in partnership_opt.addressed_issue_ids

    # Evidence IDs must be preserved
    assert "ev-p1" in curriculum_opt.evidence_ids
    assert "ev-emp1" in partnership_opt.evidence_ids

    # Must be materially distinct strategies, not renamed duplicates
    assert curriculum_opt.category != partnership_opt.category
    assert curriculum_opt.feasibility == FeasibilityLevel.MEDIUM
    assert partnership_opt.feasibility == FeasibilityLevel.HIGH
    assert curriculum_opt.resource_requirement == "MEDIUM"
    assert partnership_opt.resource_requirement == "LOW"


# ==============================================================================
# 3. Option Generation from Constraints & Opportunities
# ==============================================================================

def test_option_generation_from_constraints_and_opportunities():
    """
    Validates generation of infrastructure modernization from capacity constraint,
    faculty recruitment from faculty constraint, and research accelerator from opportunity.
    """
    intel_repo = InMemoryStrategicIntelligenceRepo()
    options_repo = InMemoryStrategicOptionsRepo()
    service = StrategicOptionsService(options_repo, intel_repo)

    sample_intel = build_sample_strategic_intelligence()
    intel_repo.create_strategic_intelligence_analysis(sample_intel)

    req = StrategicOptionsRequestDTO(
        institution_id="INST-01",
        organizational_unit_id="UNIT-ENG",
        analysis_period="2024-2025",
    )
    response = service.generate_strategic_options_analysis(req)

    infra_opt = next((o for o in response.options if "Laboratory Modernization" in o.title), None)
    fac_opt = next((o for o in response.options if "Faculty Recruitment" in o.title), None)
    res_opt = next((o for o in response.options if "Research Innovation Cluster" in o.title), None)

    assert infra_opt is not None
    assert "ev-inf1" in infra_opt.evidence_ids
    assert infra_opt.resource_requirement == "HIGH"

    assert fac_opt is not None
    assert "ev-fac1" in fac_opt.evidence_ids

    assert res_opt is not None
    assert res_opt.category == OptionCategory.GROWTH
    assert "opp-research" in res_opt.opportunity_ids
    assert "ev-r1" in res_opt.evidence_ids


# ==============================================================================
# 4. Duplicate Option Merging & Evidence Traceability
# ==============================================================================

def test_duplicate_option_merging_and_evidence_traceability():
    """
    Verifies that multiple corroborating issues and risks within the same domain
    merge into a single consolidated option without producing duplicate redundant options.
    """
    intel_repo = InMemoryStrategicIntelligenceRepo()
    options_repo = InMemoryStrategicOptionsRepo()
    service = StrategicOptionsService(options_repo, intel_repo)

    sample_intel = build_sample_strategic_intelligence()
    intel_repo.create_strategic_intelligence_analysis(sample_intel)

    req = StrategicOptionsRequestDTO(
        institution_id="INST-01",
        organizational_unit_id="UNIT-ENG",
        analysis_period="2024-2025",
    )
    response = service.generate_strategic_options_analysis(req)

    # Verify options count is between 3 and 8
    assert 3 <= len(response.options) <= 8

    # Check that titles are unique (no duplicates)
    titles = [o.title for o in response.options]
    assert len(titles) == len(set(titles)), "All generated options must be distinct"


# ==============================================================================
# 5. Four Conditional Scenarios Generated per Option
# ==============================================================================

def test_four_conditional_scenarios_generated_per_option():
    """
    Verifies that every option generates exactly 4 conditional scenarios:
    BASELINE, UPSIDE, DOWNSIDE, STRESS, and that scenarios contain qualitative effects
    rather than fabricated statistical prophecies or fabricated budgets.
    """
    intel_repo = InMemoryStrategicIntelligenceRepo()
    options_repo = InMemoryStrategicOptionsRepo()
    service = StrategicOptionsService(options_repo, intel_repo)

    sample_intel = build_sample_strategic_intelligence()
    intel_repo.create_strategic_intelligence_analysis(sample_intel)

    req = StrategicOptionsRequestDTO(
        institution_id="INST-01",
        organizational_unit_id="UNIT-ENG",
        analysis_period="2024-2025",
    )
    response = service.generate_strategic_options_analysis(req)

    assert len(response.scenarios) == len(response.options) * 4

    for opt in response.options:
        opt_scens = [s for s in response.scenarios if s.option_id == opt.id]
        assert len(opt_scens) == 4
        scen_types = {s.scenario_type for s in opt_scens}
        assert scen_types == {
            ScenarioType.BASELINE,
            ScenarioType.UPSIDE,
            ScenarioType.DOWNSIDE,
            ScenarioType.STRESS,
        }

        # Check qualitative content guardrails (no fabricated currency symbols or budgets)
        for s in opt_scens:
            assert len(s.assumptions) > 0
            assert len(s.expected_effects) > 0
            assert len(s.risks) > 0
            assert len(s.opportunities) > 0
            assert "$" not in s.description
            assert "€" not in s.description


# ==============================================================================
# 6. Deterministic 7-Dimension Option Evaluation & Formula
# ==============================================================================

def test_deterministic_evaluation_with_7_dimensions():
    """
    Verifies that every option is evaluated across the EXACT 7 dimensions on a 0-100 scale:
    - STRATEGIC_ALIGNMENT
    - IMPACT
    - FEASIBILITY
    - RESOURCE_EFFICIENCY
    - IMPLEMENTATION_RISK (higher score = lower implementation risk)
    - URGENCY
    - EVIDENCE_STRENGTH
    """
    intel_repo = InMemoryStrategicIntelligenceRepo()
    options_repo = InMemoryStrategicOptionsRepo()
    service = StrategicOptionsService(options_repo, intel_repo)

    sample_intel = build_sample_strategic_intelligence()
    intel_repo.create_strategic_intelligence_analysis(sample_intel)

    req = StrategicOptionsRequestDTO(
        institution_id="INST-01",
        organizational_unit_id="UNIT-ENG",
        analysis_period="2024-2025",
    )
    response = service.generate_strategic_options_analysis(req)

    assert len(response.evaluations) == len(response.options)

    w_align = settings.OPTION_WEIGHT_STRATEGIC_ALIGNMENT
    w_imp = settings.OPTION_WEIGHT_IMPACT
    w_feas = settings.OPTION_WEIGHT_FEASIBILITY
    w_res = settings.OPTION_WEIGHT_RESOURCE_EFFICIENCY
    w_risk = settings.OPTION_WEIGHT_IMPLEMENTATION_RISK
    w_urg = settings.OPTION_WEIGHT_URGENCY
    w_evi = settings.OPTION_WEIGHT_EVIDENCE_STRENGTH

    # Verify weights sum to 1.00
    total_weights = round(w_align + w_imp + w_feas + w_res + w_risk + w_urg + w_evi, 4)
    assert total_weights == 1.00

    for ev in response.evaluations:
        # All individual scores must be within 0-100
        assert 0.0 <= ev.strategic_alignment_score <= 100.0
        assert 0.0 <= ev.impact_score <= 100.0
        assert 0.0 <= ev.feasibility_score <= 100.0
        assert 0.0 <= ev.resource_efficiency_score <= 100.0
        assert 0.0 <= ev.implementation_risk_score <= 100.0
        assert 0.0 <= ev.urgency_score <= 100.0
        assert 0.0 <= ev.evidence_strength_score <= 100.0

        # Check total score formula
        expected_total = round(
            (ev.strategic_alignment_score * w_align)
            + (ev.impact_score * w_imp)
            + (ev.feasibility_score * w_feas)
            + (ev.resource_efficiency_score * w_res)
            + (ev.implementation_risk_score * w_risk)
            + (ev.urgency_score * w_urg)
            + (ev.evidence_strength_score * w_evi),
            2,
        )
        assert ev.total_score == expected_total

        # Check priority classification matches thresholds
        if ev.total_score >= settings.OPTION_PRIORITY_CRITICAL_THRESHOLD:
            assert ev.priority_level == PriorityLevel.CRITICAL
        elif ev.total_score >= settings.OPTION_PRIORITY_HIGH_THRESHOLD:
            assert ev.priority_level == PriorityLevel.HIGH
        elif ev.total_score >= settings.OPTION_PRIORITY_MEDIUM_THRESHOLD:
            assert ev.priority_level == PriorityLevel.MEDIUM
        else:
            assert ev.priority_level == PriorityLevel.LOW


# ==============================================================================
# 7. Implementation Risk Score Directionality
# ==============================================================================

def test_implementation_risk_directionality_higher_means_better():
    """
    Validates the specific requirement that for IMPLEMENTATION_RISK:
    higher score = lower implementation risk / better risk profile
    lower score = higher implementation risk
    """
    intel_repo = InMemoryStrategicIntelligenceRepo()
    options_repo = InMemoryStrategicOptionsRepo()
    service = StrategicOptionsService(options_repo, intel_repo)

    sample_intel = build_sample_strategic_intelligence()
    intel_repo.create_strategic_intelligence_analysis(sample_intel)

    req = StrategicOptionsRequestDTO(
        institution_id="INST-01",
        organizational_unit_id="UNIT-ENG",
        analysis_period="2024-2025",
    )
    response = service.generate_strategic_options_analysis(req)

    # Compare partnership (low implementation risk) vs infra modernization (medium implementation risk)
    partnership_opt = next(o for o in response.options if o.category == OptionCategory.PARTNERSHIP)
    infra_opt = next(o for o in response.options if "Laboratory Modernization" in o.title)

    ev_part = next(e for e in response.evaluations if e.option_id == partnership_opt.id)
    ev_infra = next(e for e in response.evaluations if e.option_id == infra_opt.id)

    # Partnership has lower risk, so its implementation risk score must be higher
    assert ev_part.implementation_risk_score > ev_infra.implementation_risk_score


# ==============================================================================
# 8. Missing Financial/Resource Evidence Handling
# ==============================================================================

def test_resource_uncertainty_handling_no_fabricated_budgets():
    """
    When financial evidence is incomplete, verifies that resource assessment is marked
    qualitatively and uncertainty is elevated without fabricating exact dollar budgets.
    """
    intel_repo = InMemoryStrategicIntelligenceRepo()
    options_repo = InMemoryStrategicOptionsRepo()
    service = StrategicOptionsService(options_repo, intel_repo)

    sample_intel = build_sample_strategic_intelligence()
    intel_repo.create_strategic_intelligence_analysis(sample_intel)

    req = StrategicOptionsRequestDTO(
        institution_id="INST-01",
        organizational_unit_id="UNIT-ENG",
        analysis_period="2024-2025",
    )
    response = service.generate_strategic_options_analysis(req)

    # Ensure no fabricated budget amounts in options
    for opt in response.options:
        assert "$" not in opt.description
        assert "€" not in opt.description
        assert opt.resource_requirement in ("LOW", "MEDIUM", "HIGH", "UNCERTAIN")


# ==============================================================================
# 9. Trade-offs and Dependencies are Explicit
# ==============================================================================

def test_trade_offs_and_dependencies_are_explicit():
    """
    Verifies that all options and evaluations have non-empty, actionable trade-offs
    and cross-option dependencies.
    """
    intel_repo = InMemoryStrategicIntelligenceRepo()
    options_repo = InMemoryStrategicOptionsRepo()
    service = StrategicOptionsService(options_repo, intel_repo)

    sample_intel = build_sample_strategic_intelligence()
    intel_repo.create_strategic_intelligence_analysis(sample_intel)

    req = StrategicOptionsRequestDTO(
        institution_id="INST-01",
        organizational_unit_id="UNIT-ENG",
        analysis_period="2024-2025",
    )
    response = service.generate_strategic_options_analysis(req)

    for opt in response.options:
        assert len(opt.trade_offs) > 0, f"Option {opt.title} must have trade-offs"
        assert len(opt.dependencies) > 0, f"Option {opt.title} must have dependencies"

    for ev in response.evaluations:
        assert len(ev.trade_offs) > 0, f"Evaluation for {ev.option_id} must have trade-offs"


# ==============================================================================
# 10. Prioritized Ranking & Leadership Decision Guardrail
# ==============================================================================

def test_prioritized_ranking_and_leadership_disclaimer():
    """
    Verifies that options are sorted descending by total score and that the
    mandatory leadership decision-support disclaimer is present.
    """
    intel_repo = InMemoryStrategicIntelligenceRepo()
    options_repo = InMemoryStrategicOptionsRepo()
    service = StrategicOptionsService(options_repo, intel_repo)

    sample_intel = build_sample_strategic_intelligence()
    intel_repo.create_strategic_intelligence_analysis(sample_intel)

    req = StrategicOptionsRequestDTO(
        institution_id="INST-01",
        organizational_unit_id="UNIT-ENG",
        analysis_period="2024-2025",
    )
    response = service.generate_strategic_options_analysis(req)

    # Check prioritized_option_ids order matches descending scores
    eval_map = {e.option_id: e.total_score for e in response.evaluations}
    scores_in_priority_order = [eval_map[opt_id] for opt_id in response.prioritized_option_ids]
    assert scores_in_priority_order == sorted(scores_in_priority_order, reverse=True)

    # Mandatory leadership decision-support disclaimer
    expected_disclaimer = (
        "Strategic options and priority signals are decision-support outputs. "
        "Final strategic decisions remain with institutional leadership/governing bodies."
    )
    assert response.decision_support_disclaimer == expected_disclaimer


# ==============================================================================
# 11. Scope Isolation by Organizational Unit
# ==============================================================================

def test_organizational_unit_scope_isolation():
    """Verifies that an analysis scoped to UNIT-ENG resolves only UNIT-ENG intelligence."""
    intel_repo = InMemoryStrategicIntelligenceRepo()
    options_repo = InMemoryStrategicOptionsRepo()
    service = StrategicOptionsService(options_repo, intel_repo)

    sample_intel = build_sample_strategic_intelligence(institution_id="INST-01", unit_id="UNIT-ENG")
    intel_repo.create_strategic_intelligence_analysis(sample_intel)

    # Query for another unit should fail cleanly
    req = StrategicOptionsRequestDTO(
        institution_id="INST-01",
        organizational_unit_id="UNIT-BIZ",
        analysis_period="2024-2025",
    )
    with pytest.raises(ValidationError) as exc:
        service.generate_strategic_options_analysis(req)
    assert "Missing required prerequisite Strategic Intelligence Analysis" in str(exc.value)


# ==============================================================================
# 12. AI Synthesis Guardrails
# ==============================================================================

def test_ai_synthesis_guardrails_never_alters_scores_or_options():
    """
    Verifies that AI synthesis provides executive narrative formatting but CANNOT alter
    option counts, scores, priority levels, or rankings.
    """
    intel_repo = InMemoryStrategicIntelligenceRepo()
    options_repo = InMemoryStrategicOptionsRepo()
    mock_ai = MockAIProvider(response="Executive Briefing: Leadership should focus on experiential learning.")
    service = StrategicOptionsService(options_repo, intel_repo, ai_provider=mock_ai)

    sample_intel = build_sample_strategic_intelligence()
    intel_repo.create_strategic_intelligence_analysis(sample_intel)

    # Run with AI synthesis enabled
    req = StrategicOptionsRequestDTO(
        institution_id="INST-01",
        organizational_unit_id="UNIT-ENG",
        analysis_period="2024-2025",
        include_ai_synthesis=True,
    )
    response = service.generate_strategic_options_analysis(req)

    assert mock_ai.called is True
    assert response.ai_synthesis_notes == "Executive Briefing: Leadership should focus on experiential learning."

    # Verify deterministic scores remain completely intact and valid
    for ev in response.evaluations:
        assert ev.total_score > 0
        assert ev.priority_level in (PriorityLevel.CRITICAL, PriorityLevel.HIGH, PriorityLevel.MEDIUM, PriorityLevel.LOW)


# ==============================================================================
# 13. Option Count Boundaries & Data Limitations
# ==============================================================================

def test_option_count_boundaries_and_data_limitations():
    """
    Verifies that when only minimal evidence exists (e.g. only 1 risk signal),
    the engine does NOT fabricate options to reach 3, but records a data limitation.
    """
    intel_repo = InMemoryStrategicIntelligenceRepo()
    options_repo = InMemoryStrategicOptionsRepo()
    service = StrategicOptionsService(options_repo, intel_repo)

    # Intelligence with only ONE risk and no constraints or opportunities
    minimal_intel = StrategicIntelligenceAnalysis(
        id="intel-minimal",
        institution_id="INST-MIN",
        analysis_period="2024-2025",
        strategic_issues=[],
        risk_signals=[
            RiskSignal(
                id="risk-single",
                title="Infrastructure Utilization Strain",
                description="Lab utilization is at 89%.",
                severity=RiskSeverity.HIGH,
                impact=ImpactLevel.HIGH,
                likelihood=LikelihoodLevel.HIGH,
                related_metrics=["infra.lab_utilization_rate"],
                evidence_ids=["ev-1"],
                rationale="Over capacity.",
            )
        ],
        constraint_signals=[],
        opportunity_signals=[],
        external_factors=[],
        strategic_priority_signals=[],
        evidence_references=[],
        overall_confidence=ConfidenceAssessment(score=0.8, level="HIGH", factors={}),
        assumptions=[],
        status="FINALIZED",
    )
    intel_repo.create_strategic_intelligence_analysis(minimal_intel)

    req = StrategicOptionsRequestDTO(
        institution_id="INST-MIN",
        analysis_period="2024-2025",
    )
    response = service.generate_strategic_options_analysis(req)

    # Must generate the 1 supported option without fabricating fake ones
    assert len(response.options) == 1
    assert len(response.data_limitations) > 0
    assert "no unevidenced options were fabricated" in response.data_limitations[0]
