"""Unit tests for Evidence validation, provenance, and academic periods."""

import pytest
from pydantic import ValidationError as PydanticValidationError
from agent72.application.dtos.evidence_dto import EvidenceIngestionDTO
from agent72.domain.models.evidence import (
    InstitutionalEvidence,
    MetricDomain,
    QualityTier,
    SourceType,
)


def test_valid_academic_period_formats():
    valid_periods = ["2024-2025", "2025-2026", "2024-Q1", "2024-Q4", "2025"]
    for p in valid_periods:
        dto = EvidenceIngestionDTO(
            institution_id="inst-1",
            metric_key="research.pubs",
            domain=MetricDomain.RESEARCH_PRODUCTIVITY,
            numeric_value=42.0,
            unit="count",
            period=p,
            source_type=SourceType.AGENT,
            source_name="Agent 20",
        )
        assert dto.period == p


def test_invalid_academic_period_raises_validation_error():
    invalid_periods = ["invalid-period", "2024/2025", "24-25", "Q1-2024", "2024-Q5"]
    for p in invalid_periods:
        with pytest.raises(PydanticValidationError) as excinfo:
            EvidenceIngestionDTO(
                institution_id="inst-1",
                metric_key="research.pubs",
                domain=MetricDomain.RESEARCH_PRODUCTIVITY,
                numeric_value=42.0,
                unit="count",
                period=p,
                source_name="Agent 20",
            )
        assert "Invalid academic period" in str(excinfo.value)


def test_confidence_score_boundaries():
    # Valid boundaries
    dto_zero = EvidenceIngestionDTO(
        institution_id="inst-1",
        metric_key="academic.retention",
        domain=MetricDomain.ACADEMIC_PERFORMANCE,
        numeric_value=85.0,
        unit="percent",
        period="2024-2025",
        source_name="Manual Entry",
        confidence_score=0.0,
    )
    assert dto_zero.confidence_score == 0.0

    dto_one = EvidenceIngestionDTO(
        institution_id="inst-1",
        metric_key="academic.retention",
        domain=MetricDomain.ACADEMIC_PERFORMANCE,
        numeric_value=85.0,
        unit="percent",
        period="2024-2025",
        source_name="Manual Entry",
        confidence_score=1.0,
    )
    assert dto_one.confidence_score == 1.0

    # Invalid > 1.0
    with pytest.raises(PydanticValidationError):
        EvidenceIngestionDTO(
            institution_id="inst-1",
            metric_key="academic.retention",
            domain=MetricDomain.ACADEMIC_PERFORMANCE,
            numeric_value=85.0,
            unit="percent",
            period="2024-2025",
            source_name="Manual Entry",
            confidence_score=1.5,
        )


def test_domain_model_provenance_validation():
    ev = InstitutionalEvidence(
        institution_id="inst-1",
        metric_key="admissions.enrolled",
        domain=MetricDomain.ADMISSIONS_MARKET,
        numeric_value=1200.0,
        unit="count",
        period="2024-2025",
        source_type=SourceType.AGENT,
        source_name="Agent 38",
        confidence_score=0.95,
        quality_tier=QualityTier.VERIFIED,
    )
    ev.validate_provenance()  # Should not raise

    # Invalid confidence score on domain model
    ev.confidence_score = 1.2
    with pytest.raises(ValueError) as excinfo:
        ev.validate_provenance()
    assert "Confidence score" in str(excinfo.value)
