"""Unit tests for dynamic EvidenceFreshnessService."""

from datetime import date, timedelta
from agent72.application.services.freshness import EvidenceFreshnessService
from agent72.domain.models.evidence import (
    InstitutionalEvidence,
    MetricDomain,
    FreshnessStatus,
)


def test_freshness_evaluation_fresh():
    today = date(2026, 9, 11)
    service = EvidenceFreshnessService()

    # Admissions has 90 days threshold. Age = 10 days -> FRESH (<= 90 * 0.75 = 67.5)
    ev = InstitutionalEvidence(
        institution_id="inst-1",
        metric_key="admissions.intake",
        domain=MetricDomain.ADMISSIONS_MARKET,
        as_of_date=today - timedelta(days=10),
    )
    meta = service.evaluate_freshness(ev, reference_date=today)
    assert meta.status == FreshnessStatus.FRESH
    assert meta.age_days == 10
    assert meta.threshold_days == 90


def test_freshness_evaluation_aging():
    today = date(2026, 9, 11)
    service = EvidenceFreshnessService()

    # Admissions has 90 days threshold. Age = 75 days -> AGING (> 67.5 and <= 90)
    ev = InstitutionalEvidence(
        institution_id="inst-1",
        metric_key="admissions.intake",
        domain=MetricDomain.ADMISSIONS_MARKET,
        as_of_date=today - timedelta(days=75),
    )
    meta = service.evaluate_freshness(ev, reference_date=today)
    assert meta.status == FreshnessStatus.AGING
    assert meta.age_days == 75


def test_freshness_evaluation_stale():
    today = date(2026, 9, 11)
    service = EvidenceFreshnessService()

    # Admissions has 90 days threshold. Age = 120 days -> STALE (> 90)
    ev = InstitutionalEvidence(
        institution_id="inst-1",
        metric_key="admissions.intake",
        domain=MetricDomain.ADMISSIONS_MARKET,
        as_of_date=today - timedelta(days=120),
    )
    meta = service.evaluate_freshness(ev, reference_date=today)
    assert meta.status == FreshnessStatus.STALE
    assert meta.age_days == 120


def test_configurable_threshold_overrides():
    today = date(2026, 9, 11)
    # Custom policy override: Research = 180 days instead of 365
    custom_service = EvidenceFreshnessService(thresholds_override={"RESEARCH_PRODUCTIVITY": 180})

    ev = InstitutionalEvidence(
        institution_id="inst-1",
        metric_key="research.pubs",
        domain=MetricDomain.RESEARCH_PRODUCTIVITY,
        as_of_date=today - timedelta(days=200),
    )
    meta = custom_service.evaluate_freshness(ev, reference_date=today)
    assert meta.threshold_days == 180
    assert meta.status == FreshnessStatus.STALE
