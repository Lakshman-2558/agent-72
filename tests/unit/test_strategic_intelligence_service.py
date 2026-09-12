"""Unit tests for Phase 6 Strategic Intelligence Service."""

from datetime import datetime, timezone, timedelta
import pytest

from agent72.application.dtos.strategic_intelligence_dto import StrategicIntelligenceRequestDTO
from agent72.application.services.strategic_intelligence_service import StrategicIntelligenceService
from agent72.core.config import settings
from agent72.core.exceptions import EntityNotFoundException, ValidationError
from agent72.domain.interfaces.ai_provider import IAIProvider
from agent72.domain.interfaces.analysis_repository import IAnalysisRepository
from agent72.domain.interfaces.evidence_repository import IEvidenceRepository
from agent72.domain.interfaces.organization_repository import IOrganizationRepository
from agent72.domain.interfaces.strategic_intelligence_repository import IStrategicIntelligenceRepository
from agent72.domain.interfaces.trajectory_repository import ITrajectoryRepository
from agent72.domain.models.analysis import (
    ConfidenceAssessment,
    CurrentPositionAnalysis,
    FindingCategory,
    FindingSeverity,
    MetricAssessment,
    PerformanceStatus,
    PositionFinding,
)
from agent72.domain.models.evidence import (
    FreshnessStatus,
    InstitutionalEvidence,
    MetricDefinition,
    MetricDirection,
    MetricDomain,
    QualityTier,
    SourceType,
)
from agent72.domain.models.organization import EntityStatus, Institution, OrganizationalUnit, UnitType
from agent72.domain.models.strategic_intelligence import (
    ImpactLevel,
    IssueCategory,
    LikelihoodLevel,
    RiskSeverity,
    StrategicIntelligenceAnalysis,
    UncertaintyLevel,
)
from agent72.domain.models.trajectory import (
    AccelerationStatus,
    ConsistencyRating,
    TrajectoryAnalysis,
    TrajectoryMetric,
    TrajectoryStatus,
)


class InMemoryStrategicIntelligenceRepo(IStrategicIntelligenceRepository):
    def __init__(self):
        self.analyses: dict[str, StrategicIntelligenceAnalysis] = {}

    def create_strategic_intelligence_analysis(self, analysis: StrategicIntelligenceAnalysis) -> StrategicIntelligenceAnalysis:
        if not analysis.id:
            analysis.id = f"strat-{len(self.analyses) + 1}"
        self.analyses[analysis.id] = analysis
        return analysis

    def get_strategic_intelligence_analysis_by_id(self, analysis_id: str):
        return self.analyses.get(analysis_id)

    def list_strategic_intelligence_analyses(self, institution_id=None, organizational_unit_id=None, analysis_period=None, skip=0, limit=50):
        items = list(self.analyses.values())
        if institution_id:
            items = [a for a in items if a.institution_id == institution_id]
        if organizational_unit_id:
            items = [a for a in items if a.organizational_unit_id == organizational_unit_id]
        if analysis_period:
            items = [a for a in items if a.analysis_period == analysis_period]
        return items[skip : skip + limit]

    def count_strategic_intelligence_analyses(self, institution_id=None, organizational_unit_id=None, analysis_period=None):
        return len(self.list_strategic_intelligence_analyses(institution_id, organizational_unit_id, analysis_period))


class InMemoryAnalysisRepo(IAnalysisRepository):
    def __init__(self):
        self.analyses: dict[str, CurrentPositionAnalysis] = {}

    def create_analysis(self, analysis: CurrentPositionAnalysis):
        if not analysis.id:
            analysis.id = f"pos-{len(self.analyses) + 1}"
        self.analyses[analysis.id] = analysis
        return analysis

    def get_analysis_by_id(self, analysis_id: str):
        return self.analyses.get(analysis_id)

    def list_analyses(self, institution_id=None, organizational_unit_id=None, analysis_period=None, skip=0, limit=50):
        items = list(self.analyses.values())
        if institution_id:
            items = [a for a in items if a.institution_id == institution_id]
        if organizational_unit_id:
            items = [a for a in items if a.organizational_unit_id == organizational_unit_id]
        if analysis_period:
            items = [a for a in items if a.analysis_period == analysis_period]
        return items[skip : skip + limit]

    def count_analyses(self, institution_id=None, organizational_unit_id=None, analysis_period=None):
        return len(self.list_analyses(institution_id, organizational_unit_id, analysis_period))


class InMemoryTrajectoryRepo(ITrajectoryRepository):
    def __init__(self):
        self.analyses: dict[str, TrajectoryAnalysis] = {}

    def create_trajectory_analysis(self, analysis: TrajectoryAnalysis):
        if not analysis.id:
            analysis.id = f"traj-{len(self.analyses) + 1}"
        self.analyses[analysis.id] = analysis
        return analysis

    def get_trajectory_analysis_by_id(self, analysis_id: str):
        return self.analyses.get(analysis_id)

    def list_trajectory_analyses(self, institution_id=None, organizational_unit_id=None, analysis_period=None, skip=0, limit=50):
        items = list(self.analyses.values())
        if institution_id:
            items = [a for a in items if a.institution_id == institution_id]
        if organizational_unit_id:
            items = [a for a in items if a.organizational_unit_id == organizational_unit_id]
        if analysis_period:
            items = [a for a in items if a.analysis_period == analysis_period]
        return items[skip : skip + limit]

    def count_trajectory_analyses(self, institution_id=None, organizational_unit_id=None, analysis_period=None):
        return len(self.list_trajectory_analyses(institution_id, organizational_unit_id, analysis_period))


class InMemoryEvidenceRepo(IEvidenceRepository):
    def __init__(self):
        self.metrics: dict[str, MetricDefinition] = {}
        self.evidence_list: list[InstitutionalEvidence] = []

    def create_metric_definition(self, definition: MetricDefinition) -> MetricDefinition:
        self.metrics[definition.metric_key] = definition
        return definition

    def get_metric_definition(self, metric_key: str):
        return self.metrics.get(metric_key)

    def list_metric_definitions(self, domain=None, skip=0, limit=100):
        items = list(self.metrics.values())
        if domain:
            items = [m for m in items if m.domain == domain]
        return items[skip : skip + limit]

    def find_existing_evidence(self, institution_id, idempotency_key):
        return None

    def record_evidence(self, evidence: InstitutionalEvidence) -> InstitutionalEvidence:
        if not evidence.id:
            evidence.id = f"ev-{len(self.evidence_list) + 1}"
        self.evidence_list.append(evidence)
        return evidence

    def record_evidence_batch(self, batch: list[InstitutionalEvidence]):
        for e in batch:
            self.record_evidence(e)
        return batch

    def create_evidence(self, evidence: InstitutionalEvidence):
        return self.record_evidence(evidence)

    def query_evidence(
        self,
        institution_id: str,
        unit_id=None,
        metric_key=None,
        domain=None,
        period=None,
        as_of_date_start=None,
        as_of_date_end=None,
        source_type=None,
        source_name=None,
        quality_tier=None,
        skip: int = 0,
        limit: int = 500,
    ):
        res = [e for e in self.evidence_list if e.institution_id == institution_id]
        if unit_id:
            res = [e for e in res if e.unit_id == unit_id]
        if metric_key:
            res = [e for e in res if e.metric_key == metric_key]
        if domain:
            res = [e for e in res if e.domain == domain]
        if period:
            res = [e for e in res if e.period == period]
        return res[skip : skip + limit]

    def get_latest_evidence(self, institution_id: str, metric_key: str, unit_id=None):
        filtered = [
            e for e in self.evidence_list
            if e.institution_id == institution_id and e.metric_key == metric_key
        ]
        if unit_id:
            filtered = [e for e in filtered if e.organizational_unit_id == unit_id]
        return filtered[-1] if filtered else None

    def get_historical_series(self, institution_id: str, metric_key: str, unit_id=None, skip: int = 0, limit: int = 50):
        filtered = [
            e for e in self.evidence_list
            if e.institution_id == institution_id and e.metric_key == metric_key
        ]
        if unit_id:
            filtered = [e for e in filtered if e.organizational_unit_id == unit_id]
        return filtered[skip : skip + limit]

    def get_evidence_by_domain(self, institution_id: str, domain: MetricDomain, period=None, skip: int = 0, limit: int = 50):
        filtered = [
            e for e in self.evidence_list
            if e.institution_id == institution_id and e.domain == domain
        ]
        if period:
            filtered = [e for e in filtered if e.period == period]
        return filtered[skip : skip + limit]

    def record_batch_log(self, batch_log):
        return batch_log

    def get_batch_log(self, batch_id: str):
        return None

    def find_by_batch_id(self, batch_id: str):
        return []



class InMemoryOrganizationRepo(IOrganizationRepository):
    def __init__(self):
        self.institutions: dict[str, Institution] = {}
        self.units: dict[str, OrganizationalUnit] = {}

    def get_institution_by_id(self, institution_id: str):
        return self.institutions.get(institution_id)

    def get_institution_by_code(self, code: str):
        return next((i for i in self.institutions.values() if i.code == code), None)

    def create_institution(self, institution: Institution):
        if not institution.id:
            institution.id = f"inst-{len(self.institutions) + 1}"
        self.institutions[institution.id] = institution
        return institution

    def list_institutions(self, status=None, skip=0, limit=50):
        return list(self.institutions.values())[skip : skip + limit]

    def count_institutions(self, status=None):
        return len(self.institutions)

    def get_unit_by_id(self, unit_id: str):
        return self.units.get(unit_id)

    def create_unit(self, unit: OrganizationalUnit):
        if not unit.id:
            unit.id = f"unit-{len(self.units) + 1}"
        self.units[unit.id] = unit
        return unit

    def list_units_by_institution(self, institution_id: str, status=None):
        return [u for u in self.units.values() if u.institution_id == institution_id]


from agent72.infrastructure.ai.mock_provider import MockAIProvider


@pytest.fixture
def repos():
    strat_repo = InMemoryStrategicIntelligenceRepo()
    analysis_repo = InMemoryAnalysisRepo()
    traj_repo = InMemoryTrajectoryRepo()
    ev_repo = InMemoryEvidenceRepo()
    org_repo = InMemoryOrganizationRepo()
    ai_provider = MockAIProvider(model_name="mock-strat-intel")

    # Create test institution & unit
    inst = org_repo.create_institution(
        Institution(id="inst-test-1", code="TEST-U", name="Test University", status=EntityStatus.ACTIVE)
    )
    unit = org_repo.create_unit(
        OrganizationalUnit(id="unit-test-1", institution_id=inst.id, code="TEST-ENG", name="Engineering", unit_type=UnitType.SCHOOL, status=EntityStatus.ACTIVE)
    )

    # Register metric definitions
    ev_repo.create_metric_definition(
        MetricDefinition(
            metric_key="placement.rate",
            name="Placement Rate",
            domain=MetricDomain.PLACEMENT_EMPLOYER_DEMAND,
            direction=MetricDirection.HIGHER_IS_BETTER,
        )
    )
    ev_repo.create_metric_definition(
        MetricDefinition(
            metric_key="academic.dropout.rate",
            name="Dropout Rate",
            domain=MetricDomain.ACADEMIC_PERFORMANCE,
            direction=MetricDirection.LOWER_IS_BETTER,
        )
    )
    ev_repo.create_metric_definition(
        MetricDefinition(
            metric_key="admissions.yield",
            name="Admissions Yield",
            domain=MetricDomain.ADMISSIONS_MARKET,
            direction=MetricDirection.HIGHER_IS_BETTER,
        )
    )
    ev_repo.create_metric_definition(
        MetricDefinition(
            metric_key="research.publications",
            name="Publications",
            domain=MetricDomain.RESEARCH_PRODUCTIVITY,
            direction=MetricDirection.HIGHER_IS_BETTER,
        )
    )
    ev_repo.create_metric_definition(
        MetricDefinition(
            metric_key="infra.lab.utilization",
            name="Lab Utilization",
            domain=MetricDomain.INFRASTRUCTURE,
            direction=MetricDirection.HIGHER_IS_BETTER,
        )
    )
    ev_repo.create_metric_definition(
        MetricDefinition(
            metric_key="faculty.phd.ratio",
            name="Faculty PhD Ratio",
            domain=MetricDomain.FACULTY_CAPABILITY,
            direction=MetricDirection.HIGHER_IS_BETTER,
        )
    )
    ev_repo.create_metric_definition(
        MetricDefinition(
            metric_key="faculty.student.ratio",
            name="Student Faculty Ratio",
            domain=MetricDomain.FACULTY_CAPABILITY,
            direction=MetricDirection.LOWER_IS_BETTER,
        )
    )

    service = StrategicIntelligenceService(
        strategic_intelligence_repository=strat_repo,
        analysis_repository=analysis_repo,
        trajectory_repository=traj_repo,
        evidence_repository=ev_repo,
        organization_repository=org_repo,
        ai_provider=ai_provider,
    )

    return {
        "service": service,
        "strat_repo": strat_repo,
        "analysis_repo": analysis_repo,
        "traj_repo": traj_repo,
        "ev_repo": ev_repo,
        "org_repo": org_repo,
        "ai_provider": ai_provider,
        "inst": inst,
        "unit": unit,
    }


def test_prerequisite_failures_missing_phase4_and_phase5(repos):
    service = repos["service"]
    inst = repos["inst"]
    unit = repos["unit"]

    # Fails if Phase 4 doesn't exist
    with pytest.raises(ValidationError, match=r"Prerequisite Current Position Analysis \(Phase 4\) not found"):
        service.generate_strategic_intelligence_analysis(
            StrategicIntelligenceRequestDTO(
                institution_id=inst.id,
                organizational_unit_id=unit.id,
                analysis_period="2024-2025",
            )
        )


def test_gap_plus_declining_trajectory_compounding_deficit(repos):
    service = repos["service"]
    inst = repos["inst"]
    unit = repos["unit"]
    analysis_repo = repos["analysis_repo"]
    traj_repo = repos["traj_repo"]

    # Phase 4: placement below target
    pos = analysis_repo.create_analysis(
        CurrentPositionAnalysis(
            institution_id=inst.id,
            organizational_unit_id=unit.id,
            analysis_period="2024-2025",
            key_metrics=[
                MetricAssessment(
                    metric_key="placement.rate",
                    metric_name="Placement Rate",
                    domain=MetricDomain.PLACEMENT_EMPLOYER_DEMAND,
                    direction=MetricDirection.HIGHER_IS_BETTER,
                    unit="percent",
                    latest_value=72.0,
                    target_value=85.0,
                    target_variance=-13.0,
                    performance_status=PerformanceStatus.BELOW_TARGET,
                    confidence_score=0.9,
                )
            ],
            gaps=[
                PositionFinding(
                    id="gap-1",
                    category=FindingCategory.GAP,
                    metric_key="placement.rate",
                    title="Placement Gap",
                    description="Placement is 13% below target.",
                    severity=FindingSeverity.HIGH,
                )
            ],
            overall_confidence=ConfidenceAssessment(score=0.9, level="HIGH", factors={}, explanation="Verified"),
        )
    )

    # Phase 5: declining trajectory
    traj = traj_repo.create_trajectory_analysis(
        TrajectoryAnalysis(
            institution_id=inst.id,
            organizational_unit_id=unit.id,
            analysis_period="2024-2025",
            overall_trajectory_status=TrajectoryStatus.DECLINING,
            metric_trends=[
                TrajectoryMetric(
                    metric_key="placement.rate",
                    metric_name="Placement Rate",
                    domain=MetricDomain.PLACEMENT_EMPLOYER_DEMAND,
                    direction=MetricDirection.HIGHER_IS_BETTER,
                    earliest_value=85.0,
                    latest_value=72.0,
                    percentage_change=-15.3,
                    trend_status=TrajectoryStatus.DECLINING,
                    consistency=ConsistencyRating.HIGH,
                    acceleration=AccelerationStatus.CONSTANT_VELOCITY,
                    confidence_score=0.9,
                )
            ],
            overall_confidence=ConfidenceAssessment(score=0.9, level="HIGH", factors={}, explanation="Verified"),
        )
    )

    result = service.generate_strategic_intelligence_analysis(
        StrategicIntelligenceRequestDTO(
            institution_id=inst.id,
            organizational_unit_id=unit.id,
            analysis_period="2024-2025",
            current_position_analysis_id=pos.id,
            trajectory_analysis_id=traj.id,
        )
    )

    # Should detect Compounding Deficit
    issues = [i for i in result.strategic_issues if "Compounding deficit" in i.title]
    assert len(issues) == 1
    assert issues[0].severity == RiskSeverity.HIGH
    assert issues[0].impact == ImpactLevel.HIGH


def test_gap_plus_improving_trajectory_narrowing_deficit(repos):
    service = repos["service"]
    inst = repos["inst"]
    unit = repos["unit"]
    analysis_repo = repos["analysis_repo"]
    traj_repo = repos["traj_repo"]

    # Phase 4: placement below target
    pos = analysis_repo.create_analysis(
        CurrentPositionAnalysis(
            institution_id=inst.id,
            organizational_unit_id=unit.id,
            analysis_period="2024-2025",
            key_metrics=[
                MetricAssessment(
                    metric_key="placement.rate",
                    metric_name="Placement Rate",
                    domain=MetricDomain.PLACEMENT_EMPLOYER_DEMAND,
                    direction=MetricDirection.HIGHER_IS_BETTER,
                    unit="percent",
                    latest_value=80.0,
                    target_value=85.0,
                    target_variance=-5.0,
                    performance_status=PerformanceStatus.BELOW_TARGET,
                    confidence_score=0.9,
                )
            ],
            gaps=[
                PositionFinding(
                    id="gap-1",
                    category=FindingCategory.GAP,
                    metric_key="placement.rate",
                    title="Placement Gap",
                    description="Placement is 5% below target.",
                    severity=FindingSeverity.MEDIUM,
                )
            ],
            overall_confidence=ConfidenceAssessment(score=0.9, level="HIGH", factors={}, explanation="Verified"),
        )
    )

    # Phase 5: improving trajectory
    traj = traj_repo.create_trajectory_analysis(
        TrajectoryAnalysis(
            institution_id=inst.id,
            organizational_unit_id=unit.id,
            analysis_period="2024-2025",
            overall_trajectory_status=TrajectoryStatus.IMPROVING,
            metric_trends=[
                TrajectoryMetric(
                    metric_key="placement.rate",
                    metric_name="Placement Rate",
                    domain=MetricDomain.PLACEMENT_EMPLOYER_DEMAND,
                    direction=MetricDirection.HIGHER_IS_BETTER,
                    earliest_value=70.0,
                    latest_value=80.0,
                    percentage_change=+14.3,
                    trend_status=TrajectoryStatus.IMPROVING,
                    consistency=ConsistencyRating.HIGH,
                    acceleration=AccelerationStatus.ACCELERATING,
                    confidence_score=0.9,
                )
            ],
            overall_confidence=ConfidenceAssessment(score=0.9, level="HIGH", factors={}, explanation="Verified"),
        )
    )

    result = service.generate_strategic_intelligence_analysis(
        StrategicIntelligenceRequestDTO(
            institution_id=inst.id,
            organizational_unit_id=unit.id,
            analysis_period="2024-2025",
            current_position_analysis_id=pos.id,
            trajectory_analysis_id=traj.id,
        )
    )

    # Should detect Narrowing Deficit
    issues = [i for i in result.strategic_issues if "Narrowing deficit" in i.title]
    assert len(issues) == 1
    assert issues[0].severity == RiskSeverity.MEDIUM
    assert "actively narrowing" in issues[0].rationale.lower()


def test_strength_plus_declining_trajectory_vulnerable_strength(repos):
    service = repos["service"]
    inst = repos["inst"]
    unit = repos["unit"]
    analysis_repo = repos["analysis_repo"]
    traj_repo = repos["traj_repo"]

    pos = analysis_repo.create_analysis(
        CurrentPositionAnalysis(
            institution_id=inst.id,
            organizational_unit_id=unit.id,
            analysis_period="2024-2025",
            key_metrics=[
                MetricAssessment(
                    metric_key="research.publications",
                    metric_name="Publications",
                    domain=MetricDomain.RESEARCH_PRODUCTIVITY,
                    direction=MetricDirection.HIGHER_IS_BETTER,
                    unit="count",
                    latest_value=120.0,
                    performance_status=PerformanceStatus.POSITIVE_PERFORMANCE,
                    confidence_score=0.9,
                )
            ],
            strengths=[
                PositionFinding(
                    id="str-1",
                    category=FindingCategory.STRENGTH,
                    metric_key="research.publications",
                    title="Research Publication Strength",
                    description="Strong research output.",
                    severity=FindingSeverity.LOW,
                )
            ],
            overall_confidence=ConfidenceAssessment(score=0.9, level="HIGH", factors={}, explanation="Verified"),
        )
    )

    traj = traj_repo.create_trajectory_analysis(
        TrajectoryAnalysis(
            institution_id=inst.id,
            organizational_unit_id=unit.id,
            analysis_period="2024-2025",
            overall_trajectory_status=TrajectoryStatus.DECLINING,
            metric_trends=[
                TrajectoryMetric(
                    metric_key="research.publications",
                    metric_name="Publications",
                    domain=MetricDomain.RESEARCH_PRODUCTIVITY,
                    direction=MetricDirection.HIGHER_IS_BETTER,
                    earliest_value=160.0,
                    latest_value=120.0,
                    percentage_change=-25.0,
                    trend_status=TrajectoryStatus.DECLINING,
                    consistency=ConsistencyRating.HIGH,
                    acceleration=AccelerationStatus.CONSTANT_VELOCITY,
                    confidence_score=0.9,
                )
            ],
            overall_confidence=ConfidenceAssessment(score=0.9, level="HIGH", factors={}, explanation="Verified"),
        )
    )

    result = service.generate_strategic_intelligence_analysis(
        StrategicIntelligenceRequestDTO(
            institution_id=inst.id,
            organizational_unit_id=unit.id,
            analysis_period="2024-2025",
            current_position_analysis_id=pos.id,
            trajectory_analysis_id=traj.id,
        )
    )

    # Should detect Vulnerable Institutional Strength
    issues = [i for i in result.strategic_issues if "Vulnerable institutional strength" in i.title]
    assert len(issues) == 1
    assert issues[0].severity == RiskSeverity.HIGH


def test_structural_multi_metric_risks_and_correlation_causation(repos):
    service = repos["service"]
    inst = repos["inst"]
    unit = repos["unit"]
    analysis_repo = repos["analysis_repo"]
    traj_repo = repos["traj_repo"]

    pos = analysis_repo.create_analysis(
        CurrentPositionAnalysis(
            institution_id=inst.id,
            organizational_unit_id=unit.id,
            analysis_period="2024-2025",
            overall_confidence=ConfidenceAssessment(score=0.9, level="HIGH", factors={}, explanation="Verified"),
        )
    )

    # Trajectory with admissions declining AND dropout rate declining (meaning increasing dropouts)
    traj = traj_repo.create_trajectory_analysis(
        TrajectoryAnalysis(
            institution_id=inst.id,
            organizational_unit_id=unit.id,
            analysis_period="2024-2025",
            overall_trajectory_status=TrajectoryStatus.DECLINING,
            metric_trends=[
                TrajectoryMetric(
                    metric_key="admissions.yield",
                    metric_name="Admissions Yield",
                    domain=MetricDomain.ADMISSIONS_MARKET,
                    direction=MetricDirection.HIGHER_IS_BETTER,
                    earliest_value=45.0,
                    latest_value=32.0,
                    percentage_change=-28.9,
                    trend_status=TrajectoryStatus.DECLINING,
                    consistency=ConsistencyRating.HIGH,
                    acceleration=AccelerationStatus.CONSTANT_VELOCITY,
                    confidence_score=0.88,
                ),
                TrajectoryMetric(
                    metric_key="academic.dropout.rate",
                    metric_name="Dropout Rate",
                    domain=MetricDomain.ACADEMIC_PERFORMANCE,
                    direction=MetricDirection.LOWER_IS_BETTER,
                    earliest_value=5.0,
                    latest_value=8.5,
                    percentage_change=+70.0,
                    trend_status=TrajectoryStatus.DECLINING,
                    consistency=ConsistencyRating.HIGH,
                    acceleration=AccelerationStatus.ACCELERATING,
                    confidence_score=0.92,
                ),
            ],
            overall_confidence=ConfidenceAssessment(score=0.9, level="HIGH", factors={}, explanation="Verified"),
        )
    )

    result = service.generate_strategic_intelligence_analysis(
        StrategicIntelligenceRequestDTO(
            institution_id=inst.id,
            organizational_unit_id=unit.id,
            analysis_period="2024-2025",
            current_position_analysis_id=pos.id,
            trajectory_analysis_id=traj.id,
        )
    )

    # Multi-metric enrollment pipeline risk
    risks = [r for r in result.risk_signals if "Enrollment" in r.title]
    assert len(risks) == 1
    r = risks[0]
    assert len(r.related_metrics) >= 2
    assert "admissions.yield" in r.related_metrics
    assert "academic.dropout.rate" in r.related_metrics
    # Must explicitly state correlation vs causation
    assert "correlation does not imply direct mechanistic causation" in r.correlation_vs_causation_note


def test_constraint_detection_threshold_driven(repos):
    service = repos["service"]
    inst = repos["inst"]
    unit = repos["unit"]
    analysis_repo = repos["analysis_repo"]
    traj_repo = repos["traj_repo"]

    pos = analysis_repo.create_analysis(
        CurrentPositionAnalysis(
            institution_id=inst.id,
            organizational_unit_id=unit.id,
            analysis_period="2024-2025",
            overall_confidence=ConfidenceAssessment(score=0.9, level="HIGH", factors={}, explanation="Verified"),
        )
    )

    # Lab utilization >= 85% and faculty PhD ratio < 70% and student-faculty ratio >= 18
    traj = traj_repo.create_trajectory_analysis(
        TrajectoryAnalysis(
            institution_id=inst.id,
            organizational_unit_id=unit.id,
            analysis_period="2024-2025",
            overall_trajectory_status=TrajectoryStatus.STABLE,
            metric_trends=[
                TrajectoryMetric(
                    metric_key="infra.lab.utilization",
                    metric_name="Lab Utilization",
                    domain=MetricDomain.INFRASTRUCTURE,
                    direction=MetricDirection.HIGHER_IS_BETTER,
                    earliest_value=80.0,
                    latest_value=89.0,  # >= 85% threshold
                    percentage_change=+11.25,
                    trend_status=TrajectoryStatus.IMPROVING,
                    consistency=ConsistencyRating.HIGH,
                    acceleration=AccelerationStatus.CONSTANT_VELOCITY,
                    confidence_score=0.95,
                ),
                TrajectoryMetric(
                    metric_key="faculty.phd.ratio",
                    metric_name="Faculty PhD Ratio",
                    domain=MetricDomain.FACULTY_CAPABILITY,
                    direction=MetricDirection.HIGHER_IS_BETTER,
                    earliest_value=65.0,
                    latest_value=64.0,  # < 70% threshold
                    percentage_change=-1.5,
                    trend_status=TrajectoryStatus.STABLE,
                    consistency=ConsistencyRating.HIGH,
                    acceleration=AccelerationStatus.CONSTANT_VELOCITY,
                    confidence_score=0.90,
                ),
                TrajectoryMetric(
                    metric_key="faculty.student.ratio",
                    metric_name="Student Faculty Ratio",
                    domain=MetricDomain.FACULTY_CAPABILITY,
                    direction=MetricDirection.LOWER_IS_BETTER,
                    earliest_value=16.0,
                    latest_value=19.5,  # >= 18:1 threshold
                    percentage_change=+21.8,
                    trend_status=TrajectoryStatus.DECLINING,
                    consistency=ConsistencyRating.HIGH,
                    acceleration=AccelerationStatus.CONSTANT_VELOCITY,
                    confidence_score=0.90,
                ),
            ],
            overall_confidence=ConfidenceAssessment(score=0.9, level="HIGH", factors={}, explanation="Verified"),
        )
    )

    result = service.generate_strategic_intelligence_analysis(
        StrategicIntelligenceRequestDTO(
            institution_id=inst.id,
            organizational_unit_id=unit.id,
            analysis_period="2024-2025",
            current_position_analysis_id=pos.id,
            trajectory_analysis_id=traj.id,
        )
    )

    con_types = [c.constraint_type for c in result.constraint_signals]
    assert "INFRASTRUCTURE_CAPACITY" in con_types
    assert "FACULTY_CAPABILITY" in con_types
    assert "FACULTY_LOAD" in con_types


def test_missing_data_never_infers_constraints(repos):
    service = repos["service"]
    inst = repos["inst"]
    unit = repos["unit"]
    analysis_repo = repos["analysis_repo"]
    traj_repo = repos["traj_repo"]

    # Trajectory with NO infrastructure or faculty metrics
    pos = analysis_repo.create_analysis(
        CurrentPositionAnalysis(
            institution_id=inst.id,
            organizational_unit_id=unit.id,
            analysis_period="2024-2025",
            overall_confidence=ConfidenceAssessment(score=0.9, level="HIGH", factors={}, explanation="Verified"),
        )
    )
    traj = traj_repo.create_trajectory_analysis(
        TrajectoryAnalysis(
            institution_id=inst.id,
            organizational_unit_id=unit.id,
            analysis_period="2024-2025",
            overall_trajectory_status=TrajectoryStatus.STABLE,
            metric_trends=[],  # Zero metrics
            overall_confidence=ConfidenceAssessment(score=0.5, level="LOW", factors={}, explanation="No metrics"),
        )
    )

    result = service.generate_strategic_intelligence_analysis(
        StrategicIntelligenceRequestDTO(
            institution_id=inst.id,
            organizational_unit_id=unit.id,
            analysis_period="2024-2025",
            current_position_analysis_id=pos.id,
            trajectory_analysis_id=traj.id,
        )
    )

    # Constraints must NEVER be inferred from missing data!
    assert len(result.constraint_signals) == 0
    # Missing data must be captured in uncertainty summary
    assert result.uncertainty_summary["data_limitations_count"] > 0
    assert result.uncertainty_summary["overall_uncertainty_level"] in ("MEDIUM", "HIGH")


def test_opportunity_detection_diagnostic_no_recommendations(repos):
    service = repos["service"]
    inst = repos["inst"]
    unit = repos["unit"]
    analysis_repo = repos["analysis_repo"]
    traj_repo = repos["traj_repo"]

    pos = analysis_repo.create_analysis(
        CurrentPositionAnalysis(
            institution_id=inst.id,
            organizational_unit_id=unit.id,
            analysis_period="2024-2025",
            overall_confidence=ConfidenceAssessment(score=0.9, level="HIGH", factors={}, explanation="Verified"),
        )
    )

    traj = traj_repo.create_trajectory_analysis(
        TrajectoryAnalysis(
            institution_id=inst.id,
            organizational_unit_id=unit.id,
            analysis_period="2024-2025",
            overall_trajectory_status=TrajectoryStatus.IMPROVING,
            metric_trends=[
                TrajectoryMetric(
                    metric_key="research.publications",
                    metric_name="Publications",
                    domain=MetricDomain.RESEARCH_PRODUCTIVITY,
                    direction=MetricDirection.HIGHER_IS_BETTER,
                    earliest_value=100.0,
                    latest_value=160.0,
                    percentage_change=+60.0,
                    trend_status=TrajectoryStatus.IMPROVING,
                    consistency=ConsistencyRating.HIGH,
                    acceleration=AccelerationStatus.ACCELERATING,
                    confidence_score=0.95,
                )
            ],
            overall_confidence=ConfidenceAssessment(score=0.9, level="HIGH", factors={}, explanation="Verified"),
        )
    )

    result = service.generate_strategic_intelligence_analysis(
        StrategicIntelligenceRequestDTO(
            institution_id=inst.id,
            organizational_unit_id=unit.id,
            analysis_period="2024-2025",
            current_position_analysis_id=pos.id,
            trajectory_analysis_id=traj.id,
        )
    )

    assert len(result.opportunity_signals) >= 1
    opp = result.opportunity_signals[0]
    assert opp.opportunity_type == "RESEARCH_MOMENTUM"
    # Verify NO action words or prescriptive recommendations in interpretation/rationale
    for word in ("should create", "must launch", "recommend building", "we advise", "strategy recommendation"):
        assert word not in opp.interpretation.lower()


def test_external_factor_freshness_confidence_penalty(repos):
    service = repos["service"]
    inst = repos["inst"]
    unit = repos["unit"]
    analysis_repo = repos["analysis_repo"]
    traj_repo = repos["traj_repo"]
    ev_repo = repos["ev_repo"]

    pos = analysis_repo.create_analysis(
        CurrentPositionAnalysis(
            institution_id=inst.id,
            organizational_unit_id=unit.id,
            analysis_period="2024-2025",
            overall_confidence=ConfidenceAssessment(score=0.9, level="HIGH", factors={}, explanation="Verified"),
        )
    )
    traj = traj_repo.create_trajectory_analysis(
        TrajectoryAnalysis(
            institution_id=inst.id,
            organizational_unit_id=unit.id,
            analysis_period="2024-2025",
            overall_trajectory_status=TrajectoryStatus.STABLE,
            metric_trends=[],
            overall_confidence=ConfidenceAssessment(score=0.9, level="HIGH", factors={}, explanation="Verified"),
        )
    )

    now = datetime.now(timezone.utc)
    ev_repo.create_evidence(
        InstitutionalEvidence(
            institution_id=inst.id,
            unit_id=unit.id,
            metric_key="external.accreditation.mandate",
            period="2023-2024",
            text_value="Updated laboratory ventilation mandate.",
            domain=MetricDomain.EXTERNAL_REGULATORY,
            source_name="Accreditation Board",
            source_type=SourceType.EXTERNAL,
            quality_tier=QualityTier.ESTIMATED,
            confidence_score=0.80,
            as_of_date=now - timedelta(days=400),
            is_stale=True,
        )
    )

    result = service.generate_strategic_intelligence_analysis(
        StrategicIntelligenceRequestDTO(
            institution_id=inst.id,
            organizational_unit_id=unit.id,
            analysis_period="2024-2025",
            current_position_analysis_id=pos.id,
            trajectory_analysis_id=traj.id,
        )
    )

    ext = next((e for e in result.external_factors if "accreditation" in e.factor_name.lower()), None)
    assert ext is not None
    assert ext.freshness == FreshnessStatus.STALE
    # Confidence penalty applied: 0.80 * 0.85 = 0.68
    assert ext.confidence < 0.80
    assert ext.confidence == 0.68


def test_deterministic_risk_scoring_and_preliminary_priorities(repos):
    service = repos["service"]
    # Test deterministic calculation directly
    score, sev, ftrs = service._calculate_risk_score(
        impact=ImpactLevel.CRITICAL,
        likelihood=LikelihoodLevel.HIGH,
        trajectory_trend=TrajectoryStatus.DECLINING,
        evidence_conf=0.95,
        is_structural=True,
    )
    assert score >= settings.HIGH_RISK_SCORE_THRESHOLD
    assert sev in (RiskSeverity.HIGH, RiskSeverity.CRITICAL)
    assert "trajectory_multiplier" in ftrs
    assert ftrs["trajectory_multiplier"] == 1.20

    # Test preliminary priority scoring
    p_score, p_lvl, p_ftrs = service._calculate_priority_score(
        impact=ImpactLevel.HIGH,
        urgency=LikelihoodLevel.HIGH,
        evidence_conf=0.90,
    )
    assert p_score > 0.70
    assert p_lvl in ("URGENT", "HIGH")


def test_organizational_unit_scope_isolation(repos):
    service = repos["service"]
    inst = repos["inst"]
    unit = repos["unit"]
    org_repo = repos["org_repo"]
    analysis_repo = repos["analysis_repo"]
    traj_repo = repos["traj_repo"]

    other_unit = org_repo.create_unit(
        OrganizationalUnit(id="unit-other", institution_id=inst.id, code="OTHER", name="Other School", unit_type=UnitType.SCHOOL, status=EntityStatus.ACTIVE)
    )

    # Create analyses for unit-test-1 only
    analysis_repo.create_analysis(
        CurrentPositionAnalysis(
            institution_id=inst.id,
            organizational_unit_id=unit.id,
            analysis_period="2024-2025",
            overall_confidence=ConfidenceAssessment(score=0.9, level="HIGH", factors={}, explanation="Verified"),
        )
    )
    traj_repo.create_trajectory_analysis(
        TrajectoryAnalysis(
            institution_id=inst.id,
            organizational_unit_id=unit.id,
            analysis_period="2024-2025",
            overall_trajectory_status=TrajectoryStatus.STABLE,
            metric_trends=[],
            overall_confidence=ConfidenceAssessment(score=0.9, level="HIGH", factors={}, explanation="Verified"),
        )
    )

    # Calling for other_unit must fail to find prerequisite analyses
    with pytest.raises(ValidationError, match=r"Prerequisite Current Position Analysis \(Phase 4\) not found"):
        service.generate_strategic_intelligence_analysis(
            StrategicIntelligenceRequestDTO(
                institution_id=inst.id,
                organizational_unit_id=other_unit.id,
                analysis_period="2024-2025",
            )
        )


def test_ai_synthesis_guardrails_never_alters_findings(repos):
    service = repos["service"]
    inst = repos["inst"]
    unit = repos["unit"]
    analysis_repo = repos["analysis_repo"]
    traj_repo = repos["traj_repo"]

    pos = analysis_repo.create_analysis(
        CurrentPositionAnalysis(
            institution_id=inst.id,
            organizational_unit_id=unit.id,
            analysis_period="2024-2025",
            overall_confidence=ConfidenceAssessment(score=0.9, level="HIGH", factors={}, explanation="Verified"),
        )
    )
    traj = traj_repo.create_trajectory_analysis(
        TrajectoryAnalysis(
            institution_id=inst.id,
            organizational_unit_id=unit.id,
            analysis_period="2024-2025",
            overall_trajectory_status=TrajectoryStatus.STABLE,
            metric_trends=[
                TrajectoryMetric(
                    metric_key="infra.lab.utilization",
                    metric_name="Lab Utilization",
                    domain=MetricDomain.INFRASTRUCTURE,
                    direction=MetricDirection.HIGHER_IS_BETTER,
                    earliest_value=80.0,
                    latest_value=90.0,
                    percentage_change=+12.5,
                    trend_status=TrajectoryStatus.IMPROVING,
                    consistency=ConsistencyRating.HIGH,
                    acceleration=AccelerationStatus.CONSTANT_VELOCITY,
                    confidence_score=0.95,
                )
            ],
            overall_confidence=ConfidenceAssessment(score=0.9, level="HIGH", factors={}, explanation="Verified"),
        )
    )

    # Run with AI synthesis enabled
    res = service.generate_strategic_intelligence_analysis(
        StrategicIntelligenceRequestDTO(
            institution_id=inst.id,
            organizational_unit_id=unit.id,
            analysis_period="2024-2025",
            current_position_analysis_id=pos.id,
            trajectory_analysis_id=traj.id,
            include_ai_synthesis=True,
        )
    )

    # Deterministic signals remain unmodified
    assert res.ai_synthesis_notes is not None
    assert len(res.constraint_signals) == 1
    assert res.constraint_signals[0].constraint_type == "INFRASTRUCTURE_CAPACITY"
    # Repo snapshot is immutable
    assert res.status == "FINALIZED"


