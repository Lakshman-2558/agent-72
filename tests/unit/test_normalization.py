"""Unit tests for Evidence Normalizer."""

import pytest
from agent72.application.services.normalization import EvidenceNormalizer
from agent72.domain.models.evidence import MetricDomain
from agent72.core.exceptions import ValidationError


def test_metric_key_normalization():
    assert EvidenceNormalizer.normalize_metric_key(" RESEARCH.publications_q1 ") == "research.publications.q1"
    assert EvidenceNormalizer.normalize_metric_key("placement-rate-pct") == "placement.rate.pct"
    assert EvidenceNormalizer.normalize_metric_key("admissions..intake...fill") == "admissions.intake.fill"
    assert EvidenceNormalizer.normalize_metric_key("faculty_cadre_ratio") == "faculty.cadre.ratio"

    with pytest.raises(ValidationError):
        EvidenceNormalizer.normalize_metric_key("   ")


def test_domain_synonym_normalization():
    assert EvidenceNormalizer.normalize_domain("research") == MetricDomain.RESEARCH_PRODUCTIVITY
    assert EvidenceNormalizer.normalize_domain("RESEARCH_PRODUCTIVITY") == MetricDomain.RESEARCH_PRODUCTIVITY
    assert EvidenceNormalizer.normalize_domain("admissions") == MetricDomain.ADMISSIONS_MARKET
    assert EvidenceNormalizer.normalize_domain("placement") == MetricDomain.PLACEMENT_EMPLOYER_DEMAND
    assert EvidenceNormalizer.normalize_domain("faculty") == MetricDomain.FACULTY_CAPABILITY
    assert EvidenceNormalizer.normalize_domain("financial") == MetricDomain.FINANCE_RESOURCES
    assert EvidenceNormalizer.normalize_domain("regulatory") == MetricDomain.EXTERNAL_REGULATORY
    assert EvidenceNormalizer.normalize_domain("peers") == MetricDomain.PEER_COMPETITOR

    with pytest.raises(ValidationError):
        EvidenceNormalizer.normalize_domain("non_existent_domain")


def test_unit_normalization():
    assert EvidenceNormalizer.normalize_unit("%") == "percent"
    assert EvidenceNormalizer.normalize_unit("pct") == "percent"
    assert EvidenceNormalizer.normalize_unit("percentage") == "percent"
    assert EvidenceNormalizer.normalize_unit("cnt") == "count"
    assert EvidenceNormalizer.normalize_unit("num") == "count"
    assert EvidenceNormalizer.normalize_unit("inr") == "INR"
    assert EvidenceNormalizer.normalize_unit("rs") == "INR"
    assert EvidenceNormalizer.normalize_unit("usd") == "USD"
    assert EvidenceNormalizer.normalize_unit("cgpa") == "CGPA"


def test_academic_period_normalization():
    # Shorthand 2-digit format
    assert EvidenceNormalizer.normalize_academic_period("2024-25") == "2024-2025"
    assert EvidenceNormalizer.normalize_academic_period("2025-26") == "2025-2026"

    # Full 4-digit format
    assert EvidenceNormalizer.normalize_academic_period("2024-2025") == "2024-2025"

    # Quarterly format
    assert EvidenceNormalizer.normalize_academic_period("2024-q1") == "2024-Q1"
    assert EvidenceNormalizer.normalize_academic_period("2024-Q3") == "2024-Q3"

    # Year format
    assert EvidenceNormalizer.normalize_academic_period("2024") == "2024"

    # Invalid non-consecutive years
    with pytest.raises(ValidationError):
        EvidenceNormalizer.normalize_academic_period("2024-2026")

    # Invalid format
    with pytest.raises(ValidationError):
        EvidenceNormalizer.normalize_academic_period("invalid-period")


def test_value_validation():
    num, txt = EvidenceNormalizer.validate_and_normalize_value(95.5, "Some note")
    assert num == 95.5
    assert txt == "Some note"

    # Both missing
    with pytest.raises(ValidationError):
        EvidenceNormalizer.validate_and_normalize_value(None, None)

    # Infinite or NaN rejected
    with pytest.raises(ValidationError):
        EvidenceNormalizer.validate_and_normalize_value(float("nan"), None)

    with pytest.raises(ValidationError):
        EvidenceNormalizer.validate_and_normalize_value(float("inf"), None)
