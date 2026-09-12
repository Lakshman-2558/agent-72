"""Canonical normalization service for incoming institutional evidence."""

import math
import re
from typing import Optional, Tuple
from agent72.domain.models.evidence import MetricDomain, SourceType
from agent72.core.exceptions import ValidationError

# Domain synonyms mapping
DOMAIN_SYNONYMS = {
    "academic": MetricDomain.ACADEMIC_PERFORMANCE,
    "academic_performance": MetricDomain.ACADEMIC_PERFORMANCE,
    "academics": MetricDomain.ACADEMIC_PERFORMANCE,
    "admissions": MetricDomain.ADMISSIONS_MARKET,
    "admissions_market": MetricDomain.ADMISSIONS_MARKET,
    "admission": MetricDomain.ADMISSIONS_MARKET,
    "placement": MetricDomain.PLACEMENT_EMPLOYER_DEMAND,
    "placement_employer_demand": MetricDomain.PLACEMENT_EMPLOYER_DEMAND,
    "placements": MetricDomain.PLACEMENT_EMPLOYER_DEMAND,
    "research": MetricDomain.RESEARCH_PRODUCTIVITY,
    "research_productivity": MetricDomain.RESEARCH_PRODUCTIVITY,
    "faculty": MetricDomain.FACULTY_CAPABILITY,
    "faculty_capability": MetricDomain.FACULTY_CAPABILITY,
    "infrastructure": MetricDomain.INFRASTRUCTURE,
    "finance": MetricDomain.FINANCE_RESOURCES,
    "finance_resources": MetricDomain.FINANCE_RESOURCES,
    "financial": MetricDomain.FINANCE_RESOURCES,
    "regulatory": MetricDomain.EXTERNAL_REGULATORY,
    "external_regulatory": MetricDomain.EXTERNAL_REGULATORY,
    "competitor": MetricDomain.PEER_COMPETITOR,
    "peer_competitor": MetricDomain.PEER_COMPETITOR,
    "peers": MetricDomain.PEER_COMPETITOR,
}

# Unit synonyms and standardizations
UNIT_STANDARDIZATION = {
    "%": "percent",
    "pct": "percent",
    "percentage": "percent",
    "ratio": "ratio",
    "rate": "ratio",
    "count": "count",
    "cnt": "count",
    "num": "count",
    "number": "count",
    "inr": "INR",
    "rs": "INR",
    "rupees": "INR",
    "usd": "USD",
    "days": "days",
    "months": "months",
    "years": "years",
    "rank": "rank",
    "score": "score",
    "index": "index",
    "gpa": "GPA",
    "cgpa": "CGPA",
}


class EvidenceNormalizer:
    """Normalizes raw input fields into canonical representations without altering numerical meaning."""

    @staticmethod
    def normalize_metric_key(key: str) -> str:
        if not key or not key.strip():
            raise ValidationError("Metric key cannot be empty.")
        trimmed = key.strip().lower()
        # Replace non-alphanumeric except dots with dots
        sanitized = re.sub(r"[^a-z0-9.]+", ".", trimmed)
        # Collapse multiple dots and strip leading/trailing dots
        sanitized = re.sub(r"\.+", ".", sanitized).strip(".")
        if not sanitized:
            raise ValidationError(f"Metric key '{key}' contains no valid characters.")
        return sanitized

    @staticmethod
    def normalize_domain(domain_input: str | MetricDomain) -> MetricDomain:
        if isinstance(domain_input, MetricDomain):
            return domain_input

        clean = domain_input.strip().lower().replace("-", "_").replace(" ", "_")
        if clean in DOMAIN_SYNONYMS:
            return DOMAIN_SYNONYMS[clean]

        try:
            return MetricDomain(domain_input.upper())
        except ValueError:
            valid_options = ", ".join([d.value for d in MetricDomain])
            raise ValidationError(
                f"Unknown domain '{domain_input}'. Must be one of: {valid_options}"
            )

    @staticmethod
    def normalize_unit(unit_input: str) -> str:
        if not unit_input or not unit_input.strip():
            raise ValidationError("Measurement unit cannot be empty.")
        clean = unit_input.strip().lower()
        return UNIT_STANDARDIZATION.get(clean, unit_input.strip())

    @staticmethod
    def normalize_academic_period(period_input: str) -> str:
        """
        Normalizes academic periods:
        e.g. '2024-25' -> '2024-2025'
        '2024-2025' -> '2024-2025'
        '2024-q1' -> '2024-Q1'
        '2024' -> '2024'
        """
        if not period_input or not period_input.strip():
            raise ValidationError("Academic period cannot be empty.")

        clean = period_input.strip()

        # Handle 2-digit end year like 2024-25
        match_shorthand = re.match(r"^(\d{4})-(\d{2})$", clean)
        if match_shorthand:
            start_yr = int(match_shorthand.group(1))
            end_short = int(match_shorthand.group(2))
            century = start_yr // 100 * 100
            end_yr = century + end_short
            if end_yr != start_yr + 1:
                raise ValidationError(
                    f"Invalid academic period '{clean}'. End year must follow start year."
                )
            return f"{start_yr}-{end_yr}"

        # Handle full 4-digit period like 2024-2025
        match_full = re.match(r"^(\d{4})-(\d{4})$", clean)
        if match_full:
            start_yr = int(match_full.group(1))
            end_yr = int(match_full.group(2))
            if end_yr != start_yr + 1:
                raise ValidationError(
                    f"Academic period span must be exactly 1 year: '{clean}'."
                )
            return f"{start_yr}-{end_yr}"

        # Handle quarterly period like 2024-Q1 or 2024-q1
        match_quarter = re.match(r"^(\d{4})-[qQ]([1-4])$", clean)
        if match_quarter:
            return f"{match_quarter.group(1)}-Q{match_quarter.group(2)}"

        # Handle calendar year like 2024
        match_year = re.match(r"^(\d{4})$", clean)
        if match_year:
            return match_year.group(1)

        raise ValidationError(
            f"Invalid academic period '{period_input}'. Expected formats: 'YYYY-YYYY' (e.g. '2024-2025'), 'YYYY-YY' (e.g. '2024-25'), 'YYYY-Q#' (e.g. '2024-Q1'), or 'YYYY'."
        )

    @staticmethod
    def validate_and_normalize_value(
        numeric_value: Optional[float], text_value: Optional[str]
    ) -> Tuple[Optional[float], Optional[str]]:
        """Ensures at least one value is present and validates numeric finite bounds."""
        if numeric_value is None and (text_value is None or not text_value.strip()):
            raise ValidationError("Either numeric_value or text_value must be provided.")

        if numeric_value is not None:
            if math.isnan(numeric_value) or math.isinf(numeric_value):
                raise ValidationError(f"Numeric value '{numeric_value}' is invalid (NaN or Infinite).")

        clean_text = text_value.strip() if text_value else None
        return numeric_value, clean_text
