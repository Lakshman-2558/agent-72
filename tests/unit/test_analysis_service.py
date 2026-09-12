"""Unit tests for Phase 4 Current Institutional Position Analysis Service."""

from datetime import date, datetime, timezone
import pytest

from agent72.application.dtos.analysis_dto import CurrentPositionAnalysisRequestDTO
from agent72.application.services.analysis_service import CurrentPositionAnalysisService
from agent72.domain.interfaces.analysis_repository import IAnalysisRepository
from agent72.domain.interfaces.evidence_repository import IEvidenceRepository
from agent72.domain.interfaces.organization_repository import IOrganizationRepository
from agent72.domain.models.analysis import (
    CurrentPositionAnalysis,
    FindingCategory,
    PerformanceStatus,
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
from agent72.domain.models.organization import EntityStatus, Institution, UnitType


class InMemoryAnalysisRepo(IAnalysisRepository):
    def __init__(self):
        self.analyses: dict[str, CurrentPositionAnalysis] = {}

    def create_analysis(self, analysis: CurrentPositionAnalysis) -> CurrentPositionAnalysis:
        analysis.id = f"analysis-{len(self.analyses) + 1}"
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


class InMemoryEvidenceRepo(IEvidenceRepository):
    def __init__(self):
        self.metrics: dict[str, MetricDefinition] = {}
        self.evidence: list[InstitutionalEvidence] = []

    def create_metric_definition(self, definition):
        self.metrics[definition.metric_key] = definition
        return definition

    def get_metric_definition(self, metric_key):
        return self.metrics.get(metric_key)

    def list_metric_definitions(self, domain=None):
        items = list(self.metrics.values())
        if domain:
            items = [m for m in items if m.domain == domain]
        return items

    def find_existing_evidence(self, institution_id, idempotency_key):
        return None

    def record_evidence(self, evidence):
        self.evidence.append(evidence)
        return evidence

    def record_evidence_batch(self, evidence_items):
        self.evidence.extend(evidence_items)
        return evidence_items

    def query_evidence(self, **kwargs):
        return self.evidence

    def get_latest_evidence(self, institution_id, metric_key, unit_id=None):
        filtered = [e for e in self.evidence if e.institution_id == institution_id and e.metric_key == metric_key]
        return filtered[-1] if filtered else None

    def get_historical_series(self, institution_id, metric_key, unit_id=None, skip=0, limit=50):
        return [
            e for e in self.evidence
            if e.institution_id == institution_id
            and e.metric_key == metric_key
            and (unit_id is None or e.unit_id == unit_id)
        ]

    def get_evidence_by_domain(self, institution_id, domain, period=None, skip=0, limit=50):
        return [e for e in self.evidence if e.institution_id == institution_id and e.domain == domain]

    def record_batch_log(self, batch_log):
        return batch_log

    def get_batch_log(self, batch_id):
        return None

    def find_by_batch_id(self, batch_id):
        return []


class InMemoryOrgRepo(IOrganizationRepository):
    def __init__(self):
        self.institutions: dict[str, Institution] = {}

    def create_institution(self, institution):
        self.institutions[institution.id] = institution
        return institution

    def get_institution_by_id(self, institution_id):
        return self.institutions.get(institution_id)

    def get_institution_by_code(self, code):
        for inst in self.institutions.values():
            if inst.code == code:
                return inst
        return None

    def list_institutions(self, skip=0, limit=50):
        return list(self.institutions.values())[skip : skip + limit]

    def create_unit(self, unit):
        return unit

    def get_unit_by_id(self, unit_id):
        return None

    def list_units_by_institution(self, institution_id, skip=0, limit=50):
        return []


@pytest.fixture
def setup_service():
    analysis_repo = InMemoryAnalysisRepo()
    evidence_repo = InMemoryEvidenceRepo()
    org_repo = InMemoryOrgRepo()

    # Create test institution
    org_repo.create_institution(
        Institution(
            id="inst-test-1",
            code="TEST-UNIV",
            name="Test University",
            institution_type=UnitType.UNIVERSITY,
            status=EntityStatus.ACTIVE,
        )
    )

    service = CurrentPositionAnalysisService(
        analysis_repository=analysis_repo,
        evidence_repository=evidence_repo,
        organization_repository=org_repo,
    )
    return service, evidence_repo, analysis_repo


def test_metric_directionality_higher_is_better(setup_service):
    service, ev_repo, _ = setup_service

    # Placement rate (HIGHER_IS_BETTER)
    ev_repo.create_metric_definition(
        MetricDefinition(
            metric_key="placement.rate",
            name="Placement Rate",
            domain=MetricDomain.PLACEMENT_EMPLOYER_DEMAND,
            direction=MetricDirection.HIGHER_IS_BETTER,
            default_unit="percent",
        )
    )

    # 2023-2024: 76%, 2024-2025: 81% (Increase = Good)
    ev_repo.record_evidence(
        InstitutionalEvidence(
            id="ev-1",
            institution_id="inst-test-1",
            metric_key="placement.rate",
            domain=MetricDomain.PLACEMENT_EMPLOYER_DEMAND,
            numeric_value=76.0,
            unit="percent",
            period="2023-2024",
            as_of_date=date.today(),
            source_name="Agent 71",
            source_type=SourceType.AGENT,
        )
    )
    ev_repo.record_evidence(
        InstitutionalEvidence(
            id="ev-2",
            institution_id="inst-test-1",
            metric_key="placement.rate",
            domain=MetricDomain.PLACEMENT_EMPLOYER_DEMAND,
            numeric_value=81.0,
            unit="percent",
            period="2024-2025",
            as_of_date=date.today(),
            source_name="Agent 71",
            source_type=SourceType.AGENT,
        )
    )

    res = service.generate_current_position_analysis(
        CurrentPositionAnalysisRequestDTO(
            institution_id="inst-test-1",
            analysis_period="2024-2025",
        )
    )

    placement = next(m for m in res.key_metrics if m.metric_key == "placement.rate")
    assert placement.performance_status == PerformanceStatus.POSITIVE_PERFORMANCE
    assert placement.change_direction == "↑"
    assert placement.percent_change == 6.58
    assert len(res.strengths) >= 1
    assert any("Placement Rate improved" in s.title for s in res.strengths)


def test_metric_directionality_lower_is_better(setup_service):
    service, ev_repo, _ = setup_service

    # Dropout rate (LOWER_IS_BETTER)
    ev_repo.create_metric_definition(
        MetricDefinition(
            metric_key="academic.dropout_rate",
            name="Dropout Rate",
            domain=MetricDomain.ACADEMIC_PERFORMANCE,
            direction=MetricDirection.LOWER_IS_BETTER,
            default_unit="percent",
        )
    )

    # 2023-2024: 8.5%, 2024-2025: 7.2% (Decrease = Good)
    ev_repo.record_evidence(
        InstitutionalEvidence(
            id="ev-3",
            institution_id="inst-test-1",
            metric_key="academic.dropout_rate",
            domain=MetricDomain.ACADEMIC_PERFORMANCE,
            numeric_value=8.5,
            unit="percent",
            period="2023-2024",
            as_of_date=date.today(),
            source_name="Agent 71",
            source_type=SourceType.AGENT,
        )
    )
    ev_repo.record_evidence(
        InstitutionalEvidence(
            id="ev-4",
            institution_id="inst-test-1",
            metric_key="academic.dropout_rate",
            domain=MetricDomain.ACADEMIC_PERFORMANCE,
            numeric_value=7.2,
            unit="percent",
            period="2024-2025",
            as_of_date=date.today(),
            source_name="Agent 71",
            source_type=SourceType.AGENT,
        )
    )

    res = service.generate_current_position_analysis(
        CurrentPositionAnalysisRequestDTO(
            institution_id="inst-test-1",
            analysis_period="2024-2025",
        )
    )

    dropout = next(m for m in res.key_metrics if m.metric_key == "academic.dropout_rate")
    # For LOWER_IS_BETTER, a decrease is POSITIVE performance
    assert dropout.performance_status == PerformanceStatus.POSITIVE_PERFORMANCE
    assert dropout.change_direction == "↓"
    assert any("Dropout Rate improved" in s.title for s in res.strengths)


def test_meaningful_change_thresholding(setup_service):
    service, ev_repo, _ = setup_service

    # Indicator with minor fluctuation: 81.0 -> 81.2 (0.25% change, below 2% threshold)
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
            id="ev-10",
            institution_id="inst-test-1",
            metric_key="placement.rate",
            domain=MetricDomain.PLACEMENT_EMPLOYER_DEMAND,
            numeric_value=81.0,
            unit="percent",
            period="2023-2024",
            as_of_date=date.today(),
            source_name="Agent 71",
            source_type=SourceType.AGENT,
        )
    )
    ev_repo.record_evidence(
        InstitutionalEvidence(
            id="ev-11",
            institution_id="inst-test-1",
            metric_key="placement.rate",
            domain=MetricDomain.PLACEMENT_EMPLOYER_DEMAND,
            numeric_value=81.2,
            unit="percent",
            period="2024-2025",
            as_of_date=date.today(),
            source_name="Agent 71",
            source_type=SourceType.AGENT,
        )
    )

    res = service.generate_current_position_analysis(
        CurrentPositionAnalysisRequestDTO(
            institution_id="inst-test-1",
            analysis_period="2024-2025",
        )
    )

    placement = next(m for m in res.key_metrics if m.metric_key == "placement.rate")
    # Below 2% significance threshold -> NEUTRAL, not classified as a strength
    assert placement.performance_status == PerformanceStatus.NEUTRAL
    assert len(res.strengths) == 0


def test_target_variance_with_directionality(setup_service):
    service, ev_repo, _ = setup_service

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
            id="ev-20",
            institution_id="inst-test-1",
            metric_key="placement.rate",
            domain=MetricDomain.PLACEMENT_EMPLOYER_DEMAND,
            numeric_value=81.0,
            unit="percent",
            period="2024-2025",
            as_of_date=date.today(),
            source_name="Agent 71",
            source_type=SourceType.AGENT,
        )
    )

    # Configured target of 85% -> 81% is BELOW target by 4 pp
    res = service.generate_current_position_analysis(
        CurrentPositionAnalysisRequestDTO(
            institution_id="inst-test-1",
            analysis_period="2024-2025",
            configured_baselines={"placement.rate": 85.0},
        )
    )

    placement = next(m for m in res.key_metrics if m.metric_key == "placement.rate")
    assert placement.performance_status == PerformanceStatus.BELOW_TARGET
    assert placement.target_value == 85.0
    assert placement.target_variance == -4.0
    assert len(res.gaps) >= 1
    assert any("Placement Rate below strategic target" in g.title for g in res.gaps)


def test_deterministic_tie_breaking(setup_service):
    service, ev_repo, _ = setup_service

    ev_repo.create_metric_definition(
        MetricDefinition(
            metric_key="research.citations",
            name="Citations",
            domain=MetricDomain.RESEARCH_PRODUCTIVITY,
            direction=MetricDirection.HIGHER_IS_BETTER,
            default_unit="count",
        )
    )

    # Two observations for the exact same period 2024-2025:
    # Obs A: PROVISIONAL, confidence 0.75, value 2000
    # Obs B: VERIFIED, confidence 0.98, value 2500
    ev_repo.record_evidence(
        InstitutionalEvidence(
            id="ev-tie-a",
            institution_id="inst-test-1",
            metric_key="research.citations",
            domain=MetricDomain.RESEARCH_PRODUCTIVITY,
            numeric_value=2000.0,
            unit="count",
            period="2024-2025",
            as_of_date=date.today(),
            quality_tier=QualityTier.PROVISIONAL,
            confidence_score=0.75,
            source_name="Scraper",
        )
    )
    ev_repo.record_evidence(
        InstitutionalEvidence(
            id="ev-tie-b",
            institution_id="inst-test-1",
            metric_key="research.citations",
            domain=MetricDomain.RESEARCH_PRODUCTIVITY,
            numeric_value=2500.0,
            unit="count",
            period="2024-2025",
            as_of_date=date.today(),
            quality_tier=QualityTier.VERIFIED,
            confidence_score=0.98,
            source_name="Agent 20",
            source_type=SourceType.AGENT,
        )
    )

    res = service.generate_current_position_analysis(
        CurrentPositionAnalysisRequestDTO(
            institution_id="inst-test-1",
            analysis_period="2024-2025",
        )
    )

    citations = next(m for m in res.key_metrics if m.metric_key == "research.citations")
    # Deterministic tie-breaker must select the VERIFIED record (ev-tie-b) with value 2500
    assert citations.latest_value == 2500.0
    assert citations.quality_tier == QualityTier.VERIFIED
    assert citations.evidence_id == "ev-tie-b"


def test_missing_data_isolated_as_data_gap_not_weakness(setup_service):
    service, ev_repo, _ = setup_service

    # Registered metric with NO observations
    ev_repo.create_metric_definition(
        MetricDefinition(
            metric_key="faculty.capability_index",
            name="Faculty Capability Index",
            domain=MetricDomain.FACULTY_CAPABILITY,
            default_unit="index",
        )
    )

    res = service.generate_current_position_analysis(
        CurrentPositionAnalysisRequestDTO(
            institution_id="inst-test-1",
            analysis_period="2024-2025",
        )
    )

    # Missing evidence must NOT be an institutional weakness
    assert len(res.weaknesses) == 0

    # It MUST be isolated into data_gaps
    assert len(res.data_gaps) >= 1
    assert any("Missing Evidence: Faculty Capability Index" in g.title for g in res.data_gaps)
    assert any(g.category == FindingCategory.DATA_GAP for g in res.data_gaps)
