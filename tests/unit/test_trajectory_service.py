"""Unit tests for Institutional Trajectory Analysis Service (Phase 5)."""

from datetime import date, datetime, timezone
import pytest

from agent72.application.dtos.analysis_dto import CurrentPositionAnalysisRequestDTO
from agent72.application.dtos.trajectory_dto import TrajectoryAnalysisRequestDTO
from agent72.application.services.analysis_service import CurrentPositionAnalysisService
from agent72.application.services.trajectory_service import TrajectoryAnalysisService
from agent72.domain.interfaces.analysis_repository import IAnalysisRepository
from agent72.domain.interfaces.evidence_repository import IEvidenceRepository
from agent72.domain.interfaces.organization_repository import IOrganizationRepository
from agent72.domain.interfaces.trajectory_repository import ITrajectoryRepository
from agent72.domain.models.analysis import (
    ConfidenceAssessment,
    CurrentPositionAnalysis,
    FindingCategory,
    MetricAssessment,
    PerformanceStatus,
    PositionFinding,
)
from agent72.domain.models.evidence import (
    InstitutionalEvidence,
    MetricDefinition,
    MetricDirection,
    MetricDomain,
    QualityTier,
    SourceType,
)
from agent72.domain.models.organization import EntityStatus, Institution, OrganizationalUnit, UnitType
from agent72.domain.models.trajectory import (
    AccelerationStatus,
    ConsistencyRating,
    TrajectoryAnalysis,
    TrajectoryStatus,
)


class InMemoryTrajectoryRepo(ITrajectoryRepository):
    def __init__(self):
        self.analyses: dict[str, TrajectoryAnalysis] = {}

    def create_trajectory_analysis(self, analysis: TrajectoryAnalysis) -> TrajectoryAnalysis:
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
        self.evidence_list.append(evidence)
        return evidence

    def record_evidence_batch(self, batch):
        self.evidence_list.extend(batch)
        return batch

    def query_evidence(self, **kwargs):
        items = list(self.evidence_list)
        if kwargs.get("institution_id"):
            items = [e for e in items if e.institution_id == kwargs["institution_id"]]
        if kwargs.get("unit_id") is not None:
            items = [e for e in items if e.unit_id == kwargs["unit_id"]]
        if kwargs.get("metric_key"):
            items = [e for e in items if e.metric_key == kwargs["metric_key"]]
        return items

    def get_latest_evidence(self, institution_id, metric_key, unit_id=None):
        filtered = [e for e in self.evidence_list if e.institution_id == institution_id and e.metric_key == metric_key]
        return filtered[-1] if filtered else None

    def get_historical_series(self, institution_id, metric_key, unit_id=None, skip=0, limit=500):
        items = [
            e for e in self.evidence_list
            if e.institution_id == institution_id and e.metric_key == metric_key
        ]
        if unit_id is not None:
            items = [e for e in items if e.unit_id == unit_id]
        return items[skip : skip + limit]

    def get_evidence_by_domain(self, institution_id, domain, period=None, skip=0, limit=50):
        return [e for e in self.evidence_list if e.institution_id == institution_id and e.domain == domain]

    def record_batch_log(self, batch_log):
        return batch_log

    def get_batch_log(self, batch_id):
        return None

    def find_by_batch_id(self, batch_id):
        return []


class InMemoryOrgRepo(IOrganizationRepository):
    def __init__(self):
        self.institutions: dict[str, Institution] = {}
        self.units: dict[str, OrganizationalUnit] = {}

    def create_institution(self, institution):
        self.institutions[institution.id] = institution
        return institution

    def get_institution_by_id(self, institution_id: str):
        return self.institutions.get(institution_id)

    def get_institution_by_code(self, code):
        for inst in self.institutions.values():
            if inst.code == code:
                return inst
        return None

    def list_institutions(self, skip=0, limit=50):
        return list(self.institutions.values())[skip : skip + limit]

    def count_institutions(self):
        return len(self.institutions)

    def create_unit(self, unit):
        self.units[unit.id] = unit
        return unit

    def get_unit_by_id(self, unit_id: str):
        return self.units.get(unit_id)

    def get_unit_by_code(self, institution_id, code):
        for u in self.units.values():
            if u.institution_id == institution_id and u.code == code:
                return u
        return None

    def list_units_by_institution(self, institution_id, skip=0, limit=50):
        return [u for u in self.units.values() if u.institution_id == institution_id][skip : skip + limit]

    def count_units_by_institution(self, institution_id):
        return len([u for u in self.units.values() if u.institution_id == institution_id])


class InMemoryAnalysisRepo(IAnalysisRepository):
    def __init__(self):
        self.analyses: dict[str, CurrentPositionAnalysis] = {}

    def create_analysis(self, analysis: CurrentPositionAnalysis) -> CurrentPositionAnalysis:
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
        if analysis_period:
            items = [a for a in items if a.analysis_period == analysis_period]
        return items[skip : skip + limit]

    def count_analyses(self, institution_id=None, organizational_unit_id=None, analysis_period=None):
        return len(self.list_analyses(institution_id, organizational_unit_id, analysis_period))


@pytest.fixture
def setup_trajectory():
    traj_repo = InMemoryTrajectoryRepo()
    ev_repo = InMemoryEvidenceRepo()
    org_repo = InMemoryOrgRepo()
    analysis_repo = InMemoryAnalysisRepo()

    org_repo.institutions["inst-1"] = Institution(
        id="inst-1",
        name="Apex University",
        code="APEX",
        status=EntityStatus.ACTIVE,
    )

    service = TrajectoryAnalysisService(
        trajectory_repository=traj_repo,
        evidence_repository=ev_repo,
        organization_repository=org_repo,
        analysis_repository=analysis_repo,
    )
    return service, ev_repo, org_repo, analysis_repo, traj_repo


def test_insufficient_historical_data_isolation(setup_trajectory):
    """0 and 1 observation must be isolated as data limitations and never classified as trends."""
    service, ev_repo, _, _, _ = setup_trajectory

    # Metric with 0 observations
    ev_repo.create_metric_definition(
        MetricDefinition(
            metric_key="faculty.phd_ratio",
            name="PhD Ratio",
            domain=MetricDomain.FACULTY_CAPABILITY,
            direction=MetricDirection.HIGHER_IS_BETTER,
            default_unit="percent",
        )
    )
    # Metric with 1 observation
    ev_repo.create_metric_definition(
        MetricDefinition(
            metric_key="infra.library_capacity",
            name="Library Capacity",
            domain=MetricDomain.INFRASTRUCTURE,
            direction=MetricDirection.HIGHER_IS_BETTER,
            default_unit="seats",
        )
    )
    ev_repo.record_evidence(
        InstitutionalEvidence(
            id="ev-lib-1",
            institution_id="inst-1",
            metric_key="infra.library_capacity",
            numeric_value=1200.0,
            unit="seats",
            period="2024-2025",
            source_name="Facilities",
            source_type=SourceType.MANUAL,
        )
    )

    res = service.generate_trajectory_analysis(
        TrajectoryAnalysisRequestDTO(institution_id="inst-1", analysis_period="2024-2025")
    )

    phd = next(m for m in res.metric_trends if m.metric_key == "faculty.phd_ratio")
    assert phd.trend_status == TrajectoryStatus.INSUFFICIENT_DATA
    assert phd.observations == []

    lib = next(m for m in res.metric_trends if m.metric_key == "infra.library_capacity")
    assert lib.trend_status == TrajectoryStatus.INSUFFICIENT_DATA
    assert len(lib.observations) == 1

    # Check that both are explicitly tracked in data_limitations
    assert len(res.data_limitations) == 2
    lim_keys = {l.metric_key for l in res.data_limitations}
    assert "faculty.phd_ratio" in lim_keys
    assert "infra.library_capacity" in lim_keys


def test_two_period_basic_directional_trend(setup_trajectory):
    """2 observations yield basic directional change, with consistency and acceleration as INSUFFICIENT_DATA."""
    service, ev_repo, _, _, _ = setup_trajectory

    ev_repo.create_metric_definition(
        MetricDefinition(
            metric_key="placement.rate",
            name="Placement Rate",
            domain=MetricDomain.PLACEMENT_EMPLOYER_DEMAND,
            direction=MetricDirection.HIGHER_IS_BETTER,
            default_unit="percent",
        )
    )
    ev_repo.record_evidence(
        InstitutionalEvidence(
            id="ev-p-1",
            institution_id="inst-1",
            metric_key="placement.rate",
            numeric_value=76.0,
            unit="percent",
            period="2023-2024",
            source_name="Agent 71",
            source_type=SourceType.AGENT,
            confidence_score=0.95,
        )
    )
    ev_repo.record_evidence(
        InstitutionalEvidence(
            id="ev-p-2",
            institution_id="inst-1",
            metric_key="placement.rate",
            numeric_value=81.0,
            unit="percent",
            period="2024-2025",
            source_name="Agent 71",
            source_type=SourceType.AGENT,
            confidence_score=0.95,
        )
    )

    res = service.generate_trajectory_analysis(
        TrajectoryAnalysisRequestDTO(institution_id="inst-1", analysis_period="2024-2025")
    )

    placement = next(m for m in res.metric_trends if m.metric_key == "placement.rate")
    assert placement.trend_status == TrajectoryStatus.IMPROVING
    assert placement.absolute_change == 5.0
    assert placement.percentage_change == 6.58
    assert placement.consistency == ConsistencyRating.INSUFFICIENT_DATA
    assert placement.acceleration == AccelerationStatus.INSUFFICIENT_DATA
    assert placement.volatility is None


def test_three_period_consistency_high(setup_trajectory):
    """3 observations moving monotonically upward yield HIGH consistency."""
    service, ev_repo, _, _, _ = setup_trajectory

    ev_repo.create_metric_definition(
        MetricDefinition(
            metric_key="research.citations",
            name="Citations",
            domain=MetricDomain.RESEARCH_PRODUCTIVITY,
            direction=MetricDirection.HIGHER_IS_BETTER,
            default_unit="count",
        )
    )
    for p, val, eid in [("2022-2023", 2200.0, "ev-c-1"), ("2023-2024", 2800.0, "ev-c-2"), ("2024-2025", 3400.0, "ev-c-3")]:
        ev_repo.record_evidence(
            InstitutionalEvidence(
                id=eid,
                institution_id="inst-1",
                metric_key="research.citations",
                numeric_value=val,
                unit="count",
                period=p,
                source_name="Agent 20",
                source_type=SourceType.AGENT,
                confidence_score=0.96,
                quality_tier=QualityTier.VERIFIED,
            )
        )

    res = service.generate_trajectory_analysis(
        TrajectoryAnalysisRequestDTO(institution_id="inst-1", analysis_period="2024-2025")
    )

    citations = next(m for m in res.metric_trends if m.metric_key == "research.citations")
    assert citations.trend_status == TrajectoryStatus.IMPROVING
    assert citations.consistency == ConsistencyRating.HIGH
    assert citations.volatility is not None
    assert citations.acceleration == AccelerationStatus.CONSTANT_VELOCITY  # +600 then +600


def test_improving_lower_is_better_metric(setup_trajectory):
    """Lower-is-better metric (e.g. dropout rate) decreasing over periods is IMPROVING."""
    service, ev_repo, _, _, _ = setup_trajectory

    ev_repo.create_metric_definition(
        MetricDefinition(
            metric_key="academic.dropout_rate",
            name="Dropout Rate",
            domain=MetricDomain.ACADEMIC_PERFORMANCE,
            direction=MetricDirection.LOWER_IS_BETTER,
            default_unit="percent",
        )
    )
    for p, val, eid in [("2022-2023", 10.2, "ev-d-1"), ("2023-2024", 8.5, "ev-d-2"), ("2024-2025", 7.2, "ev-d-3")]:
        ev_repo.record_evidence(
            InstitutionalEvidence(
                id=eid,
                institution_id="inst-1",
                metric_key="academic.dropout_rate",
                numeric_value=val,
                unit="percent",
                period=p,
                source_name="Agent 71",
                source_type=SourceType.AGENT,
                confidence_score=0.90,
            )
        )

    res = service.generate_trajectory_analysis(
        TrajectoryAnalysisRequestDTO(institution_id="inst-1", analysis_period="2024-2025")
    )

    dropout = next(m for m in res.metric_trends if m.metric_key == "academic.dropout_rate")
    assert dropout.trend_status == TrajectoryStatus.IMPROVING
    assert dropout.absolute_change == -3.0
    assert dropout.percentage_change == -29.41
    assert dropout.consistency == ConsistencyRating.HIGH


def test_declining_metric(setup_trajectory):
    """Higher-is-better metric that decreases over time is classified as DECLINING."""
    service, ev_repo, _, _, _ = setup_trajectory

    ev_repo.create_metric_definition(
        MetricDefinition(
            metric_key="admissions.yield_rate",
            name="Admissions Yield",
            domain=MetricDomain.ADMISSIONS_MARKET,
            direction=MetricDirection.HIGHER_IS_BETTER,
            default_unit="percent",
        )
    )
    for p, val, eid in [("2022-2023", 42.0, "ev-y-1"), ("2023-2024", 38.0, "ev-y-2"), ("2024-2025", 34.0, "ev-y-3")]:
        ev_repo.record_evidence(
            InstitutionalEvidence(
                id=eid,
                institution_id="inst-1",
                metric_key="admissions.yield_rate",
                numeric_value=val,
                unit="percent",
                period=p,
                source_name="Agent 71",
                source_type=SourceType.AGENT,
            )
        )

    res = service.generate_trajectory_analysis(
        TrajectoryAnalysisRequestDTO(institution_id="inst-1", analysis_period="2024-2025")
    )

    adm = next(m for m in res.metric_trends if m.metric_key == "admissions.yield_rate")
    assert adm.trend_status == TrajectoryStatus.DECLINING
    assert adm.absolute_change == -8.0


def test_stable_metric_within_threshold(setup_trajectory):
    """Changes below significance threshold (default 2%) are classified as STABLE."""
    service, ev_repo, _, _, _ = setup_trajectory

    ev_repo.create_metric_definition(
        MetricDefinition(
            metric_key="faculty.ratio",
            name="Student Faculty Ratio",
            domain=MetricDomain.FACULTY_CAPABILITY,
            direction=MetricDirection.LOWER_IS_BETTER,
            default_unit="ratio",
        )
    )
    # 15.0 -> 15.1 -> 15.05 (change is < 1%)
    for p, val, eid in [("2022-2023", 15.0, "ev-f-1"), ("2023-2024", 15.1, "ev-f-2"), ("2024-2025", 15.05, "ev-f-3")]:
        ev_repo.record_evidence(
            InstitutionalEvidence(
                id=eid,
                institution_id="inst-1",
                metric_key="faculty.ratio",
                numeric_value=val,
                unit="ratio",
                period=p,
                source_name="Agent 71",
                source_type=SourceType.AGENT,
            )
        )

    res = service.generate_trajectory_analysis(
        TrajectoryAnalysisRequestDTO(institution_id="inst-1", analysis_period="2024-2025")
    )

    ratio = next(m for m in res.metric_trends if m.metric_key == "faculty.ratio")
    assert ratio.trend_status == TrajectoryStatus.STABLE


def test_volatile_metric_detection(setup_trajectory):
    """Large alternating swings with low consistency produce VOLATILE status."""
    service, ev_repo, _, _, _ = setup_trajectory

    ev_repo.create_metric_definition(
        MetricDefinition(
            metric_key="finance.grant_funding",
            name="External Grants",
            domain=MetricDomain.FINANCE_RESOURCES,
            direction=MetricDirection.HIGHER_IS_BETTER,
            default_unit="usd_thousands",
        )
    )
    # Wild swings: 100 -> 300 (+200) -> 90 (-210) -> 350 (+260)
    for p, val, eid in [
        ("2021-2022", 100.0, "ev-g-1"),
        ("2022-2023", 300.0, "ev-g-2"),
        ("2023-2024", 90.0, "ev-g-3"),
        ("2024-2025", 350.0, "ev-g-4"),
    ]:
        ev_repo.record_evidence(
            InstitutionalEvidence(
                id=eid,
                institution_id="inst-1",
                metric_key="finance.grant_funding",
                numeric_value=val,
                unit="usd_thousands",
                period=p,
                source_name="Finance Dept",
                source_type=SourceType.MANUAL,
            )
        )

    res = service.generate_trajectory_analysis(
        TrajectoryAnalysisRequestDTO(institution_id="inst-1", analysis_period="2024-2025")
    )

    grant = next(m for m in res.metric_trends if m.metric_key == "finance.grant_funding")
    assert grant.consistency == ConsistencyRating.LOW
    assert grant.volatility == "HIGH"
    assert grant.volatility_score is not None and grant.volatility_score > 15.0
    assert grant.trend_status == TrajectoryStatus.VOLATILE


def test_acceleration_and_deceleration(setup_trajectory):
    """70 -> 74 (+4) -> 80 (+6) indicates ACCELERATING positive momentum."""
    service, ev_repo, _, _, _ = setup_trajectory

    ev_repo.create_metric_definition(
        MetricDefinition(
            metric_key="placement.rate",
            name="Placement Rate",
            domain=MetricDomain.PLACEMENT_EMPLOYER_DEMAND,
            direction=MetricDirection.HIGHER_IS_BETTER,
            default_unit="percent",
        )
    )
    for p, val, eid in [("2022-2023", 70.0, "ev-acc-1"), ("2023-2024", 74.0, "ev-acc-2"), ("2024-2025", 80.0, "ev-acc-3")]:
        ev_repo.record_evidence(
            InstitutionalEvidence(
                id=eid,
                institution_id="inst-1",
                metric_key="placement.rate",
                numeric_value=val,
                unit="percent",
                period=p,
                source_name="Agent 71",
                source_type=SourceType.AGENT,
            )
        )

    res = service.generate_trajectory_analysis(
        TrajectoryAnalysisRequestDTO(institution_id="inst-1", analysis_period="2024-2025")
    )

    placement = next(m for m in res.metric_trends if m.metric_key == "placement.rate")
    assert placement.acceleration == AccelerationStatus.ACCELERATING


def test_trajectory_signal_synthesis_with_current_position(setup_trajectory):
    """Connecting Current Position Analysis to Trajectory creates structured combination signals."""
    service, ev_repo, _, analysis_repo, _ = setup_trajectory

    # 1. Placement rate: Current position below target (81% vs 85%), but trajectory is IMPROVING (76 -> 81)
    # -> Signal: 'Improving but below target'
    ev_repo.create_metric_definition(
        MetricDefinition(
            metric_key="placement.rate",
            name="Placement Rate",
            domain=MetricDomain.PLACEMENT_EMPLOYER_DEMAND,
            direction=MetricDirection.HIGHER_IS_BETTER,
            default_unit="percent",
        )
    )
    for p, val in [("2022-2023", 72.0), ("2023-2024", 76.0), ("2024-2025", 81.0)]:
        ev_repo.record_evidence(
            InstitutionalEvidence(
                id=f"ev-p-{p}",
                institution_id="inst-1",
                metric_key="placement.rate",
                numeric_value=val,
                unit="percent",
                period=p,
                source_name="Agent 71",
                source_type=SourceType.AGENT,
            )
        )

    # 2. Admissions yield: Current position below target and DECLINING
    # -> Signal: 'Declining and below target'
    ev_repo.create_metric_definition(
        MetricDefinition(
            metric_key="admissions.yield",
            name="Admissions Yield",
            domain=MetricDomain.ADMISSIONS_MARKET,
            direction=MetricDirection.HIGHER_IS_BETTER,
            default_unit="percent",
        )
    )
    for p, val in [("2022-2023", 45.0), ("2023-2024", 40.0), ("2024-2025", 35.0)]:
        ev_repo.record_evidence(
            InstitutionalEvidence(
                id=f"ev-y-{p}",
                institution_id="inst-1",
                metric_key="admissions.yield",
                numeric_value=val,
                unit="percent",
                period=p,
                source_name="Agent 71",
                source_type=SourceType.AGENT,
            )
        )

    # Create a Current Position Analysis snapshot in the repo
    current_analysis = CurrentPositionAnalysis(
        id="pos-snap-1",
        institution_id="inst-1",
        analysis_period="2024-2025",
        key_metrics=[
            MetricAssessment(
                metric_key="placement.rate",
                metric_name="Placement Rate",
                domain=MetricDomain.PLACEMENT_EMPLOYER_DEMAND,
                unit="percent",
                direction=MetricDirection.HIGHER_IS_BETTER,
                latest_value=81.0,
                target_value=85.0,
                target_variance=-4.0,
                performance_status=PerformanceStatus.BELOW_TARGET,
            ),
            MetricAssessment(
                metric_key="admissions.yield",
                metric_name="Admissions Yield",
                domain=MetricDomain.ADMISSIONS_MARKET,
                unit="percent",
                direction=MetricDirection.HIGHER_IS_BETTER,
                latest_value=35.0,
                target_value=42.0,
                target_variance=-7.0,
                performance_status=PerformanceStatus.BELOW_TARGET,
            ),
        ],
        gaps=[
            PositionFinding(
                category=FindingCategory.GAP,
                title="Placement Rate below target",
                description="4 pp below target",
                metric_key="placement.rate",
                observed_value=81.0,
                comparison_value=85.0,
                rationale="Gap",
            ),
            PositionFinding(
                category=FindingCategory.GAP,
                title="Admissions Yield below target",
                description="7 pp below target",
                metric_key="admissions.yield",
                observed_value=35.0,
                comparison_value=42.0,
                rationale="Gap",
            ),
        ],
        overall_confidence=ConfidenceAssessment(score=0.9, level="HIGH", factors={}, explanation="High"),
    )
    analysis_repo.create_analysis(current_analysis)

    res = service.generate_trajectory_analysis(
        TrajectoryAnalysisRequestDTO(
            institution_id="inst-1",
            analysis_period="2024-2025",
            current_position_analysis_id="pos-snap-1",
        )
    )

    signals = {s.signal_type: s for s in res.trajectory_signals}
    assert "GAP_IMPROVING" in signals
    assert "Improving but below target" in signals["GAP_IMPROVING"].title
    assert signals["GAP_IMPROVING"].status == "BELOW_TARGET_IMPROVING"
    assert "Performance is improving but remains below the current target." in signals["GAP_IMPROVING"].interpretation

    assert "GAP_DECLINING" in signals
    assert "Declining and below target" in signals["GAP_DECLINING"].title
    assert signals["GAP_DECLINING"].status == "BELOW_TARGET_DECLINING"
    assert "Performance is declining and remains below the current target." in signals["GAP_DECLINING"].interpretation


def test_deceleration_momentum_slowing(setup_trajectory):
    """70 -> 78 (+8) -> 81 (+3) indicates DECELERATING momentum."""
    service, ev_repo, _, _, _ = setup_trajectory

    ev_repo.create_metric_definition(
        MetricDefinition(
            metric_key="retention.rate",
            name="Retention Rate",
            domain=MetricDomain.ACADEMIC_PERFORMANCE,
            direction=MetricDirection.HIGHER_IS_BETTER,
            default_unit="percent",
        )
    )
    for p, val, eid in [("2022-2023", 70.0, "ev-dec-1"), ("2023-2024", 78.0, "ev-dec-2"), ("2024-2025", 81.0, "ev-dec-3")]:
        ev_repo.record_evidence(
            InstitutionalEvidence(
                id=eid,
                institution_id="inst-1",
                metric_key="retention.rate",
                numeric_value=val,
                unit="percent",
                period=p,
                source_name="Registrar",
                source_type=SourceType.MANUAL,
            )
        )

    res = service.generate_trajectory_analysis(
        TrajectoryAnalysisRequestDTO(institution_id="inst-1", analysis_period="2024-2025")
    )

    retention = next(m for m in res.metric_trends if m.metric_key == "retention.rate")
    assert retention.acceleration == AccelerationStatus.DECELERATING


def test_stale_and_provisional_evidence_handling(setup_trajectory):
    """Stale evidence is tagged and applies a transparency freshness penalty to confidence."""
    service, ev_repo, _, _, _ = setup_trajectory

    ev_repo.create_metric_definition(
        MetricDefinition(
            metric_key="faculty.phd_ratio",
            name="Faculty PhD Ratio",
            domain=MetricDomain.FACULTY_CAPABILITY,
            direction=MetricDirection.HIGHER_IS_BETTER,
            default_unit="percent",
        )
    )
    for p, val, stale, tier in [
        ("2022-2023", 65.0, True, QualityTier.PROVISIONAL),
        ("2023-2024", 68.0, True, QualityTier.PROVISIONAL),
        ("2024-2025", 70.0, False, QualityTier.ESTIMATED),
    ]:
        ev_repo.record_evidence(
            InstitutionalEvidence(
                id=f"ev-stale-{p}",
                institution_id="inst-1",
                metric_key="faculty.phd_ratio",
                numeric_value=val,
                unit="percent",
                period=p,
                source_name="HR",
                source_type=SourceType.MANUAL,
                quality_tier=tier,
                is_stale=stale,
                confidence_score=0.70,
            )
        )

    res = service.generate_trajectory_analysis(
        TrajectoryAnalysisRequestDTO(institution_id="inst-1", analysis_period="2024-2025")
    )

    metric = next(m for m in res.metric_trends if m.metric_key == "faculty.phd_ratio")
    stale_obs = [o for o in metric.observations if o.is_stale]
    assert len(stale_obs) == 2

    # Freshness penalty in confidence factors
    assert res.overall_confidence.factors["stale_observations_count"] == 2
    assert res.overall_confidence.factors["freshness_penalty"] > 0


def test_organizational_unit_scope_filtering(setup_trajectory):
    """Trajectory analysis scoped to an organizational unit filters observations to that unit."""
    service, ev_repo, org_repo, _, _ = setup_trajectory

    # Create department unit
    dept = org_repo.create_unit(
        OrganizationalUnit(
            id="unit-cs",
            institution_id="inst-1",
            name="Computer Science",
            unit_type=UnitType.DEPARTMENT,
        )
    )

    ev_repo.create_metric_definition(
        MetricDefinition(
            metric_key="research.publications",
            name="Research Publications",
            domain=MetricDomain.RESEARCH_PRODUCTIVITY,
            direction=MetricDirection.HIGHER_IS_BETTER,
            default_unit="count",
        )
    )

    # Record unit-specific evidence
    for p, val in [("2022-2023", 20.0), ("2023-2024", 25.0), ("2024-2025", 32.0)]:
        ev_repo.record_evidence(
            InstitutionalEvidence(
                id=f"ev-cs-{p}",
                institution_id="inst-1",
                unit_id="unit-cs",
                metric_key="research.publications",
                numeric_value=val,
                unit="count",
                period=p,
                source_name="CS Dept",
                source_type=SourceType.MANUAL,
            )
        )

    # Record institutional (non-unit) evidence with different values
    for p, val in [("2022-2023", 100.0), ("2023-2024", 120.0), ("2024-2025", 150.0)]:
        ev_repo.record_evidence(
            InstitutionalEvidence(
                id=f"ev-inst-{p}",
                institution_id="inst-1",
                unit_id=None,
                metric_key="research.publications",
                numeric_value=val,
                unit="count",
                period=p,
                source_name="Research Office",
                source_type=SourceType.MANUAL,
            )
        )

    # Scoped to unit-cs
    res = service.generate_trajectory_analysis(
        TrajectoryAnalysisRequestDTO(
            institution_id="inst-1",
            organizational_unit_id="unit-cs",
            analysis_period="2024-2025",
        )
    )

    pub_trend = next(m for m in res.metric_trends if m.metric_key == "research.publications")
    assert pub_trend.latest_value == 32.0
    assert pub_trend.earliest_value == 20.0
    assert res.organizational_unit_id == "unit-cs"


def test_confidence_calculation_and_traceability(setup_trajectory):
    """Transparent confidence calculation with contributing factors and traceable evidence references."""
    service, ev_repo, _, _, traj_repo = setup_trajectory

    ev_repo.create_metric_definition(
        MetricDefinition(
            metric_key="placement.rate",
            name="Placement Rate",
            domain=MetricDomain.PLACEMENT_EMPLOYER_DEMAND,
            direction=MetricDirection.HIGHER_IS_BETTER,
            default_unit="percent",
        )
    )
    for p, val in [("2022-2023", 72.0), ("2023-2024", 76.0), ("2024-2025", 81.0)]:
        ev_repo.record_evidence(
            InstitutionalEvidence(
                id=f"trace-{p}",
                institution_id="inst-1",
                metric_key="placement.rate",
                numeric_value=val,
                unit="percent",
                period=p,
                source_name="Agent 71",
                source_type=SourceType.AGENT,
                confidence_score=0.95,
                quality_tier=QualityTier.VERIFIED,
            )
        )

    res = service.generate_trajectory_analysis(
        TrajectoryAnalysisRequestDTO(institution_id="inst-1", analysis_period="2024-2025")
    )

    # Check overall confidence
    assert res.overall_confidence.score >= 0.80
    assert res.overall_confidence.level == "HIGH"
    assert "depth_score" in res.overall_confidence.factors
    assert "average_evidence_confidence" in res.overall_confidence.factors

    # Check evidence traceability
    assert len(res.evidence_references) == 3
    ref_ids = {r.evidence_id for r in res.evidence_references}
    assert "trace-2022-2023" in ref_ids
    assert "trace-2023-2024" in ref_ids
    assert "trace-2024-2025" in ref_ids

    # Check immutable persistence
    saved = traj_repo.get_trajectory_analysis_by_id(res.id)
    assert saved is not None
    assert saved.institution_id == "inst-1"
    assert saved.analysis_period == "2024-2025"
