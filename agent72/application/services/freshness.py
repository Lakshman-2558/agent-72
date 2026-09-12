"""Service for dynamic evaluation of evidence freshness."""

from datetime import date, datetime, timezone
from typing import Dict, Optional
from agent72.core.config import settings
from agent72.domain.models.evidence import (
    InstitutionalEvidence,
    FreshnessMetadata,
    FreshnessStatus,
    MetricDomain,
)


class EvidenceFreshnessService:
    """Calculates data freshness dynamically at query time using configuration-driven policies."""

    def __init__(self, thresholds_override: Optional[Dict[str, int]] = None) -> None:
        self.thresholds = thresholds_override or settings.FRESHNESS_THRESHOLDS_DAYS

    def get_threshold_days(self, domain: MetricDomain | str) -> int:
        domain_name = domain.value if isinstance(domain, MetricDomain) else str(domain)
        return self.thresholds.get(domain_name, settings.DEFAULT_FRESHNESS_THRESHOLD_DAYS)

    def evaluate_freshness(
        self,
        evidence: InstitutionalEvidence,
        reference_date: Optional[date] = None,
    ) -> FreshnessMetadata:
        ref_date = reference_date or datetime.now(timezone.utc).date()
        obs_date = evidence.as_of_date or ref_date
        age_days = max(0, (ref_date - obs_date).days)
        threshold_days = self.get_threshold_days(evidence.domain)

        # Freshness determination:
        # FRESH: age <= 75% of threshold
        # AGING: 75% < age <= 100% of threshold
        # STALE: age > threshold
        if age_days <= int(threshold_days * 0.75):
            status = FreshnessStatus.FRESH
        elif age_days <= threshold_days:
            status = FreshnessStatus.AGING
        else:
            status = FreshnessStatus.STALE

        return FreshnessMetadata(
            status=status,
            age_days=age_days,
            threshold_days=threshold_days,
            as_of_date=obs_date,
        )

    def enrich_evidence(
        self,
        evidence: InstitutionalEvidence,
        reference_date: Optional[date] = None,
    ) -> InstitutionalEvidence:
        """Enriches an evidence domain instance with calculated freshness metadata."""
        freshness_meta = self.evaluate_freshness(evidence, reference_date)
        evidence.freshness = freshness_meta
        evidence.is_stale = (freshness_meta.status == FreshnessStatus.STALE)
        return evidence
