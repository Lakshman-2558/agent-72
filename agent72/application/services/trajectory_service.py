"""
Deterministic Institutional Trajectory Analysis Service (Phase 5).

Evaluates chronological multi-period evidence series, computes magnitude of change,
consistency, volatility, acceleration, and polarity-aware trend statuses, and connects
trajectory findings to current institutional position snapshots.
"""

import math
from datetime import datetime, timezone
import logging
from typing import Any, Dict, List, Optional, Tuple

from agent72.application.dtos.analysis_dto import ConfidenceAssessmentDTO
from agent72.application.dtos.trajectory_dto import (
    PeriodObservationDTO,
    TrajectoryAnalysisListResponseDTO,
    TrajectoryAnalysisRequestDTO,
    TrajectoryAnalysisResponseDTO,
    TrajectoryDataLimitationDTO,
    TrajectoryEvidenceReferenceDTO,
    TrajectoryMetricDTO,
    TrajectorySignalDTO,
)
from agent72.core.config import settings
from agent72.core.exceptions import EntityNotFoundException, ValidationError
from agent72.domain.interfaces.analysis_repository import IAnalysisRepository
from agent72.domain.interfaces.evidence_repository import IEvidenceRepository
from agent72.domain.interfaces.organization_repository import IOrganizationRepository
from agent72.domain.interfaces.trajectory_repository import ITrajectoryRepository
from agent72.domain.models.analysis import (
    ConfidenceAssessment,
    CurrentPositionAnalysis,
    FindingCategory,
    PerformanceStatus,
)
from agent72.domain.models.evidence import (
    FreshnessStatus,
    InstitutionalEvidence,
    MetricDefinition,
    MetricDirection,
    QualityTier,
    SourceType,
)
from agent72.domain.models.trajectory import (
    AccelerationStatus,
    ConsistencyRating,
    PeriodObservation,
    TrajectoryAnalysis,
    TrajectoryDataLimitation,
    TrajectoryEvidenceReference,
    TrajectoryMetric,
    TrajectorySignal,
    TrajectoryStatus,
    VolatilityRating,
)

logger = logging.getLogger(__name__)

QUALITY_TIER_WEIGHTS = {
    QualityTier.VERIFIED: 3,
    QualityTier.ESTIMATED: 2,
    QualityTier.PROVISIONAL: 1,
}


class TrajectoryAnalysisService:
    """
    Deterministic Trajectory Analysis Service.

    Extends Agent 72 from 'Where are we now?' to 'Where are we heading?'.
    Never uses an LLM for numerical trajectory calculations.
    """

    def __init__(
        self,
        trajectory_repository: ITrajectoryRepository,
        evidence_repository: IEvidenceRepository,
        organization_repository: IOrganizationRepository,
        analysis_repository: Optional[IAnalysisRepository] = None,
    ):
        self.traj_repo = trajectory_repository
        self.evidence_repo = evidence_repository
        self.org_repo = organization_repository
        self.analysis_repo = analysis_repository

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

    def _calculate_volatility(self, period_changes: List[float]) -> Tuple[Optional[str], Optional[float]]:
        """
        Calculates transparent volatility (sample standard deviation of period-to-period changes).
        Requires at least 2 period-to-period changes (i.e., 3 observations).
        Returns (rating, score).
        """
        if len(period_changes) < 2:
            return (None, None)

        n = len(period_changes)
        mean_val = sum(period_changes) / n
        variance = sum((x - mean_val) ** 2 for x in period_changes) / (n - 1)
        std_dev = round(math.sqrt(variance), 4)

        if std_dev < 5.0:
            rating = VolatilityRating.LOW.value
        elif std_dev < 15.0:
            rating = VolatilityRating.MEDIUM.value
        else:
            rating = VolatilityRating.HIGH.value

        return (rating, std_dev)

    def _evaluate_consistency(self, period_changes: List[float]) -> ConsistencyRating:
        """
        Evaluates sign consistency across period-to-period changes:
        - HIGH: all non-zero changes in the same direction
        - MODERATE: >= 70% of non-zero changes in the same direction
        - LOW: alternating or evenly mixed directions
        """
        if len(period_changes) < 2:
            return ConsistencyRating.INSUFFICIENT_DATA

        pos = sum(1 for c in period_changes if c > 0)
        neg = sum(1 for c in period_changes if c < 0)
        non_zero = pos + neg

        if non_zero == 0:
            return ConsistencyRating.HIGH  # completely flat/stable

        max_dir = max(pos, neg)
        ratio = max_dir / non_zero

        if ratio == 1.0:
            return ConsistencyRating.HIGH
        elif ratio >= 0.70:
            return ConsistencyRating.MODERATE
        else:
            return ConsistencyRating.LOW

    def _evaluate_acceleration(
        self,
        observations: List[PeriodObservation],
        direction: MetricDirection,
    ) -> AccelerationStatus:
        """
        Evaluates second-order change (rate of change across consecutive periods).
        Requires at least 3 chronological observations (v0, v1, v2).
        """
        if len(observations) < 3:
            return AccelerationStatus.INSUFFICIENT_DATA

        # Take last two period changes
        v_last = observations[-1].numeric_value
        v_mid = observations[-2].numeric_value
        v_prev = observations[-3].numeric_value

        delta_recent = v_last - v_mid
        delta_prior = v_mid - v_prev

        # Direction-adjusted velocity: positive value means movement in desirable direction
        if direction == MetricDirection.HIGHER_IS_BETTER:
            u_recent = delta_recent
            u_prior = delta_prior
        elif direction == MetricDirection.LOWER_IS_BETTER:
            u_recent = -delta_recent
            u_prior = -delta_prior
        else:
            # For NEUTRAL, evaluate magnitude of absolute momentum
            u_recent = abs(delta_recent)
            u_prior = abs(delta_prior)

        diff = round(u_recent - u_prior, 4)
        # 5% tolerance buffer for constant velocity
        tolerance = 0.05 * max(abs(u_prior), abs(u_recent), 1.0)

        if abs(diff) <= tolerance:
            return AccelerationStatus.CONSTANT_VELOCITY
        elif diff > 0:
            return AccelerationStatus.ACCELERATING
        else:
            return AccelerationStatus.DECELERATING

    def _evaluate_trend_status(
        self,
        earliest_val: float,
        latest_val: float,
        direction: MetricDirection,
        pct_change: float,
        min_change_threshold: float,
        consistency: ConsistencyRating,
        volatility_score: Optional[float],
        obs_count: int,
    ) -> TrajectoryStatus:
        """
        Deterministic trend classification respecting metric polarity,
        significance threshold, consistency, and volatility.
        """
        if obs_count < 2:
            return TrajectoryStatus.INSUFFICIENT_DATA

        # High volatility with alternating direction
        if obs_count >= 3 and consistency == ConsistencyRating.LOW and volatility_score is not None and volatility_score > 15.0:
            return TrajectoryStatus.VOLATILE

        # Small changes within threshold -> STABLE
        if abs(pct_change) < min_change_threshold:
            return TrajectoryStatus.STABLE

        # Meaningful directional change evaluated against polarity
        abs_change = latest_val - earliest_val
        if direction == MetricDirection.HIGHER_IS_BETTER:
            return TrajectoryStatus.IMPROVING if abs_change > 0 else TrajectoryStatus.DECLINING
        elif direction == MetricDirection.LOWER_IS_BETTER:
            return TrajectoryStatus.IMPROVING if abs_change < 0 else TrajectoryStatus.DECLINING
        else:
            # NEUTRAL: cannot be classified as good or bad
            return TrajectoryStatus.STABLE

    def _calculate_overall_confidence(
        self,
        metrics: List[TrajectoryMetric],
        limitations_count: int,
    ) -> ConfidenceAssessment:
        """Calculates transparent, factor-based overall confidence for trajectory analysis."""
        if not metrics:
            return ConfidenceAssessment(
                score=0.1,
                level="LOW",
                factors={"evaluated_metrics": 0, "limitations_count": limitations_count},
                explanation="No metrics evaluated for trajectory analysis.",
            )

        evaluated_with_trend = [m for m in metrics if m.trend_status != TrajectoryStatus.INSUFFICIENT_DATA]
        total_metrics = len(metrics)

        # Depth ratio (how close average observation count is to 3+ periods)
        all_obs = [o for m in metrics for o in m.observations]
        total_obs_count = len(all_obs)
        avg_obs = (total_obs_count / total_metrics) if total_metrics else 0.0
        depth_score = min(1.0, avg_obs / 3.0)

        # Evidence confidence
        all_ev_confs = [o.confidence_score for o in all_obs if o.confidence_score > 0]
        avg_ev_conf = (sum(all_ev_confs) / len(all_ev_confs)) if all_ev_confs else 0.5

        # Freshness penalty: proportion of stale observations
        stale_count = sum(1 for o in all_obs if o.is_stale)
        stale_ratio = (stale_count / total_obs_count) if total_obs_count else 0.0
        freshness_penalty = round(stale_ratio * 0.15, 2)

        # Quality tier weighting: proportion of verified observations
        verified_count = sum(1 for o in all_obs if o.quality_tier == QualityTier.VERIFIED)
        verified_ratio = (verified_count / total_obs_count) if total_obs_count else 0.0

        # Consistency ratio (metrics with HIGH or MODERATE consistency)
        consistent_metrics = [
            m for m in evaluated_with_trend if m.consistency in (ConsistencyRating.HIGH, ConsistencyRating.MODERATE)
        ]
        consistency_ratio = (len(consistent_metrics) / len(evaluated_with_trend)) if evaluated_with_trend else 0.0

        # Limitation penalty
        limitation_penalty = min(0.30, limitations_count * 0.05)

        raw_score = (
            (depth_score * 0.30)
            + (avg_ev_conf * 0.30)
            + (verified_ratio * 0.15)
            + (consistency_ratio * 0.25)
            - limitation_penalty
            - freshness_penalty
        )
        score = max(0.1, min(1.0, round(raw_score, 2)))
        level = "HIGH" if score >= 0.80 else ("MEDIUM" if score >= 0.50 else "LOW")

        factors = {
            "total_metrics_evaluated": total_metrics,
            "metrics_with_sufficient_history": len(evaluated_with_trend),
            "total_observations_count": total_obs_count,
            "average_observation_depth": round(avg_obs, 2),
            "depth_score": round(depth_score, 2),
            "average_evidence_confidence": round(avg_ev_conf, 2),
            "verified_tier_ratio": round(verified_ratio, 2),
            "stale_observations_count": stale_count,
            "freshness_penalty": freshness_penalty,
            "consistency_ratio": round(consistency_ratio, 2),
            "data_limitations_count": limitations_count,
            "data_limitation_penalty": round(limitation_penalty, 2),
        }

        explanation = (
            f"Confidence is {level} ({score*100:.0f}%). "
            f"Based on {len(evaluated_with_trend)}/{total_metrics} metrics with sufficient historical depth "
            f"(avg {avg_obs:.1f} periods), {avg_ev_conf*100:.0f}% average evidence confidence, "
            f"{verified_ratio*100:.0f}% verified observations, {stale_count} stale observations, "
            f"and {limitations_count} isolated data limitations."
        )

        return ConfidenceAssessment(score=score, level=level, factors=factors, explanation=explanation)

    def _synthesize_trajectory_signals(
        self,
        current_position: Optional[CurrentPositionAnalysis],
        trajectory_metrics: List[TrajectoryMetric],
    ) -> List[TrajectorySignal]:
        """
        Connects relevant trajectory metrics to current institutional findings.
        Creates structured signals, NOT strategic recommendations.
        """
        signals: List[TrajectorySignal] = []
        if not current_position:
            return signals

        # Map current position assessments by metric_key
        curr_map = {m.metric_key: m for m in current_position.key_metrics}
        gaps_keys = {g.metric_key for g in current_position.gaps if g.metric_key}
        strengths_keys = {s.metric_key for s in current_position.strengths if s.metric_key}
        weaknesses_keys = {w.metric_key for w in current_position.weaknesses if w.metric_key}

        for t_metric in trajectory_metrics:
            key = t_metric.metric_key
            if key not in curr_map:
                continue

            c_assessment = curr_map[key]
            trend = t_metric.trend_status

            if trend == TrajectoryStatus.INSUFFICIENT_DATA:
                continue

            # 1. Target Gap or Below Target + Trajectory
            if key in gaps_keys or c_assessment.performance_status == PerformanceStatus.BELOW_TARGET:
                if trend == TrajectoryStatus.IMPROVING:
                    signals.append(
                        TrajectorySignal(
                            metric_key=key,
                            signal_type="GAP_IMPROVING",
                            status="BELOW_TARGET_IMPROVING",
                            interpretation="Performance is improving but remains below the current target.",
                            title=f"{t_metric.metric_name}: Improving but below target",
                            description=(
                                f"Current performance ({t_metric.latest_value}) remains below strategic target "
                                f"({c_assessment.target_value}), but historical trajectory is IMPROVING "
                                f"({t_metric.percentage_change:+.1f}% from {t_metric.earliest_period} to {t_metric.latest_period})."
                            ),
                            severity="MEDIUM",
                            rationale="Positive directional momentum is narrowing the strategic target deficit.",
                        )
                    )
                elif trend == TrajectoryStatus.DECLINING:
                    signals.append(
                        TrajectorySignal(
                            metric_key=key,
                            signal_type="GAP_DECLINING",
                            status="BELOW_TARGET_DECLINING",
                            interpretation="Performance is declining and remains below the current target.",
                            title=f"{t_metric.metric_name}: Declining and below target",
                            description=(
                                f"Current performance ({t_metric.latest_value}) is below strategic target "
                                f"({c_assessment.target_value}) and continues on a DECLINING trajectory "
                                f"({t_metric.percentage_change:+.1f}%)."
                            ),
                            severity="HIGH",
                            rationale="Adverse directional momentum is compounding the strategic performance deficit.",
                        )
                    )
                elif trend == TrajectoryStatus.STABLE:
                    signals.append(
                        TrajectorySignal(
                            metric_key=key,
                            signal_type="GAP_STABLE",
                            status="BELOW_TARGET_STABLE",
                            interpretation="Performance remains below target with a stable trajectory.",
                            title=f"{t_metric.metric_name}: Stable below target",
                            description=(
                                f"Current performance ({t_metric.latest_value}) is below strategic target "
                                f"({c_assessment.target_value}) with negligible historical movement."
                            ),
                            severity="MEDIUM",
                            rationale="Stagnant trajectory indicates the gap is neither widening nor closing.",
                        )
                    )

            # 2. Current Strength or Exceeds Target + Trajectory
            elif key in strengths_keys or c_assessment.performance_status in (
                PerformanceStatus.POSITIVE_PERFORMANCE,
                PerformanceStatus.EXCEEDS_TARGET,
            ):
                if trend == TrajectoryStatus.IMPROVING:
                    signals.append(
                        TrajectorySignal(
                            metric_key=key,
                            signal_type="STRENGTH_COMPOUNDING",
                            status="ABOVE_TARGET_IMPROVING",
                            interpretation="Performance is above target and continues on an improving trajectory.",
                            title=f"{t_metric.metric_name}: Compounding strength",
                            description=(
                                f"Current performance is an institutional strength and exhibits a sustained "
                                f"IMPROVING trajectory ({t_metric.percentage_change:+.1f}% over {len(t_metric.observations)} periods)."
                            ),
                            severity="LOW",
                            rationale="Multi-period positive momentum solidifies institutional leadership in this domain.",
                        )
                    )
                elif trend == TrajectoryStatus.DECLINING:
                    signals.append(
                        TrajectorySignal(
                            metric_key=key,
                            signal_type="STRENGTH_VULNERABLE",
                            status="ABOVE_TARGET_DECLINING",
                            interpretation="Performance currently exceeds target/baseline but historical trajectory is declining.",
                            title=f"{t_metric.metric_name}: Vulnerable strength",
                            description=(
                                f"Current performance represents an institutional baseline strength, but historical "
                                f"trajectory reveals a DECLINING trend ({t_metric.percentage_change:+.1f}%)."
                            ),
                            severity="HIGH",
                            rationale="Negative trajectory threatens to erode an established institutional advantage.",
                        )
                    )
                elif trend == TrajectoryStatus.STABLE:
                    signals.append(
                        TrajectorySignal(
                            metric_key=key,
                            signal_type="STRENGTH_STABLE",
                            status="ABOVE_TARGET_STABLE",
                            interpretation="Performance is above target with a stable trajectory.",
                            title=f"{t_metric.metric_name}: Stable strength",
                            description=(
                                f"Current performance exceeds baseline/target and trajectory remains stable."
                            ),
                            severity="LOW",
                            rationale="Established performance advantage remains consistent over time.",
                        )
                    )

            # 3. Current Weakness + Trajectory
            elif key in weaknesses_keys or c_assessment.performance_status == PerformanceStatus.NEGATIVE_PERFORMANCE:
                if trend == TrajectoryStatus.IMPROVING:
                    signals.append(
                        TrajectorySignal(
                            metric_key=key,
                            signal_type="WEAKNESS_RECOVERING",
                            status="BELOW_TARGET_IMPROVING",
                            interpretation="Performance is below baseline but exhibits positive directional turnaround.",
                            title=f"{t_metric.metric_name}: Recovering from weakness",
                            description=(
                                f"Current performance is classified as a weakness, but trajectory reflects positive "
                                f"directional turnaround ({t_metric.percentage_change:+.1f}%)."
                            ),
                            severity="MEDIUM",
                            rationale="Early recovery momentum is evident despite low current performance baseline.",
                        )
                    )
                elif trend == TrajectoryStatus.DECLINING:
                    signals.append(
                        TrajectorySignal(
                            metric_key=key,
                            signal_type="WEAKNESS_PERSISTENT",
                            status="BELOW_TARGET_DECLINING",
                            interpretation="Performance is below baseline and continues on a declining trajectory.",
                            title=f"{t_metric.metric_name}: Persistent negative trajectory",
                            description=(
                                f"Current performance weakness is coupled with an ongoing DECLINING trajectory "
                                f"({t_metric.percentage_change:+.1f}%)."
                            ),
                            severity="HIGH",
                            rationale="Unarrested downward trajectory indicates entrenched performance erosion.",
                        )
                    )

            # 4. Meets Target + Trajectory
            elif c_assessment.performance_status == PerformanceStatus.MEETS_TARGET:
                if trend == TrajectoryStatus.STABLE:
                    signals.append(
                        TrajectorySignal(
                            metric_key=key,
                            signal_type="ON_TARGET_STABLE",
                            status="ON_TARGET_STABLE",
                            interpretation="Performance is on target with a stable trajectory.",
                            title=f"{t_metric.metric_name}: On target and stable",
                            description=(
                                f"Current performance meets the strategic target with consistent, stable historical performance."
                            ),
                            severity="LOW",
                            rationale="Historical trajectory matches established target expectations without significant drift.",
                        )
                    )
                elif trend == TrajectoryStatus.IMPROVING:
                    signals.append(
                        TrajectorySignal(
                            metric_key=key,
                            signal_type="ON_TARGET_IMPROVING",
                            status="ON_TARGET_IMPROVING",
                            interpretation="Performance is on target and continues on an improving trajectory.",
                            title=f"{t_metric.metric_name}: On target with positive momentum",
                            description=(
                                f"Current performance meets the strategic target and exhibits positive momentum ({t_metric.percentage_change:+.1f}%)."
                            ),
                            severity="LOW",
                            rationale="Positive trajectory is positioning the metric to exceed target parameters.",
                        )
                    )
                elif trend == TrajectoryStatus.DECLINING:
                    signals.append(
                        TrajectorySignal(
                            metric_key=key,
                            signal_type="ON_TARGET_DECLINING",
                            status="ON_TARGET_DECLINING",
                            interpretation="Performance is on target but exhibits a declining trajectory.",
                            title=f"{t_metric.metric_name}: On target but declining",
                            description=(
                                f"Current performance currently meets the target but historical trajectory shows decline ({t_metric.percentage_change:+.1f}%)."
                            ),
                            severity="MEDIUM",
                            rationale="Negative trajectory risks pulling performance below target in upcoming periods.",
                        )
                    )

        return signals

    def generate_trajectory_analysis(
        self, dto: TrajectoryAnalysisRequestDTO
    ) -> TrajectoryAnalysisResponseDTO:
        """
        Executes deterministic institutional trajectory analysis.
        Isolates insufficient historical data, computes multi-period direction,
        consistency, volatility, and acceleration, synthesizes signals with current position,
        and saves an immutable analysis snapshot.
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

        # 3. Retrieve optional Current Position Analysis snapshot
        current_pos: Optional[CurrentPositionAnalysis] = None
        if dto.current_position_analysis_id and self.analysis_repo:
            current_pos = self.analysis_repo.get_analysis_by_id(dto.current_position_analysis_id)
        elif self.analysis_repo:
            # Check if an analysis exists for this institution and analysis_period
            recent_pos = self.analysis_repo.list_analyses(
                institution_id=dto.institution_id,
                organizational_unit_id=dto.organizational_unit_id,
                analysis_period=dto.analysis_period,
                limit=1,
            )
            if recent_pos:
                current_pos = recent_pos[0]

        threshold = dto.min_significant_change_percent or settings.MIN_SIGNIFICANT_CHANGE_PERCENT

        # 4. Batch query historical evidence observations (Section 16: Performance)
        all_evidence = self.evidence_repo.query_evidence(
            institution_id=dto.institution_id,
            unit_id=dto.organizational_unit_id,
            limit=10000,
        )
        evidence_by_metric: Dict[str, List[InstitutionalEvidence]] = {}
        for ev in all_evidence:
            evidence_by_metric.setdefault(ev.metric_key, []).append(ev)

        # 5. Evaluate each metric's historical observations
        metric_trends: List[TrajectoryMetric] = []
        data_limitations: List[TrajectoryDataLimitation] = []
        evidence_refs: List[TrajectoryEvidenceReference] = []
        seen_evidence_ids = set()

        for m_def in metric_defs:
            raw_series = evidence_by_metric.get(m_def.metric_key, [])

            # Filter series strictly up to target analysis_period
            series = [ev for ev in raw_series if ev.period <= dto.analysis_period and ev.numeric_value is not None]

            # Group by period and resolve ties per period
            by_period: Dict[str, List[InstitutionalEvidence]] = {}
            for ev in series:
                by_period.setdefault(ev.period, []).append(ev)

            # Deterministic best observation per period
            period_winners: Dict[str, InstitutionalEvidence] = {
                p: self._select_best_observation_for_period(evs)
                for p, evs in by_period.items()
            }

            sorted_periods = sorted(period_winners.keys())
            obs_list: List[PeriodObservation] = []
            ev_ids: List[str] = []

            for p in sorted_periods:
                ev = period_winners[p]
                if ev.id:
                    ev_ids.append(ev.id)
                    if ev.id not in seen_evidence_ids:
                        seen_evidence_ids.add(ev.id)
                        evidence_refs.append(
                            TrajectoryEvidenceReference(
                                evidence_id=ev.id,
                                metric_key=ev.metric_key,
                                period=ev.period,
                                as_of_date=ev.as_of_date,
                                source_name=ev.source_name,
                                source_type=ev.source_type,
                                confidence_score=ev.confidence_score,
                                quality_tier=ev.quality_tier,
                                freshness_status=FreshnessStatus.STALE if ev.is_stale else FreshnessStatus.FRESH,
                            )
                        )

                obs_list.append(
                    PeriodObservation(
                        period=p,
                        numeric_value=ev.numeric_value,
                        evidence_id=ev.id,
                        as_of_date=ev.as_of_date,
                        quality_tier=ev.quality_tier,
                        confidence_score=ev.confidence_score,
                        is_stale=ev.is_stale,
                    )
                )

            obs_count = len(obs_list)

            # 0 observations -> isolated data limitation
            if obs_count == 0:
                data_limitations.append(
                    TrajectoryDataLimitation(
                        metric_key=m_def.metric_key,
                        limitation_type="INSUFFICIENT_HISTORICAL_DATA",
                        description=f"No historical evidence observations found for '{m_def.metric_key}'.",
                        observation_count=0,
                        rationale="Information deficiency: cannot infer trajectory without historical observations.",
                    )
                )
                metric_trends.append(
                    TrajectoryMetric(
                        metric_key=m_def.metric_key,
                        metric_name=m_def.name,
                        domain=m_def.domain,
                        unit=m_def.default_unit,
                        direction=m_def.direction,
                        observations=[],
                        latest_value=None,
                        earliest_value=None,
                        latest_period=None,
                        earliest_period=None,
                        absolute_change=None,
                        percentage_change=None,
                        change_direction=None,
                        trend_status=TrajectoryStatus.INSUFFICIENT_DATA,
                        consistency=ConsistencyRating.INSUFFICIENT_DATA,
                        volatility=None,
                        volatility_score=None,
                        acceleration=AccelerationStatus.INSUFFICIENT_DATA,
                        confidence_score=0.0,
                        evidence_ids=[],
                    )
                )
                continue

            # 1 observation -> single observation data limitation
            if obs_count == 1:
                single_obs = obs_list[0]
                data_limitations.append(
                    TrajectoryDataLimitation(
                        metric_key=m_def.metric_key,
                        limitation_type="SINGLE_OBSERVATION",
                        description=(
                            f"Only 1 observation available for '{m_def.metric_key}' ({single_obs.period}: {single_obs.numeric_value}). "
                            "A single observation does not constitute a trend."
                        ),
                        observation_count=1,
                        rationale="Depth deficiency: at least 2 chronological observations required to establish directional movement.",
                    )
                )
                metric_trends.append(
                    TrajectoryMetric(
                        metric_key=m_def.metric_key,
                        metric_name=m_def.name,
                        domain=m_def.domain,
                        unit=m_def.default_unit,
                        direction=m_def.direction,
                        observations=obs_list,
                        latest_value=single_obs.numeric_value,
                        earliest_value=single_obs.numeric_value,
                        latest_period=single_obs.period,
                        earliest_period=single_obs.period,
                        absolute_change=None,
                        percentage_change=None,
                        change_direction=None,
                        trend_status=TrajectoryStatus.INSUFFICIENT_DATA,
                        consistency=ConsistencyRating.INSUFFICIENT_DATA,
                        volatility=None,
                        volatility_score=None,
                        acceleration=AccelerationStatus.INSUFFICIENT_DATA,
                        confidence_score=single_obs.confidence_score,
                        evidence_ids=ev_ids,
                    )
                )
                continue

            # 2+ observations -> Calculate trajectory
            earliest_obs = obs_list[0]
            latest_obs = obs_list[-1]

            earliest_val = earliest_obs.numeric_value
            latest_val = latest_obs.numeric_value

            abs_change = round(latest_val - earliest_val, 4)
            pct_change = round(((latest_val - earliest_val) / abs(earliest_val)) * 100.0, 2) if earliest_val != 0 else 0.0

            # Change direction indicator
            if abs_change > 0:
                change_dir = "↑"
            elif abs_change < 0:
                change_dir = "↓"
            else:
                change_dir = "→"

            # Period-to-period deltas
            period_deltas = [
                round(obs_list[i].numeric_value - obs_list[i - 1].numeric_value, 4)
                for i in range(1, obs_count)
            ]

            # Consistency analysis (requires 3+ periods, else INSUFFICIENT_DATA)
            consistency = self._evaluate_consistency(period_deltas)

            # Volatility (sample std dev and rating, requires 3+ periods)
            volatility_rating, volatility_score = self._calculate_volatility(period_deltas)

            # Acceleration (second-order change, requires 3+ periods)
            acceleration = self._evaluate_acceleration(obs_list, m_def.direction)

            # Trend Status
            trend_status = self._evaluate_trend_status(
                earliest_val=earliest_val,
                latest_val=latest_val,
                direction=m_def.direction,
                pct_change=pct_change,
                min_change_threshold=threshold,
                consistency=consistency,
                volatility_score=volatility_score,
                obs_count=obs_count,
            )

            # Average confidence of underlying observations
            metric_conf = round(sum(o.confidence_score for o in obs_list) / obs_count, 2)

            metric_trends.append(
                TrajectoryMetric(
                    metric_key=m_def.metric_key,
                    metric_name=m_def.name,
                    domain=m_def.domain,
                    unit=m_def.default_unit,
                    direction=m_def.direction,
                    observations=obs_list,
                    latest_value=latest_val,
                    earliest_value=earliest_val,
                    latest_period=latest_obs.period,
                    earliest_period=earliest_obs.period,
                    absolute_change=abs_change,
                    percentage_change=pct_change,
                    change_direction=change_dir,
                    trend_status=trend_status,
                    consistency=consistency,
                    volatility=volatility_rating,
                    volatility_score=volatility_score,
                    acceleration=acceleration,
                    confidence_score=metric_conf,
                    evidence_ids=ev_ids,
                )
            )

        # 6. Connect to Current Position Findings (Trajectory Signals)
        trajectory_signals = self._synthesize_trajectory_signals(
            current_position=current_pos,
            trajectory_metrics=metric_trends,
        )

        # 7. Overall Transparent Confidence
        confidence_assessment = self._calculate_overall_confidence(
            metrics=metric_trends,
            limitations_count=len(data_limitations),
        )

        # 8. Explicit Assumptions
        assumptions = [
            "Trajectory analysis reflects historical observation series and does not infer causal relationships or future guarantees.",
            f"Significant trajectory change threshold is configured to ±{threshold}%.",
            "Metrics with fewer than 2 historical observations are isolated as data limitations and never classified as trends or performance deficits.",
            "Trend statuses strictly adhere to configured metric polarities (HIGHER_IS_BETTER / LOWER_IS_BETTER / NEUTRAL).",
            "Acceleration status requires a minimum of 3 chronological periods and evaluates second-order rate of change.",
        ]

        # 9. Construct Domain Entity
        analysis = TrajectoryAnalysis(
            institution_id=dto.institution_id,
            organizational_unit_id=dto.organizational_unit_id,
            analysis_period=dto.analysis_period,
            generated_at=datetime.now(timezone.utc),
            metric_trends=metric_trends,
            trajectory_signals=trajectory_signals,
            data_limitations=data_limitations,
            evidence_references=evidence_refs,
            assumptions=assumptions,
            overall_confidence=confidence_assessment,
            status="FINALIZED",
        )

        # 10. Persist Immutable Snapshot
        saved = self.traj_repo.create_trajectory_analysis(analysis)
        logger.info(
            f"Generated Institutional Trajectory Analysis [{saved.id}] for institution '{saved.institution_id}' "
            f"(period: {saved.analysis_period}, confidence: {saved.overall_confidence.level} [{saved.overall_confidence.score}])"
        )

        return self._to_dto(saved)

    def get_trajectory_analysis_by_id(self, analysis_id: str) -> TrajectoryAnalysisResponseDTO:
        analysis = self.traj_repo.get_trajectory_analysis_by_id(analysis_id)
        if not analysis:
            raise EntityNotFoundException("TrajectoryAnalysis", analysis_id)
        return self._to_dto(analysis)

    def list_trajectory_analyses(
        self,
        institution_id: Optional[str] = None,
        organizational_unit_id: Optional[str] = None,
        analysis_period: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> TrajectoryAnalysisListResponseDTO:
        safe_limit = max(1, min(limit, settings.MAX_PAGE_SIZE))
        total = self.traj_repo.count_trajectory_analyses(
            institution_id=institution_id,
            organizational_unit_id=organizational_unit_id,
            analysis_period=analysis_period,
        )
        items = self.traj_repo.list_trajectory_analyses(
            institution_id=institution_id,
            organizational_unit_id=organizational_unit_id,
            analysis_period=analysis_period,
            skip=skip,
            limit=safe_limit,
        )
        return TrajectoryAnalysisListResponseDTO(total=total, items=[self._to_dto(a) for a in items])

    def _to_dto(self, model: TrajectoryAnalysis) -> TrajectoryAnalysisResponseDTO:
        return TrajectoryAnalysisResponseDTO(
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
            metric_trends=[
                TrajectoryMetricDTO(
                    metric_key=m.metric_key,
                    metric_name=m.metric_name,
                    domain=m.domain,
                    unit=m.unit,
                    direction=m.direction,
                    observations=[
                        PeriodObservationDTO(
                            period=o.period,
                            numeric_value=o.numeric_value,
                            evidence_id=o.evidence_id,
                            as_of_date=o.as_of_date,
                            quality_tier=o.quality_tier,
                            confidence_score=o.confidence_score,
                            is_stale=o.is_stale,
                        )
                        for o in m.observations
                    ],
                    latest_value=m.latest_value,
                    earliest_value=m.earliest_value,
                    latest_period=m.latest_period,
                    earliest_period=m.earliest_period,
                    absolute_change=m.absolute_change,
                    percentage_change=m.percentage_change,
                    change_direction=m.change_direction,
                    trend_status=m.trend_status,
                    consistency=m.consistency,
                    volatility=m.volatility,
                    volatility_score=m.volatility_score,
                    acceleration=m.acceleration,
                    confidence_score=m.confidence_score,
                    confidence=m.confidence_score,
                    evidence_ids=m.evidence_ids,
                )
                for m in model.metric_trends
            ],
            trajectory_signals=[
                TrajectorySignalDTO(
                    metric_key=s.metric_key,
                    signal_type=s.signal_type,
                    status=s.status,
                    interpretation=s.interpretation,
                    title=s.title,
                    description=s.description,
                    severity=s.severity,
                    rationale=s.rationale,
                )
                for s in model.trajectory_signals
            ],
            data_limitations=[
                TrajectoryDataLimitationDTO(
                    metric_key=l.metric_key,
                    limitation_type=l.limitation_type,
                    description=l.description,
                    observation_count=l.observation_count,
                    rationale=l.rationale,
                )
                for l in model.data_limitations
            ],
            evidence_references=[
                TrajectoryEvidenceReferenceDTO(
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

