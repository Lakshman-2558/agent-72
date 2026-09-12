"""Deterministic Current Institutional Position Analysis Engine."""

from datetime import datetime, timezone
import logging
from typing import Any, Dict, List, Optional, Tuple

from agent72.application.dtos.analysis_dto import (
    AnalysisListResponseDTO,
    ConfidenceAssessmentDTO,
    CurrentPositionAnalysisRequestDTO,
    CurrentPositionAnalysisResponseDTO,
    EvidenceReferenceDTO,
    MetricAssessmentDTO,
    PositionFindingDTO,
)
from agent72.core.config import settings
from agent72.core.exceptions import EntityNotFoundException, ValidationError
from agent72.domain.interfaces.analysis_repository import IAnalysisRepository
from agent72.domain.interfaces.evidence_repository import IEvidenceRepository
from agent72.domain.interfaces.organization_repository import IOrganizationRepository
from agent72.domain.interfaces.plan_repository import IPlanRepository
from agent72.domain.models.analysis import (
    ComparisonType,
    ConfidenceAssessment,
    CurrentPositionAnalysis,
    EvidenceReference,
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
    QualityTier,
)
from agent72.application.services.freshness import EvidenceFreshnessService

logger = logging.getLogger(__name__)

QUALITY_TIER_WEIGHTS = {
    QualityTier.VERIFIED: 3,
    QualityTier.ESTIMATED: 2,
    QualityTier.PROVISIONAL: 1,
}


class CurrentPositionAnalysisService:
    """
    Deterministic Current Institutional Position Analysis Service.

    Analyzes institutional evidence across registered metrics, calculates polarity-aware
    differences against preceding observations and targets, isolates data quality deficiencies,
    and produces explainable, immutable strategic position snapshots.
    """

    def __init__(
        self,
        analysis_repository: IAnalysisRepository,
        evidence_repository: IEvidenceRepository,
        organization_repository: IOrganizationRepository,
        plan_repository: Optional[IPlanRepository] = None,
        freshness_service: Optional[EvidenceFreshnessService] = None,
    ):
        self.analysis_repo = analysis_repository
        self.evidence_repo = evidence_repository
        self.org_repo = organization_repository
        self.plan_repo = plan_repository
        self.freshness_service = freshness_service or EvidenceFreshnessService()

    def _select_best_observation_for_period(
        self, observations: List[InstitutionalEvidence]
    ) -> InstitutionalEvidence:
        """
        Deterministic tie-breaking for multiple observations within the same period:
        1. Quality tier priority (VERIFIED > ESTIMATED > PROVISIONAL)
        2. Confidence score (descending)
        3. as_of_date (descending)
        4. captured_at (descending)
        5. id (lexicographical ascending for 100% determinism)
        """
        def tie_key(ev: InstitutionalEvidence):
            tier_val = QUALITY_TIER_WEIGHTS.get(ev.quality_tier, 0)
            as_of_val = ev.as_of_date.isoformat() if ev.as_of_date else ""
            captured_val = ev.captured_at.isoformat() if ev.captured_at else ""
            id_val = ev.id or ""
            return (tier_val, ev.confidence_score, as_of_val, captured_val, id_val)

        return max(observations, key=tie_key)

    def _get_latest_and_previous_observations(
        self,
        observations: List[InstitutionalEvidence],
        target_period: str,
    ) -> Tuple[Optional[InstitutionalEvidence], Optional[InstitutionalEvidence]]:
        """
        Groups observations by period and identifies:
        - latest observation: matching target_period, or most recent period strictly up to target_period
        - previous observation: the immediately preceding historical period observation
        """
        if not observations:
            return None, None

        # Group by period and resolve ties per period
        by_period: Dict[str, List[InstitutionalEvidence]] = {}
        for ev in observations:
            by_period.setdefault(ev.period, []).append(ev)

        period_winners: Dict[str, InstitutionalEvidence] = {
            p: self._select_best_observation_for_period(evs)
            for p, evs in by_period.items()
        }

        # Sort periods chronologically
        sorted_periods = sorted(period_winners.keys())

        # Find latest observation
        latest_period: Optional[str] = None
        if target_period in period_winners:
            latest_period = target_period
        else:
            # Pick most recent period <= target_period
            candidates = [p for p in sorted_periods if p <= target_period]
            if candidates:
                latest_period = candidates[-1]
            elif sorted_periods:
                latest_period = sorted_periods[-1]

        if not latest_period:
            return None, None

        latest_obs = period_winners[latest_period]

        # Find previous observation strictly before latest_period
        prior_periods = [p for p in sorted_periods if p < latest_period]
        previous_obs = period_winners[prior_periods[-1]] if prior_periods else None

        return latest_obs, previous_obs

    def _get_strategic_target(self, institution_id: str, metric_key: str) -> Optional[float]:
        """Retrieves active strategic plan objective target for a metric if available."""
        if not self.plan_repo:
            return None

        plans = self.plan_repo.list_all(skip=0, limit=20)
        for p in plans:
            # Check active or draft plans for this institution
            if getattr(p, "institution_id", None) == institution_id:
                for obj in p.objectives:
                    if getattr(obj, "metric_key", None) == metric_key and obj.target_value is not None:
                        return obj.target_value
        return None

    def _evaluate_metric(
        self,
        metric: MetricDefinition,
        institution_id: str,
        unit_id: Optional[str],
        analysis_period: str,
        configured_baselines: Optional[Dict[str, float]],
        include_plan_targets: bool,
    ) -> Tuple[MetricAssessment, Optional[InstitutionalEvidence]]:
        """Evaluates an individual metric's observations, changes, and target variances."""
        series = self.evidence_repo.get_historical_series(
            institution_id=institution_id,
            metric_key=metric.metric_key,
            unit_id=unit_id,
            skip=0,
            limit=500,
        )

        latest_obs, prev_obs = self._get_latest_and_previous_observations(series, analysis_period)

        if not latest_obs:
            assessment = MetricAssessment(
                metric_key=metric.metric_key,
                metric_name=metric.name,
                domain=metric.domain,
                unit=metric.default_unit,
                direction=metric.direction,
                latest_value=None,
                latest_period=None,
                previous_value=None,
                previous_period=None,
                change_direction=None,
                absolute_change=None,
                percent_change=None,
                target_value=None,
                target_variance=None,
                performance_status=PerformanceStatus.INSUFFICIENT_DATA,
                comparison_status="comparison_unavailable",
                freshness_status=FreshnessStatus.STALE,
                quality_tier=QualityTier.PROVISIONAL,
                confidence_score=0.0,
                evidence_id=None,
            )
            return assessment, None

        # Dynamically evaluate freshness on latest observation
        self.freshness_service.enrich_evidence(latest_obs)
        freshness_status = latest_obs.freshness.status if latest_obs.freshness else FreshnessStatus.FRESH

        latest_val = latest_obs.numeric_value
        prev_val = prev_obs.numeric_value if prev_obs else None

        # Calculate change between periods
        abs_change: Optional[float] = None
        pct_change: Optional[float] = None
        change_dir: Optional[str] = None
        comparison_status = "comparison_unavailable"

        if latest_val is not None and prev_val is not None:
            comparison_status = "AVAILABLE"
            abs_change = round(latest_val - prev_val, 4)
            if abs_change > 0:
                change_dir = "↑"
            elif abs_change < 0:
                change_dir = "↓"
            else:
                change_dir = "→"

            if prev_val != 0:
                pct_change = round(((latest_val - prev_val) / abs(prev_val)) * 100.0, 2)

        # Check for target / baseline
        target_val: Optional[float] = None
        if configured_baselines and metric.metric_key in configured_baselines:
            target_val = configured_baselines[metric.metric_key]
        elif include_plan_targets:
            target_val = self._get_strategic_target(institution_id, metric.metric_key)

        target_variance: Optional[float] = None
        if target_val is not None and latest_val is not None:
            target_variance = round(latest_val - target_val, 4)

        # Evaluate significance and performance status considering metric directionality
        is_significant = False
        if pct_change is not None:
            is_significant = abs(pct_change) >= settings.MIN_SIGNIFICANT_CHANGE_PERCENT
        elif abs_change is not None:
            is_significant = abs(abs_change) > 0.0

        direction = metric.direction
        perf_status = PerformanceStatus.NEUTRAL

        if target_val is not None and latest_val is not None:
            if direction == MetricDirection.HIGHER_IS_BETTER:
                if latest_val > target_val:
                    perf_status = PerformanceStatus.EXCEEDS_TARGET
                elif latest_val == target_val:
                    perf_status = PerformanceStatus.MEETS_TARGET
                else:
                    perf_status = PerformanceStatus.BELOW_TARGET
            elif direction == MetricDirection.LOWER_IS_BETTER:
                if latest_val < target_val:
                    perf_status = PerformanceStatus.EXCEEDS_TARGET
                elif latest_val == target_val:
                    perf_status = PerformanceStatus.MEETS_TARGET
                else:
                    perf_status = PerformanceStatus.BELOW_TARGET
            else:  # TARGET_RANGE or NEUTRAL
                perf_status = PerformanceStatus.MEETS_TARGET if abs(latest_val - target_val) < 0.01 else PerformanceStatus.NEUTRAL

        elif comparison_status == "AVAILABLE" and abs_change is not None:
            if not is_significant:
                perf_status = PerformanceStatus.NEUTRAL
            else:
                if direction == MetricDirection.HIGHER_IS_BETTER:
                    perf_status = PerformanceStatus.POSITIVE_PERFORMANCE if abs_change > 0 else PerformanceStatus.NEGATIVE_PERFORMANCE
                elif direction == MetricDirection.LOWER_IS_BETTER:
                    perf_status = PerformanceStatus.POSITIVE_PERFORMANCE if abs_change < 0 else PerformanceStatus.NEGATIVE_PERFORMANCE
                else:
                    perf_status = PerformanceStatus.NEUTRAL
        else:
            perf_status = PerformanceStatus.NEUTRAL

        assessment = MetricAssessment(
            metric_key=metric.metric_key,
            metric_name=metric.name,
            domain=metric.domain,
            unit=metric.default_unit,
            direction=direction,
            latest_value=latest_val,
            latest_period=latest_obs.period,
            previous_value=prev_val,
            previous_period=prev_obs.period if prev_obs else None,
            change_direction=change_dir,
            absolute_change=abs_change,
            percent_change=pct_change,
            target_value=target_val,
            target_variance=target_variance,
            performance_status=perf_status,
            comparison_status=comparison_status,
            freshness_status=freshness_status,
            quality_tier=latest_obs.quality_tier,
            confidence_score=latest_obs.confidence_score,
            evidence_id=latest_obs.id,
        )
        return assessment, latest_obs

    def _calculate_overall_confidence(
        self,
        assessments: List[MetricAssessment],
        data_gaps_count: int,
    ) -> ConfidenceAssessment:
        """Calculates transparent, factor-based overall confidence."""
        evaluated_metrics = [m for m in assessments if m.latest_value is not None]
        total_count = len(assessments)

        if not evaluated_metrics:
            return ConfidenceAssessment(
                score=0.2,
                level="LOW",
                factors={
                    "total_indicators": total_count,
                    "evaluated_indicators": 0,
                    "data_gaps": data_gaps_count,
                },
                explanation="Insufficient evidence across all registered institutional indicators.",
            )

        # Factor 1: Evidence confidence average (30%)
        avg_evidence_conf = sum(m.confidence_score for m in evaluated_metrics) / len(evaluated_metrics)

        # Factor 2: Quality tier ratio (25%)
        verified_count = sum(1 for m in evaluated_metrics if m.quality_tier == QualityTier.VERIFIED)
        quality_ratio = verified_count / len(evaluated_metrics)

        # Factor 3: Freshness ratio (25%)
        freshness_points = 0.0
        for m in evaluated_metrics:
            if m.freshness_status == FreshnessStatus.FRESH:
                freshness_points += 1.0
            elif m.freshness_status == FreshnessStatus.AGING:
                freshness_points += 0.5
        freshness_ratio = freshness_points / len(evaluated_metrics)

        # Factor 4: Comparison availability (20%)
        comp_count = sum(1 for m in evaluated_metrics if m.comparison_status == "AVAILABLE" or m.target_value is not None)
        comp_ratio = comp_count / len(evaluated_metrics)

        # Data gap penalty
        gap_penalty = (data_gaps_count / total_count) * 0.20 if total_count > 0 else 0.0

        raw_score = (
            (avg_evidence_conf * 0.30)
            + (quality_ratio * 0.25)
            + (freshness_ratio * 0.25)
            + (comp_ratio * 0.20)
            - gap_penalty
        )
        score = max(0.1, min(1.0, round(raw_score, 2)))

        level = "HIGH" if score >= 0.80 else ("MEDIUM" if score >= 0.50 else "LOW")

        factors = {
            "total_indicators_registered": total_count,
            "evaluated_indicators": len(evaluated_metrics),
            "data_gaps_count": data_gaps_count,
            "average_evidence_confidence": round(avg_evidence_conf, 2),
            "verified_evidence_ratio": round(quality_ratio, 2),
            "freshness_ratio": round(freshness_ratio, 2),
            "comparison_availability_ratio": round(comp_ratio, 2),
            "data_gap_penalty": round(gap_penalty, 2),
        }

        explanation = (
            f"Confidence is {level} ({score*100:.0f}%). "
            f"Based on {len(evaluated_metrics)}/{total_count} evaluated indicators with {quality_ratio*100:.0f}% verified evidence, "
            f"{freshness_ratio*100:.0f}% freshness index, and {data_gaps_count} isolated data gaps."
        )

        return ConfidenceAssessment(score=score, level=level, factors=factors, explanation=explanation)

    def generate_current_position_analysis(
        self, dto: CurrentPositionAnalysisRequestDTO
    ) -> CurrentPositionAnalysisResponseDTO:
        """
        Executes deterministic current position analysis for an institution.
        Isolates data gaps, detects polarity-aware strengths/weaknesses/gaps,
        computes transparent confidence, and stores an immutable snapshot.
        """
        # 1. Verify Institutional scope
        inst = self.org_repo.get_institution_by_id(dto.institution_id)
        if not inst:
            raise EntityNotFoundException("Institution", dto.institution_id)

        if dto.organizational_unit_id:
            unit = self.org_repo.get_unit_by_id(dto.organizational_unit_id)
            if not unit:
                raise EntityNotFoundException("OrganizationalUnit", dto.organizational_unit_id)
            if unit.institution_id != dto.institution_id:
                raise ValidationError(
                    f"Unit '{dto.organizational_unit_id}' does not belong to institution '{dto.institution_id}'."
                )

        # 2. Retrieve all registered metric definitions
        metric_defs = self.evidence_repo.list_metric_definitions()
        if not metric_defs:
            raise ValidationError("No metric definitions are registered in the catalog.")

        # 3. Evaluate each metric and collect underlying evidence
        key_metrics: List[MetricAssessment] = []
        evidence_refs: List[EvidenceReference] = []
        seen_evidence_ids = set()

        strengths: List[PositionFinding] = []
        weaknesses: List[PositionFinding] = []
        gaps: List[PositionFinding] = []
        constraints: List[PositionFinding] = []
        opportunities: List[PositionFinding] = []
        structural_risks: List[PositionFinding] = []
        data_gaps: List[PositionFinding] = []

        for m_def in metric_defs:
            assessment, latest_obs = self._evaluate_metric(
                metric=m_def,
                institution_id=dto.institution_id,
                unit_id=dto.organizational_unit_id,
                analysis_period=dto.analysis_period,
                configured_baselines=dto.configured_baselines,
                include_plan_targets=dto.include_plan_targets,
            )
            key_metrics.append(assessment)

            if latest_obs and latest_obs.id and latest_obs.id not in seen_evidence_ids:
                seen_evidence_ids.add(latest_obs.id)
                evidence_refs.append(
                    EvidenceReference(
                        evidence_id=latest_obs.id,
                        metric_key=latest_obs.metric_key,
                        period=latest_obs.period,
                        as_of_date=latest_obs.as_of_date,
                        source_name=latest_obs.source_name,
                        source_type=latest_obs.source_type,
                        confidence_score=latest_obs.confidence_score,
                        quality_tier=latest_obs.quality_tier,
                        freshness_status=assessment.freshness_status,
                    )
                )

            # Rule #6: Missing / Stale / Provisional Evidence isolation
            if latest_obs is None:
                data_gaps.append(
                    PositionFinding(
                        category=FindingCategory.DATA_GAP,
                        title=f"Missing Evidence: {m_def.name}",
                        description=f"No evidence observations have been recorded for indicator '{m_def.metric_key}'.",
                        severity=FindingSeverity.HIGH,
                        metric_key=m_def.metric_key,
                        rationale="Information deficiency: indicator cannot be evaluated until reliable evidence is ingested.",
                    )
                )
                continue

            if assessment.freshness_status == FreshnessStatus.STALE:
                data_gaps.append(
                    PositionFinding(
                        category=FindingCategory.DATA_GAP,
                        title=f"Stale Evidence: {m_def.name}",
                        description=f"Evidence for '{m_def.metric_key}' is stale (as of {latest_obs.as_of_date}).",
                        severity=FindingSeverity.MEDIUM,
                        metric_key=m_def.metric_key,
                        evidence_ids=[latest_obs.id or ""],
                        freshness_status=FreshnessStatus.STALE,
                        quality_tier=latest_obs.quality_tier,
                        confidence_score=latest_obs.confidence_score,
                        rationale="Recency deficiency: observation age exceeds freshness policy threshold.",
                    )
                )

            if latest_obs.quality_tier == QualityTier.PROVISIONAL or latest_obs.confidence_score < 0.70:
                data_gaps.append(
                    PositionFinding(
                        category=FindingCategory.DATA_GAP,
                        title=f"Low Confidence Evidence: {m_def.name}",
                        description=f"Evidence for '{m_def.metric_key}' has quality tier {latest_obs.quality_tier.value} with confidence score {latest_obs.confidence_score:.2f}.",
                        severity=FindingSeverity.LOW,
                        metric_key=m_def.metric_key,
                        evidence_ids=[latest_obs.id or ""],
                        quality_tier=latest_obs.quality_tier,
                        confidence_score=latest_obs.confidence_score,
                        rationale="Verification deficiency: observation requires corroborated verification before strategic reliance.",
                    )
                )

            # Finding Classifications based on Verified/Non-Stale data
            ev_id_list = [latest_obs.id] if latest_obs.id else []

            # 1. Target Gaps
            if assessment.performance_status == PerformanceStatus.BELOW_TARGET and assessment.target_value is not None:
                unit_label = "percentage points" if m_def.default_unit in ("percent", "%") else m_def.default_unit
                gaps.append(
                    PositionFinding(
                        category=FindingCategory.GAP,
                        title=f"{m_def.name} below strategic target",
                        description=(
                            f"Current observation ({assessment.latest_value} {m_def.default_unit}) is "
                            f"{abs(assessment.target_variance or 0)} {unit_label} below target ({assessment.target_value} {m_def.default_unit})."
                        ),
                        severity=FindingSeverity.HIGH if abs(assessment.target_variance or 0) > 5.0 else FindingSeverity.MEDIUM,
                        metric_key=m_def.metric_key,
                        observed_value=assessment.latest_value,
                        comparison_value=assessment.target_value,
                        comparison_type=ComparisonType.PLAN_TARGET,
                        evidence_ids=ev_id_list,
                        confidence_score=assessment.confidence_score,
                        quality_tier=assessment.quality_tier,
                        freshness_status=assessment.freshness_status,
                        rationale="Target gap: current performance does not achieve the measurable institutional objective.",
                    )
                )

            # 2. Strengths
            if assessment.performance_status in (PerformanceStatus.POSITIVE_PERFORMANCE, PerformanceStatus.EXCEEDS_TARGET):
                if assessment.comparison_status == "AVAILABLE" and assessment.previous_value is not None:
                    strengths.append(
                        PositionFinding(
                            category=FindingCategory.STRENGTH,
                            title=f"{m_def.name} improved",
                            description=(
                                f"{m_def.name} improved from {assessment.previous_value} {m_def.default_unit} "
                                f"({assessment.previous_period}) to {assessment.latest_value} {m_def.default_unit} "
                                f"({assessment.latest_period})"
                                + (f" ({assessment.percent_change:+.1f}%)" if assessment.percent_change is not None else "")
                            ),
                            severity=FindingSeverity.HIGH if (assessment.percent_change or 0) >= 10.0 else FindingSeverity.MEDIUM,
                            metric_key=m_def.metric_key,
                            observed_value=assessment.latest_value,
                            comparison_value=assessment.previous_value,
                            comparison_type=ComparisonType.PREVIOUS_PERIOD,
                            evidence_ids=ev_id_list,
                            confidence_score=assessment.confidence_score,
                            quality_tier=assessment.quality_tier,
                            freshness_status=assessment.freshness_status,
                            rationale="Positive performance: significant verified improvement relative to preceding institutional baseline.",
                        )
                    )
                elif assessment.performance_status == PerformanceStatus.EXCEEDS_TARGET and assessment.target_value is not None:
                    strengths.append(
                        PositionFinding(
                            category=FindingCategory.STRENGTH,
                            title=f"{m_def.name} exceeds strategic target",
                            description=f"Current observation ({assessment.latest_value} {m_def.default_unit}) exceeds target ({assessment.target_value} {m_def.default_unit}).",
                            severity=FindingSeverity.HIGH,
                            metric_key=m_def.metric_key,
                            observed_value=assessment.latest_value,
                            comparison_value=assessment.target_value,
                            comparison_type=ComparisonType.PLAN_TARGET,
                            evidence_ids=ev_id_list,
                            confidence_score=assessment.confidence_score,
                            quality_tier=assessment.quality_tier,
                            freshness_status=assessment.freshness_status,
                            rationale="Exceeds target: verified performance surpasses the planned target benchmark.",
                        )
                    )

            # 3. Weaknesses
            if assessment.performance_status == PerformanceStatus.NEGATIVE_PERFORMANCE:
                if assessment.comparison_status == "AVAILABLE" and assessment.previous_value is not None:
                    weaknesses.append(
                        PositionFinding(
                            category=FindingCategory.WEAKNESS,
                            title=f"{m_def.name} declined",
                            description=(
                                f"{m_def.name} dropped from {assessment.previous_value} {m_def.default_unit} "
                                f"({assessment.previous_period}) to {assessment.latest_value} {m_def.default_unit} "
                                f"({assessment.latest_period})"
                                + (f" ({assessment.percent_change:+.1f}%)" if assessment.percent_change is not None else "")
                            ),
                            severity=FindingSeverity.HIGH if abs(assessment.percent_change or 0) >= 10.0 else FindingSeverity.MEDIUM,
                            metric_key=m_def.metric_key,
                            observed_value=assessment.latest_value,
                            comparison_value=assessment.previous_value,
                            comparison_type=ComparisonType.PREVIOUS_PERIOD,
                            evidence_ids=ev_id_list,
                            confidence_score=assessment.confidence_score,
                            quality_tier=assessment.quality_tier,
                            freshness_status=assessment.freshness_status,
                            rationale="Negative performance: significant verified decline relative to preceding institutional baseline.",
                        )
                    )

            # 4. Constraints (persistent capacity limitation or resource bounds supported by evidence)
            if m_def.metric_key.endswith("fill_rate") and assessment.latest_value and assessment.latest_value >= 98.0:
                constraints.append(
                    PositionFinding(
                        category=FindingCategory.CONSTRAINT,
                        title=f"{m_def.name} operating at capacity limit",
                        description=f"Intake fill rate ({assessment.latest_value}%) indicates operational saturation of current seat/facility capacity.",
                        severity=FindingSeverity.MEDIUM,
                        metric_key=m_def.metric_key,
                        observed_value=assessment.latest_value,
                        evidence_ids=ev_id_list,
                        confidence_score=assessment.confidence_score,
                        quality_tier=assessment.quality_tier,
                        freshness_status=assessment.freshness_status,
                        rationale="Capacity constraint: physical and instructional resources are near 100% utilization.",
                    )
                )

            # 5. Opportunities (favorable conditions or significant positive momentum supported by evidence)
            if assessment.performance_status in (PerformanceStatus.POSITIVE_PERFORMANCE, PerformanceStatus.EXCEEDS_TARGET):
                if assessment.percent_change and assessment.percent_change >= 15.0:
                    opportunities.append(
                        PositionFinding(
                            category=FindingCategory.OPPORTUNITY,
                            title=f"High momentum in {m_def.name}",
                            description=f"{m_def.name} grew by {assessment.percent_change:+.1f}% to {assessment.latest_value} {m_def.default_unit}, demonstrating institutional traction.",
                            severity=FindingSeverity.HIGH,
                            metric_key=m_def.metric_key,
                            observed_value=assessment.latest_value,
                            comparison_value=assessment.previous_value,
                            comparison_type=ComparisonType.PREVIOUS_PERIOD,
                            evidence_ids=ev_id_list,
                            confidence_score=assessment.confidence_score,
                            quality_tier=assessment.quality_tier,
                            freshness_status=assessment.freshness_status,
                            rationale="Opportunity: strong performance acceleration establishes positive institutional traction.",
                        )
                    )

        # 6. Structural Risks (compound negative conditions supported by evidence)
        negative_metric_keys = [w.metric_key for w in weaknesses if w.metric_key]
        if len(negative_metric_keys) >= 2:
            neg_names = ", ".join(negative_metric_keys)
            all_neg_ev_ids = [eid for w in weaknesses for eid in w.evidence_ids]
            structural_risks.append(
                PositionFinding(
                    category=FindingCategory.STRUCTURAL_RISK,
                    title="Concurrent multi-metric performance decline",
                    description=f"Multiple institutional indicators exhibit concurrent verified decline: {neg_names}.",
                    severity=FindingSeverity.HIGH,
                    evidence_ids=all_neg_ev_ids,
                    confidence_score=0.9,
                    rationale="Structural risk: simultaneous adverse movements across multiple indicators indicate compound institutional exposure.",
                )
            )

        # 4. Transparent Confidence Calculation
        confidence_assessment = self._calculate_overall_confidence(
            assessments=key_metrics,
            data_gaps_count=len(data_gaps),
        )

        # 5. Explicit Assumptions
        assumptions = [
            "Absence of evidence is an information deficiency, not evidence of poor performance.",
            f"Significant performance change threshold is set to ±{settings.MIN_SIGNIFICANT_CHANGE_PERCENT}%.",
            "Performance evaluations adhere strictly to configured metric polarities (HIGHER_IS_BETTER / LOWER_IS_BETTER).",
            "Tie-breaking for identical period observations prioritizes verified quality tiers, confidence scores, and recency.",
        ]

        # 6. Construct Domain Snapshot Entity
        analysis = CurrentPositionAnalysis(
            institution_id=dto.institution_id,
            organizational_unit_id=dto.organizational_unit_id,
            analysis_period=dto.analysis_period,
            generated_at=datetime.now(timezone.utc),
            key_metrics=key_metrics,
            strengths=strengths,
            weaknesses=weaknesses,
            gaps=gaps,
            constraints=constraints,
            structural_risks=structural_risks,
            opportunities=opportunities,
            data_gaps=data_gaps,
            evidence_references=evidence_refs,
            assumptions=assumptions,
            overall_confidence=confidence_assessment,
            status="FINALIZED",
        )

        # 7. Persist Snapshot (Immutable historical version)
        saved = self.analysis_repo.create_analysis(analysis)
        logger.info(
            f"Generated Current Position Analysis [{saved.id}] for institution '{saved.institution_id}' "
            f"(period: {saved.analysis_period}, confidence: {saved.overall_confidence.level} [{saved.overall_confidence.score}])"
        )

        return self._to_dto(saved)

    def get_analysis_by_id(self, analysis_id: str) -> CurrentPositionAnalysisResponseDTO:
        analysis = self.analysis_repo.get_analysis_by_id(analysis_id)
        if not analysis:
            raise EntityNotFoundException("CurrentPositionAnalysis", analysis_id)
        return self._to_dto(analysis)

    def list_analyses(
        self,
        institution_id: Optional[str] = None,
        organizational_unit_id: Optional[str] = None,
        analysis_period: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> AnalysisListResponseDTO:
        safe_limit = max(1, min(limit, settings.MAX_PAGE_SIZE))
        total = self.analysis_repo.count_analyses(
            institution_id=institution_id,
            organizational_unit_id=organizational_unit_id,
            analysis_period=analysis_period,
        )
        analyses = self.analysis_repo.list_analyses(
            institution_id=institution_id,
            organizational_unit_id=organizational_unit_id,
            analysis_period=analysis_period,
            skip=skip,
            limit=safe_limit,
        )
        return AnalysisListResponseDTO(total=total, items=[self._to_dto(a) for a in analyses])

    def _to_dto(self, model: CurrentPositionAnalysis) -> CurrentPositionAnalysisResponseDTO:
        return CurrentPositionAnalysisResponseDTO(
            id=model.id or "",
            institution_id=model.institution_id,
            organizational_unit_id=model.organizational_unit_id,
            analysis_period=model.analysis_period,
            generated_at=model.generated_at,
            overall_confidence=ConfidenceAssessmentDTO(
                score=model.overall_confidence.score,
                level=model.overall_confidence.level,
                factors=model.overall_confidence.factors,
                explanation=model.overall_confidence.explanation,
            ),
            key_metrics=[
                MetricAssessmentDTO(
                    metric_key=m.metric_key,
                    metric_name=m.metric_name,
                    domain=m.domain,
                    unit=m.unit,
                    direction=m.direction,
                    latest_value=m.latest_value,
                    latest_period=m.latest_period,
                    previous_value=m.previous_value,
                    previous_period=m.previous_period,
                    change_direction=m.change_direction,
                    absolute_change=m.absolute_change,
                    percent_change=m.percent_change,
                    target_value=m.target_value,
                    target_variance=m.target_variance,
                    performance_status=m.performance_status,
                    comparison_status=m.comparison_status,
                    freshness_status=m.freshness_status,
                    quality_tier=m.quality_tier,
                    confidence_score=m.confidence_score,
                    evidence_id=m.evidence_id,
                )
                for m in model.key_metrics
            ],
            strengths=[
                PositionFindingDTO(
                    id=f.id,
                    category=f.category,
                    title=f.title,
                    description=f.description,
                    severity=f.severity,
                    metric_key=f.metric_key,
                    observed_value=f.observed_value,
                    comparison_value=f.comparison_value,
                    comparison_type=f.comparison_type,
                    evidence_ids=f.evidence_ids,
                    confidence_score=f.confidence_score,
                    quality_tier=f.quality_tier,
                    freshness_status=f.freshness_status,
                    rationale=f.rationale,
                )
                for f in model.strengths
            ],
            weaknesses=[
                PositionFindingDTO(
                    id=f.id,
                    category=f.category,
                    title=f.title,
                    description=f.description,
                    severity=f.severity,
                    metric_key=f.metric_key,
                    observed_value=f.observed_value,
                    comparison_value=f.comparison_value,
                    comparison_type=f.comparison_type,
                    evidence_ids=f.evidence_ids,
                    confidence_score=f.confidence_score,
                    quality_tier=f.quality_tier,
                    freshness_status=f.freshness_status,
                    rationale=f.rationale,
                )
                for f in model.weaknesses
            ],
            gaps=[
                PositionFindingDTO(
                    id=f.id,
                    category=f.category,
                    title=f.title,
                    description=f.description,
                    severity=f.severity,
                    metric_key=f.metric_key,
                    observed_value=f.observed_value,
                    comparison_value=f.comparison_value,
                    comparison_type=f.comparison_type,
                    evidence_ids=f.evidence_ids,
                    confidence_score=f.confidence_score,
                    quality_tier=f.quality_tier,
                    freshness_status=f.freshness_status,
                    rationale=f.rationale,
                )
                for f in model.gaps
            ],
            constraints=[
                PositionFindingDTO(
                    id=f.id,
                    category=f.category,
                    title=f.title,
                    description=f.description,
                    severity=f.severity,
                    metric_key=f.metric_key,
                    observed_value=f.observed_value,
                    comparison_value=f.comparison_value,
                    comparison_type=f.comparison_type,
                    evidence_ids=f.evidence_ids,
                    confidence_score=f.confidence_score,
                    quality_tier=f.quality_tier,
                    freshness_status=f.freshness_status,
                    rationale=f.rationale,
                )
                for f in model.constraints
            ],
            structural_risks=[
                PositionFindingDTO(
                    id=f.id,
                    category=f.category,
                    title=f.title,
                    description=f.description,
                    severity=f.severity,
                    metric_key=f.metric_key,
                    observed_value=f.observed_value,
                    comparison_value=f.comparison_value,
                    comparison_type=f.comparison_type,
                    evidence_ids=f.evidence_ids,
                    confidence_score=f.confidence_score,
                    quality_tier=f.quality_tier,
                    freshness_status=f.freshness_status,
                    rationale=f.rationale,
                )
                for f in model.structural_risks
            ],
            opportunities=[
                PositionFindingDTO(
                    id=f.id,
                    category=f.category,
                    title=f.title,
                    description=f.description,
                    severity=f.severity,
                    metric_key=f.metric_key,
                    observed_value=f.observed_value,
                    comparison_value=f.comparison_value,
                    comparison_type=f.comparison_type,
                    evidence_ids=f.evidence_ids,
                    confidence_score=f.confidence_score,
                    quality_tier=f.quality_tier,
                    freshness_status=f.freshness_status,
                    rationale=f.rationale,
                )
                for f in model.opportunities
            ],
            data_gaps=[
                PositionFindingDTO(
                    id=f.id,
                    category=f.category,
                    title=f.title,
                    description=f.description,
                    severity=f.severity,
                    metric_key=f.metric_key,
                    observed_value=f.observed_value,
                    comparison_value=f.comparison_value,
                    comparison_type=f.comparison_type,
                    evidence_ids=f.evidence_ids,
                    confidence_score=f.confidence_score,
                    quality_tier=f.quality_tier,
                    freshness_status=f.freshness_status,
                    rationale=f.rationale,
                )
                for f in model.data_gaps
            ],
            evidence_references=[
                EvidenceReferenceDTO(
                    evidence_id=r.evidence_id,
                    metric_key=r.metric_key,
                    period=r.period,
                    as_of_date=r.as_of_date,
                    source_name=r.source_name,
                    source_type=r.source_type,
                    confidence_score=r.confidence_score,
                    quality_tier=r.quality_tier,
                    freshness_status=r.freshness_status,
                )
                for r in model.evidence_references
            ],
            assumptions=model.assumptions,
            status=model.status,
        )
