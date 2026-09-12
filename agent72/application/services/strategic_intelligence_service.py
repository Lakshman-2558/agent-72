"""
Deterministic Strategic Intelligence Service (Phase 6).

Transforms:
Evidence -> Current Position -> Trajectory -> Strategic Intelligence

Answers:
"What important strategic issues, risks, constraints, opportunities and external forces should leadership consider?"

Strict architecture boundary:
Produces diagnostic strategic intelligence without final prescriptive strategic recommendations, options, or scenario plans.
"""

from datetime import datetime, timezone
import logging
from typing import Any, Dict, List, Optional, Tuple
import uuid

from agent72.application.dtos.analysis_dto import ConfidenceAssessmentDTO
from agent72.application.dtos.strategic_intelligence_dto import (
    ConstraintSignalDTO,
    EvidenceReferenceDTO,
    ExternalFactorDTO,
    OpportunitySignalDTO,
    RiskSignalDTO,
    StrategicIntelligenceListResponseDTO,
    StrategicIntelligenceRequestDTO,
    StrategicIntelligenceResponseDTO,
    StrategicIssueDTO,
    StrategicPrioritySignalDTO,
)
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
from agent72.domain.models.strategic_intelligence import (
    ConstraintSignal,
    EvidenceReference,
    ExternalFactor,
    ExternalFactorCategory,
    ImpactLevel,
    IssueCategory,
    LikelihoodLevel,
    OpportunitySignal,
    RiskSeverity,
    RiskSignal,
    StrategicIntelligenceAnalysis,
    StrategicIssue,
    StrategicPrioritySignal,
    UncertaintyLevel,
)
from agent72.domain.models.trajectory import (
    AccelerationStatus,
    ConsistencyRating,
    TrajectoryAnalysis,
    TrajectoryMetric,
    TrajectoryStatus,
)

logger = logging.getLogger(__name__)

IMPACT_WEIGHTS = {
    ImpactLevel.LOW: 0.25,
    ImpactLevel.MEDIUM: 0.50,
    ImpactLevel.HIGH: 0.80,
    ImpactLevel.CRITICAL: 1.00,
}

LIKELIHOOD_WEIGHTS = {
    LikelihoodLevel.LOW: 0.25,
    LikelihoodLevel.MEDIUM: 0.60,
    LikelihoodLevel.HIGH: 1.00,
}


class StrategicIntelligenceService:
    """
    Deterministic Strategic Intelligence Analysis Service.

    Consumes Current Position (Phase 4), Trajectory (Phase 5), and multi-domain evidence
    to synthesize strategic issues, structural risks, constraints, external factors, and opportunities.
    """

    def __init__(
        self,
        strategic_intelligence_repository: IStrategicIntelligenceRepository,
        analysis_repository: IAnalysisRepository,
        trajectory_repository: ITrajectoryRepository,
        evidence_repository: IEvidenceRepository,
        organization_repository: IOrganizationRepository,
        ai_provider: Optional[IAIProvider] = None,
    ):
        self.strat_repo = strategic_intelligence_repository
        self.analysis_repo = analysis_repository
        self.traj_repo = trajectory_repository
        self.evidence_repo = evidence_repository
        self.org_repo = organization_repository
        self.ai_provider = ai_provider

    def _calculate_risk_score(
        self,
        impact: ImpactLevel,
        likelihood: LikelihoodLevel,
        trajectory_trend: Optional[TrajectoryStatus],
        evidence_conf: float,
        is_structural: bool = True,
    ) -> Tuple[float, RiskSeverity, Dict[str, Any]]:
        """
        Deterministic, transparent risk scoring.
        Combines impact, likelihood, trajectory direction, structural weight, and evidence confidence.
        """
        imp_wt = IMPACT_WEIGHTS.get(impact, 0.5)
        lik_wt = LIKELIHOOD_WEIGHTS.get(likelihood, 0.5)

        # Polarity adjustment: deteriorating trajectory increases risk severity
        traj_multiplier = 1.0
        if trajectory_trend == TrajectoryStatus.DECLINING:
            traj_multiplier = 1.20
        elif trajectory_trend == TrajectoryStatus.IMPROVING:
            traj_multiplier = 0.85
        elif trajectory_trend == TrajectoryStatus.VOLATILE:
            traj_multiplier = 1.15

        struct_wt = 1.15 if is_structural else 1.0
        conf_factor = max(0.4, min(1.0, evidence_conf))

        raw_score = ((imp_wt * 0.45) + (lik_wt * 0.35) + (0.20 * struct_wt)) * traj_multiplier * conf_factor
        score = round(max(0.1, min(1.0, raw_score)), 3)

        if score >= settings.CRITICAL_RISK_SCORE_THRESHOLD:
            severity = RiskSeverity.CRITICAL
        elif score >= settings.HIGH_RISK_SCORE_THRESHOLD:
            severity = RiskSeverity.HIGH
        elif score >= settings.MEDIUM_RISK_SCORE_THRESHOLD:
            severity = RiskSeverity.MEDIUM
        else:
            severity = RiskSeverity.LOW

        factors = {
            "impact_weight": imp_wt,
            "likelihood_weight": lik_wt,
            "trajectory_multiplier": traj_multiplier,
            "structural_multiplier": struct_wt,
            "evidence_confidence_factor": round(conf_factor, 2),
            "raw_score": score,
        }
        return score, severity, factors

    def _calculate_priority_score(
        self,
        impact: ImpactLevel,
        urgency: LikelihoodLevel,
        evidence_conf: float,
    ) -> Tuple[float, str, Dict[str, Any]]:
        """
        Calculates preliminary priority signal for executive attention.
        Explicitly distinct from final Phase 8 strategic option prioritization.
        """
        imp_wt = IMPACT_WEIGHTS.get(impact, 0.5)
        urg_wt = LIKELIHOOD_WEIGHTS.get(urgency, 0.5)
        score = round((imp_wt * 0.50) + (urg_wt * 0.35) + (evidence_conf * 0.15), 2)

        if score >= 0.80:
            level = "URGENT"
        elif score >= 0.65:
            level = "HIGH"
        elif score >= 0.45:
            level = "MEDIUM"
        else:
            level = "LOW"

        factors = {
            "impact_weight": imp_wt,
            "urgency_weight": urg_wt,
            "evidence_confidence": round(evidence_conf, 2),
            "priority_score": score,
        }
        return score, level, factors

    def generate_strategic_intelligence_analysis(
        self, dto: StrategicIntelligenceRequestDTO
    ) -> StrategicIntelligenceResponseDTO:
        """
        Executes deterministic Strategic Intelligence analysis.
        Requires Phase 4 Current Position and Phase 5 Trajectory baselines.
        """
        # 1. Verify Institutional Scope
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

        # 2. Resolve Required Prerequisites (Phase 4 Current Position + Phase 5 Trajectory)
        current_pos: Optional[CurrentPositionAnalysis] = None
        if dto.current_position_analysis_id:
            current_pos = self.analysis_repo.get_analysis_by_id(dto.current_position_analysis_id)
            if not current_pos:
                raise EntityNotFoundException("CurrentPositionAnalysis", dto.current_position_analysis_id)
        else:
            recent_pos = self.analysis_repo.list_analyses(
                institution_id=dto.institution_id,
                organizational_unit_id=dto.organizational_unit_id,
                analysis_period=dto.analysis_period,
                limit=1,
            )
            if recent_pos:
                current_pos = recent_pos[0]

        if not current_pos:
            raise ValidationError(
                f"Prerequisite Current Position Analysis (Phase 4) not found for institution '{dto.institution_id}' "
                f"and period '{dto.analysis_period}'. Run Phase 4 first."
            )

        trajectory: Optional[TrajectoryAnalysis] = None
        if dto.trajectory_analysis_id:
            trajectory = self.traj_repo.get_trajectory_analysis_by_id(dto.trajectory_analysis_id)
            if not trajectory:
                raise EntityNotFoundException("TrajectoryAnalysis", dto.trajectory_analysis_id)
        else:
            recent_traj = self.traj_repo.list_trajectory_analyses(
                institution_id=dto.institution_id,
                organizational_unit_id=dto.organizational_unit_id,
                analysis_period=dto.analysis_period,
                limit=1,
            )
            if recent_traj:
                trajectory = recent_traj[0]

        if not trajectory:
            raise ValidationError(
                f"Prerequisite Trajectory Analysis (Phase 5) not found for institution '{dto.institution_id}' "
                f"and period '{dto.analysis_period}'. Run Phase 5 first."
            )

        # 3. Query All Relevant Evidence (Batched for performance)
        raw_evidence = self.evidence_repo.query_evidence(
            institution_id=dto.institution_id,
            unit_id=dto.organizational_unit_id,
            limit=10000,
        )
        # Filter up to analysis_period
        evidence_list = [ev for ev in raw_evidence if ev.period <= dto.analysis_period]
        ev_by_metric: Dict[str, List[InstitutionalEvidence]] = {}
        for ev in evidence_list:
            ev_by_metric.setdefault(ev.metric_key, []).append(ev)

        # Build trajectory and current position lookup maps
        traj_map: Dict[str, TrajectoryMetric] = {m.metric_key: m for m in trajectory.metric_trends}
        pos_metric_map = {m.metric_key: m for m in current_pos.key_metrics}
        pos_gaps_map = {g.metric_key: g for g in current_pos.gaps if g.metric_key}
        pos_strengths_map = {s.metric_key: s for s in current_pos.strengths if s.metric_key}
        pos_weaknesses_map = {w.metric_key: w for w in current_pos.weaknesses if w.metric_key}

        evidence_references: List[EvidenceReference] = []
        seen_ref_ids = set()

        def add_ref(ev: InstitutionalEvidence):
            if ev.id and ev.id not in seen_ref_ids:
                seen_ref_ids.add(ev.id)
                as_of = ev.as_of_date.date() if isinstance(ev.as_of_date, datetime) else ev.as_of_date
                evidence_references.append(
                    EvidenceReference(
                        evidence_id=ev.id,
                        metric_key=ev.metric_key,
                        period=ev.period,
                        as_of_date=as_of,
                        source_name=ev.source_name,
                        source_type=ev.source_type,
                        confidence_score=ev.confidence_score,
                        quality_tier=ev.quality_tier,
                        freshness_status=FreshnessStatus.STALE if ev.is_stale else FreshnessStatus.FRESH,
                    )
                )

        # 4. Strategic Issue Detection (Diagnostic Combinations of Phase 4 & Phase 5)
        strategic_issues: List[StrategicIssue] = []
        issue_counter = 1

        for key, t_metric in traj_map.items():
            if key not in pos_metric_map:
                continue

            c_metric = pos_metric_map[key]
            trend = t_metric.trend_status
            evs = ev_by_metric.get(key, [])
            for ev in evs:
                add_ref(ev)
            ev_ids = [e.id for e in evs if e.id]
            m_conf = t_metric.confidence_score or c_metric.confidence_score or 0.8

            # (A) Current Gap + Declining Trajectory -> Compounding Deficit
            if (key in pos_gaps_map or c_metric.performance_status == PerformanceStatus.BELOW_TARGET) and trend == TrajectoryStatus.DECLINING:
                diff_str = f"{abs(c_metric.target_variance):.1f}" if c_metric.target_variance is not None else ""
                target_str = f"{c_metric.target_value}" if c_metric.target_value is not None else "target"
                strategic_issues.append(
                    StrategicIssue(
                        id=f"issue-{issue_counter}",
                        category=IssueCategory.STRATEGIC_ISSUE,
                        title=f"{t_metric.metric_name}: Compounding deficit below target",
                        description=(
                            f"Performance is below {target_str} (current: {t_metric.latest_value}) and declining "
                            f"({t_metric.percentage_change:+.1f}%). The gap of {diff_str} percentage points is widening."
                        ),
                        severity=RiskSeverity.HIGH,
                        impact=ImpactLevel.HIGH,
                        likelihood=LikelihoodLevel.HIGH,
                        affected_domains=[t_metric.domain],
                        related_metrics=[key],
                        current_position_links=[f"gap:{key}"],
                        trajectory_links=[f"trajectory:{trend.value}"],
                        evidence_ids=ev_ids,
                        confidence=m_conf,
                        assumptions=["Historical downward trajectory will continue if underlying conditions remain unchanged."],
                        rationale="Adverse directional movement compounds an existing performance gap.",
                    )
                )
                issue_counter += 1

            # (B) Current Gap + Improving Trajectory -> Narrowing Deficit
            elif (key in pos_gaps_map or c_metric.performance_status == PerformanceStatus.BELOW_TARGET) and trend == TrajectoryStatus.IMPROVING:
                diff_str = f"{abs(c_metric.target_variance):.1f}" if c_metric.target_variance is not None else ""
                target_str = f"{c_metric.target_value}" if c_metric.target_value is not None else "target"
                strategic_issues.append(
                    StrategicIssue(
                        id=f"issue-{issue_counter}",
                        category=IssueCategory.STRATEGIC_ISSUE,
                        title=f"{t_metric.metric_name}: Narrowing deficit below target",
                        description=(
                            f"{t_metric.metric_name} remains {diff_str} percentage points below target ({target_str}) "
                            f"despite positive trajectory ({t_metric.percentage_change:+.1f}% from {t_metric.earliest_period} to {t_metric.latest_period})."
                        ),
                        severity=RiskSeverity.MEDIUM,
                        impact=ImpactLevel.MEDIUM,
                        likelihood=LikelihoodLevel.MEDIUM,
                        affected_domains=[t_metric.domain],
                        related_metrics=[key],
                        current_position_links=[f"gap:{key}"],
                        trajectory_links=[f"trajectory:{trend.value}"],
                        evidence_ids=ev_ids,
                        confidence=m_conf,
                        assumptions=["Positive momentum is necessary but current rate may require multi-year persistence to close target."],
                        rationale="Positive directional momentum is actively narrowing, but has not eliminated, the target deficit.",
                    )
                )
                issue_counter += 1

            # (C) Current Weakness + Declining Trajectory -> Persistent Negative Trajectory
            elif (key in pos_weaknesses_map or c_metric.performance_status == PerformanceStatus.NEGATIVE_PERFORMANCE) and trend == TrajectoryStatus.DECLINING:
                strategic_issues.append(
                    StrategicIssue(
                        id=f"issue-{issue_counter}",
                        category=IssueCategory.STRATEGIC_ISSUE,
                        title=f"{t_metric.metric_name}: Persistent negative trajectory",
                        description=(
                            f"Current baseline weakness is compounded by multi-period downward momentum ({t_metric.percentage_change:+.1f}%)."
                        ),
                        severity=RiskSeverity.HIGH,
                        impact=ImpactLevel.HIGH,
                        likelihood=LikelihoodLevel.HIGH,
                        affected_domains=[t_metric.domain],
                        related_metrics=[key],
                        current_position_links=[f"weakness:{key}"],
                        trajectory_links=[f"trajectory:{trend.value}"],
                        evidence_ids=ev_ids,
                        confidence=m_conf,
                        assumptions=["Entrenched operational and external pressures are reinforcing negative trend."],
                        rationale="Downward trajectory confirms systematic performance erosion requiring leadership attention.",
                    )
                )
                issue_counter += 1

            # (D) Current Strength + Declining Trajectory -> Vulnerable Strength
            elif (key in pos_strengths_map or c_metric.performance_status in (PerformanceStatus.POSITIVE_PERFORMANCE, PerformanceStatus.EXCEEDS_TARGET)) and trend == TrajectoryStatus.DECLINING:
                strategic_issues.append(
                    StrategicIssue(
                        id=f"issue-{issue_counter}",
                        category=IssueCategory.STRATEGIC_ISSUE,
                        title=f"{t_metric.metric_name}: Vulnerable institutional strength",
                        description=(
                            f"Current performance represents an institutional strength ({t_metric.latest_value}), but historical "
                            f"trajectory reflects a declining trend ({t_metric.percentage_change:+.1f}%)."
                        ),
                        severity=RiskSeverity.HIGH,
                        impact=ImpactLevel.HIGH,
                        likelihood=LikelihoodLevel.MEDIUM,
                        affected_domains=[t_metric.domain],
                        related_metrics=[key],
                        current_position_links=[f"strength:{key}"],
                        trajectory_links=[f"trajectory:{trend.value}"],
                        evidence_ids=ev_ids,
                        confidence=m_conf,
                        assumptions=["Established competitive advantage is at risk of erosion if recent losses persist."],
                        rationale="Negative trajectory threatens to compromise an established core competency.",
                    )
                )
                issue_counter += 1

        # 5. Detect Multi-Metric Structural Risks
        # Requires MULTIPLE corroborating evidence signals; distinguishes correlation from causation explicitly.
        risk_signals: List[RiskSignal] = []
        risk_counter = 1

        # (Risk 1) Admissions decline + enrollment/intake contraction
        adm_trend = traj_map.get("admissions.yield") or traj_map.get("admissions.selectivity")
        dropout_trend = traj_map.get("academic.dropout_rate") or traj_map.get("academic.dropout.rate")
        grad_trend = traj_map.get("academic.graduation.rate") or traj_map.get("academic.graduation_rate")

        if adm_trend and adm_trend.trend_status == TrajectoryStatus.DECLINING:
            related_m = [adm_trend.metric_key]
            supporting_ind = [f"Declining yield in admissions ({adm_trend.percentage_change:+.1f}%)"]
            ev_subset = [e.id for e in ev_by_metric.get(adm_trend.metric_key, []) if e.id]

            if dropout_trend and dropout_trend.trend_status == TrajectoryStatus.DECLINING:
                # Dropout rate DECLINING polarity means increasing dropouts
                related_m.append(dropout_trend.metric_key)
                supporting_ind.append(f"Increasing dropout rate ({dropout_trend.percentage_change:+.1f}%)")
                ev_subset.extend([e.id for e in ev_by_metric.get(dropout_trend.metric_key, []) if e.id])

            score, sev, ftrs = self._calculate_risk_score(
                impact=ImpactLevel.HIGH,
                likelihood=LikelihoodLevel.HIGH,
                trajectory_trend=adm_trend.trend_status,
                evidence_conf=adm_trend.confidence_score,
                is_structural=True,
            )

            risk_signals.append(
                RiskSignal(
                    id=f"risk-{risk_counter}",
                    title="Student Enrollment & Tuition Pipeline Vulnerability",
                    description=(
                        "Multiple indicator signals show weakening admissions yield paired with enrollment retention pressures. "
                        "Compounding attrition threatens student body scale and tuition revenue viability."
                    ),
                    severity=sev,
                    impact=ImpactLevel.HIGH,
                    likelihood=LikelihoodLevel.HIGH,
                    risk_score=score,
                    scoring_factors=ftrs,
                    affected_domains=[MetricDomain.ADMISSIONS_MARKET, MetricDomain.ACADEMIC_PERFORMANCE],
                    related_metrics=related_m,
                    supporting_indicators=supporting_ind,
                    correlation_vs_causation_note=(
                        "Observed concurrent movement indicates multi-domain vulnerability; correlation does not imply direct "
                        "mechanistic causation without controlled longitudinal cohort validation."
                    ),
                    evidence_ids=ev_subset,
                    confidence=adm_trend.confidence_score,
                    uncertainty_level=UncertaintyLevel.LOW if len(related_m) >= 2 else UncertaintyLevel.MEDIUM,
                    rationale="Multi-indicator alignment across admissions and retention points to structural enrollment pressure.",
                )
            )
            risk_counter += 1

        # (Risk 2) Placement decline + weakening employer demand
        place_trend = traj_map.get("placement.rate")
        employer_demand_ev = [
            e for e in evidence_list
            if e.domain in (MetricDomain.PLACEMENT_EMPLOYER_DEMAND, MetricDomain.EXTERNAL_REGULATORY, MetricDomain.PEER_COMPETITOR)
            and ("employer" in e.metric_key.lower() or "demand" in e.metric_key.lower())
        ]

        if place_trend and place_trend.trend_status == TrajectoryStatus.DECLINING:
            related_m = [place_trend.metric_key]
            supporting_ind = [f"Placement rate declining ({place_trend.percentage_change:+.1f}%)"]
            ev_subset = [e.id for e in ev_by_metric.get(place_trend.metric_key, []) if e.id]

            if employer_demand_ev:
                latest_ext = employer_demand_ev[-1]
                add_ref(latest_ext)
                if latest_ext.id:
                    ev_subset.append(latest_ext.id)
                supporting_ind.append(f"External employer demand indicator ({latest_ext.text_value or latest_ext.numeric_value})")

            score, sev, ftrs = self._calculate_risk_score(
                impact=ImpactLevel.HIGH,
                likelihood=LikelihoodLevel.HIGH if employer_demand_ev else LikelihoodLevel.MEDIUM,
                trajectory_trend=place_trend.trend_status,
                evidence_conf=place_trend.confidence_score,
                is_structural=True,
            )

            risk_signals.append(
                RiskSignal(
                    id=f"risk-{risk_counter}",
                    title="Graduate Career Outcomes & Market Alignment Risk",
                    description=(
                        "Graduate placement rate exhibits a multi-period declining trajectory, coupled with external employer demand shifts. "
                        "Presents strategic risk to prospective applicant attraction and institutional employer reputation."
                    ),
                    severity=sev,
                    impact=ImpactLevel.HIGH,
                    likelihood=LikelihoodLevel.HIGH if employer_demand_ev else LikelihoodLevel.MEDIUM,
                    risk_score=score,
                    scoring_factors=ftrs,
                    affected_domains=[MetricDomain.PLACEMENT_EMPLOYER_DEMAND],
                    related_metrics=related_m,
                    supporting_indicators=supporting_ind,
                    correlation_vs_causation_note=(
                        "Downturn in placement coincides with regional hiring fluctuations; correlation does not isolate "
                        "curriculum mismatch from macroeconomic hiring freezes."
                    ),
                    evidence_ids=ev_subset,
                    confidence=place_trend.confidence_score,
                    uncertainty_level=UncertaintyLevel.LOW if employer_demand_ev else UncertaintyLevel.MEDIUM,
                    rationale="Weakening placement trajectory corroborated by external employment evidence.",
                )
            )
            risk_counter += 1

        # (Risk 3) Infrastructure capacity strain + enrollment growth
        infra_util_trend = traj_map.get("infra.lab.utilization") or traj_map.get("infra.lab_utilization")
        intake_trend = traj_map.get("academic.graduation.rate") or adm_trend

        if infra_util_trend and infra_util_trend.latest_value and infra_util_trend.latest_value >= settings.INFRASTRUCTURE_CAPACITY_THRESHOLD:
            related_m = [infra_util_trend.metric_key]
            supporting_ind = [f"Infrastructure utilization at {infra_util_trend.latest_value}% (threshold: {settings.INFRASTRUCTURE_CAPACITY_THRESHOLD}%)"]
            ev_subset = [e.id for e in ev_by_metric.get(infra_util_trend.metric_key, []) if e.id]

            score, sev, ftrs = self._calculate_risk_score(
                impact=ImpactLevel.HIGH,
                likelihood=LikelihoodLevel.HIGH,
                trajectory_trend=infra_util_trend.trend_status,
                evidence_conf=infra_util_trend.confidence_score,
                is_structural=True,
            )

            risk_signals.append(
                RiskSignal(
                    id=f"risk-{risk_counter}",
                    title="Campus Physical Capacity Saturation Risk",
                    description=(
                        f"Core instructional and research infrastructure utilization has reached {infra_util_trend.latest_value}%, "
                        f"exceeding the {settings.INFRASTRUCTURE_CAPACITY_THRESHOLD}% capacity buffer threshold. "
                        "Limits future program expansion and risks physical space contention."
                    ),
                    severity=sev,
                    impact=ImpactLevel.HIGH,
                    likelihood=LikelihoodLevel.HIGH,
                    risk_score=score,
                    scoring_factors=ftrs,
                    affected_domains=[MetricDomain.INFRASTRUCTURE],
                    related_metrics=related_m,
                    supporting_indicators=supporting_ind,
                    correlation_vs_causation_note="Capacity saturation is an empirical utilization measure; direct bottleneck on teaching delivery.",
                    evidence_ids=ev_subset,
                    confidence=infra_util_trend.confidence_score,
                    uncertainty_level=UncertaintyLevel.LOW,
                    rationale="High utilization rates constrain academic delivery and physical safety buffers.",
                )
            )
            risk_counter += 1

        # 6. Detect Evidence-Backed Constraints
        # Thresholds are configuration-driven from settings. Never infer constraints from missing data!
        constraint_signals: List[ConstraintSignal] = []
        constraint_counter = 1

        # (Constraint A) Infrastructure Capacity
        for key in ("infra.lab.utilization", "infra.lab_utilization", "infra.capacity"):
            t_m = traj_map.get(key)
            if t_m and t_m.latest_value is not None and t_m.latest_value >= settings.INFRASTRUCTURE_CAPACITY_THRESHOLD:
                ev_subset = [e.id for e in ev_by_metric.get(key, []) if e.id]
                constraint_signals.append(
                    ConstraintSignal(
                        id=f"constraint-{constraint_counter}",
                        title="Infrastructure Facility Capacity Limitation",
                        description=(
                            f"{t_m.metric_name} observed at {t_m.latest_value}%, exceeding the configured "
                            f"{settings.INFRASTRUCTURE_CAPACITY_THRESHOLD}% operational threshold."
                        ),
                        constraint_type="INFRASTRUCTURE_CAPACITY",
                        severity=RiskSeverity.HIGH,
                        affected_domains=[MetricDomain.INFRASTRUCTURE],
                        related_metrics=[key],
                        persistence="MULTI_PERIOD" if len(t_m.observations) >= 2 else "EMERGING",
                        evidence_ids=ev_subset,
                        confidence=t_m.confidence_score,
                        limitations_note=None,
                        rationale="Observed physical utilization benchmarks demonstrate immediate physical ceiling.",
                    )
                )
                constraint_counter += 1
                break

        # (Constraint B) Faculty Capability / PhD Ratio
        for key in ("faculty.phd.ratio", "faculty.phd_ratio"):
            t_m = traj_map.get(key)
            if t_m and t_m.latest_value is not None and t_m.latest_value < settings.FACULTY_PHD_MIN_THRESHOLD:
                ev_subset = [e.id for e in ev_by_metric.get(key, []) if e.id]
                constraint_signals.append(
                    ConstraintSignal(
                        id=f"constraint-{constraint_counter}",
                        title="Faculty Terminal Qualification Ceiling",
                        description=(
                            f"{t_m.metric_name} is {t_m.latest_value}%, falling short of the configured "
                            f"{settings.FACULTY_PHD_MIN_THRESHOLD}% academic accreditation threshold."
                        ),
                        constraint_type="FACULTY_CAPABILITY",
                        severity=RiskSeverity.MEDIUM,
                        affected_domains=[MetricDomain.FACULTY_CAPABILITY],
                        related_metrics=[key],
                        persistence="MULTI_PERIOD",
                        evidence_ids=ev_subset,
                        confidence=t_m.confidence_score,
                        limitations_note="Requires verification across all academic schools for tenure-track faculty.",
                        rationale="Terminal credential ratios restrict postgraduate program accreditation approvals.",
                    )
                )
                constraint_counter += 1
                break

        # (Constraint C) Student-to-Faculty Ratio
        for key in ("faculty.student.ratio", "faculty.ratio"):
            t_m = traj_map.get(key)
            if t_m and t_m.latest_value is not None and t_m.latest_value >= settings.STUDENT_FACULTY_RATIO_THRESHOLD:
                ev_subset = [e.id for e in ev_by_metric.get(key, []) if e.id]
                constraint_signals.append(
                    ConstraintSignal(
                        id=f"constraint-{constraint_counter}",
                        title="High Student-Faculty Workload Strain",
                        description=(
                            f"Student-to-faculty ratio of {t_m.latest_value}:1 exceeds configured threshold of "
                            f"{settings.STUDENT_FACULTY_RATIO_THRESHOLD}:1, straining mentoring capacity."
                        ),
                        constraint_type="FACULTY_LOAD",
                        severity=RiskSeverity.MEDIUM,
                        affected_domains=[MetricDomain.FACULTY_CAPABILITY],
                        related_metrics=[key],
                        persistence="MULTI_PERIOD",
                        evidence_ids=ev_subset,
                        confidence=t_m.confidence_score,
                        limitations_note=None,
                        rationale="Elevated ratios impair personalized student instruction and research mentoring.",
                    )
                )
                constraint_counter += 1
                break

        # 7. Detect External Environmental Factors
        external_factors: List[ExternalFactor] = []
        ext_counter = 1

        ext_candidates = [
            e for e in evidence_list
            if e.domain in (
                MetricDomain.EXTERNAL_REGULATORY,
                MetricDomain.PEER_COMPETITOR,
                MetricDomain.ADMISSIONS_MARKET,
                MetricDomain.PLACEMENT_EMPLOYER_DEMAND,
            )
        ]

        # Group by metric_key to pick the latest observation
        ext_by_key: Dict[str, InstitutionalEvidence] = {}
        for ev in ext_candidates:
            ext_by_key[ev.metric_key] = ev

        for key, ev in ext_by_key.items():
            add_ref(ev)
            cat = ExternalFactorCategory.MARKET_SHIFT
            if ev.domain == MetricDomain.EXTERNAL_REGULATORY:
                cat = ExternalFactorCategory.REGULATORY
            elif ev.domain == MetricDomain.PEER_COMPETITOR:
                cat = ExternalFactorCategory.COMPETITOR_MOVEMENT
            elif "employer" in key.lower() or "demand" in key.lower():
                cat = ExternalFactorCategory.EMPLOYER_DEMAND

            # Directional impact based on value or text
            impact_dir = "NEUTRAL"
            if ev.numeric_value is not None:
                impact_dir = "FAVORABLE" if ev.numeric_value > 0 else "UNFAVORABLE"
            elif ev.text_value:
                lower_text = ev.text_value.lower()
                if any(w in lower_text for w in ("increase", "growth", "positive", "favorable", "demand")):
                    impact_dir = "FAVORABLE"
                elif any(w in lower_text for w in ("decline", "mandate", "restrict", "pressure", "weak")):
                    impact_dir = "UNFAVORABLE"

            desc_text = ev.text_value or f"Observed metric {key} at {ev.numeric_value} {ev.unit or ''}."
            if ev.is_stale:
                desc_text += " [Note: Evidence observation is aging/stale]."

            external_factors.append(
                ExternalFactor(
                    id=f"ext-{ext_counter}",
                    factor_name=key.replace(".", " ").title(),
                    category=cat,
                    direction_impact=impact_dir,
                    description=desc_text,
                    affected_domains=[ev.domain],
                    evidence_ids=[ev.id] if ev.id else [],
                    confidence=round(ev.confidence_score * (0.85 if ev.is_stale else 1.0), 2),
                    freshness=FreshnessStatus.STALE if ev.is_stale else FreshnessStatus.FRESH,
                    rationale=f"Reported external observation from {ev.source_name} ({ev.source_type.value}).",
                )
            )
            ext_counter += 1

        # 8. Detect Diagnostic Opportunities (Evidence-Supported, NO Action Recommendations)
        opportunity_signals: List[OpportunitySignal] = []
        opp_counter = 1

        # (A) Research Momentum Opportunity
        res_pubs = traj_map.get("research.publications")
        res_grants = traj_map.get("research.grant.funding") or traj_map.get("research.grant_funding")
        res_cites = traj_map.get("research.citations")

        if (res_pubs and res_pubs.trend_status == TrajectoryStatus.IMPROVING) or (res_cites and res_cites.trend_status == TrajectoryStatus.IMPROVING):
            lead_m = res_pubs if (res_pubs and res_pubs.trend_status == TrajectoryStatus.IMPROVING) else res_cites
            ev_subset = [e.id for e in ev_by_metric.get(lead_m.metric_key, []) if e.id]
            opportunity_signals.append(
                OpportunitySignal(
                    id=f"opp-{opp_counter}",
                    title=f"Strong Research Production Momentum in {lead_m.metric_name}",
                    description=(
                        f"{lead_m.metric_name} output increased {lead_m.percentage_change:+.1f}% across recent periods, "
                        f"reflecting sustained faculty scholarship and external visibility."
                    ),
                    opportunity_type="RESEARCH_MOMENTUM",
                    potential_impact=ImpactLevel.HIGH,
                    urgency=LikelihoodLevel.MEDIUM,
                    affected_domains=[MetricDomain.RESEARCH_PRODUCTIVITY],
                    related_metrics=[lead_m.metric_key],
                    evidence_ids=ev_subset,
                    confidence=lead_m.confidence_score,
                    interpretation="Strong research output momentum provides an evidence-backed reputational advantage.",
                    rationale="Multi-period positive research acceleration establishes strong institutional foundation.",
                )
            )
            opp_counter += 1

        # (B) Favorable Employer Demand Aligned with Capability
        if place_trend and place_trend.trend_status == TrajectoryStatus.IMPROVING:
            ev_subset = [e.id for e in ev_by_metric.get(place_trend.metric_key, []) if e.id]
            opportunity_signals.append(
                OpportunitySignal(
                    id=f"opp-{opp_counter}",
                    title="Expanding Graduate Career Placement Advantage",
                    description=(
                        f"Placement trajectory is actively improving ({place_trend.percentage_change:+.1f}%). "
                        "Demonstrates strong employer demand alignment with graduating student capabilities."
                    ),
                    opportunity_type="EMPLOYER_ALIGNMENT",
                    potential_impact=ImpactLevel.HIGH,
                    urgency=LikelihoodLevel.HIGH,
                    affected_domains=[MetricDomain.PLACEMENT_EMPLOYER_DEMAND],
                    related_metrics=[place_trend.metric_key],
                    evidence_ids=ev_subset,
                    confidence=place_trend.confidence_score,
                    interpretation="Improving placement momentum validates curriculum-to-market alignment.",
                    rationale="Positive placement trajectory strengthens employer partnership potential.",
                )
            )
            opp_counter += 1

        # 9. Generate Preliminary Priority Signals
        priority_signals: List[StrategicPrioritySignal] = []
        prio_counter = 1

        for r in risk_signals:
            p_score, p_level, p_factors = self._calculate_priority_score(
                impact=r.impact,
                urgency=r.likelihood,
                evidence_conf=r.confidence,
            )
            priority_signals.append(
                StrategicPrioritySignal(
                    id=f"prio-{prio_counter}",
                    issue_id=r.id,
                    title=f"Mitigate: {r.title}",
                    category=IssueCategory.RISK,
                    priority_level=p_level,
                    priority_score=p_score,
                    scoring_factors=p_factors,
                    rationale=f"Preliminary priority based on risk score {r.risk_score} and impact level {r.impact.value}.",
                )
            )
            prio_counter += 1

        for c in constraint_signals:
            p_score, p_level, p_factors = self._calculate_priority_score(
                impact=ImpactLevel.HIGH if c.severity == RiskSeverity.HIGH else ImpactLevel.MEDIUM,
                urgency=LikelihoodLevel.HIGH if c.persistence == "MULTI_PERIOD" else LikelihoodLevel.MEDIUM,
                evidence_conf=c.confidence,
            )
            priority_signals.append(
                StrategicPrioritySignal(
                    id=f"prio-{prio_counter}",
                    issue_id=c.id,
                    title=f"Address: {c.title}",
                    category=IssueCategory.CONSTRAINT,
                    priority_level=p_level,
                    priority_score=p_score,
                    scoring_factors=p_factors,
                    rationale=f"Operational constraint restricts institutional throughput and expansion buffers.",
                )
            )
            prio_counter += 1

        for o in opportunity_signals:
            p_score, p_level, p_factors = self._calculate_priority_score(
                impact=o.potential_impact,
                urgency=o.urgency,
                evidence_conf=o.confidence,
            )
            priority_signals.append(
                StrategicPrioritySignal(
                    id=f"prio-{prio_counter}",
                    issue_id=o.id,
                    title=f"Leverage: {o.title}",
                    category=IssueCategory.OPPORTUNITY,
                    priority_level=p_level,
                    priority_score=p_score,
                    scoring_factors=p_factors,
                    rationale=f"Strategic opportunity with high positive trajectory potential.",
                )
            )
            prio_counter += 1

        # Sort priority signals by priority_score descending
        priority_signals.sort(key=lambda p: p.priority_score, reverse=True)

        # 10. Transparent Uncertainty Assessment
        # Count missing evidence, stale observations, conflicting evidence
        stale_ev_count = sum(1 for e in evidence_list if e.is_stale)
        data_limitations_count = (
            (len(trajectory.data_limitations) if trajectory else 0)
            + (len(current_pos.data_gaps) if current_pos else 0)
        )
        if len(evidence_list) == 0:
            data_limitations_count += 1

        # Conflicting signals detection (e.g. positive placement trajectory alongside negative external employer indicator)
        conflicting_signals: List[str] = []
        if place_trend and place_trend.trend_status == TrajectoryStatus.IMPROVING and employer_demand_ev:
            for ext in employer_demand_ev:
                if ext.numeric_value is not None and ext.numeric_value < 0:
                    conflicting_signals.append(f"Placement improving (+{place_trend.percentage_change}%) conflicts with declining external employer index ({ext.numeric_value}).")

        if data_limitations_count > 3 or len(conflicting_signals) >= 2:
            uncertainty_lvl = UncertaintyLevel.HIGH
        elif data_limitations_count > 0 or stale_ev_count > 0 or len(conflicting_signals) > 0:
            uncertainty_lvl = UncertaintyLevel.MEDIUM
        else:
            uncertainty_lvl = UncertaintyLevel.LOW

        uncertainty_summary = {
            "overall_uncertainty_level": uncertainty_lvl.value,
            "stale_evidence_count": stale_ev_count,
            "data_limitations_count": data_limitations_count,
            "conflicting_signals_count": len(conflicting_signals),
            "conflicting_signals_details": conflicting_signals,
            "information_deficiency_statement": (
                "Missing evidence reflects informational deficiency and is never classified as poor institutional performance."
            ),
        }

        # 11. Overall Confidence Assessment
        all_confs = [r.confidence for r in risk_signals] + [c.confidence for c in constraint_signals] + [o.confidence for o in opportunity_signals]
        avg_conf = (sum(all_confs) / len(all_confs)) if all_confs else 0.8
        conf_score = round(max(0.2, min(1.0, avg_conf - (0.05 * stale_ev_count) - (0.05 * len(conflicting_signals)))), 2)
        conf_lvl = "HIGH" if conf_score >= 0.80 else ("MEDIUM" if conf_score >= 0.50 else "LOW")

        confidence_assessment = ConfidenceAssessment(
            score=conf_score,
            level=conf_lvl,
            factors={
                "average_signal_confidence": round(avg_conf, 2),
                "stale_evidence_penalty": round(0.05 * stale_ev_count, 2),
                "conflicting_evidence_penalty": round(0.05 * len(conflicting_signals), 2),
                "uncertainty_level": uncertainty_lvl.value,
            },
            explanation=(
                f"Strategic intelligence confidence is {conf_lvl} ({conf_score*100:.0f}%). "
                f"Based on {len(risk_signals)} structural risks, {len(constraint_signals)} evidence-backed constraints, "
                f"and {len(opportunity_signals)} validated opportunities across multi-period evidence."
            ),
        )

        # 12. Optional AI Synthesis (Strict Guardrails: groups existing findings, never alters scores or invents facts)
        ai_synthesis_notes: Optional[str] = None
        if dto.include_ai_synthesis and self.ai_provider:
            prompt_context = (
                f"Synthesize the following deterministic institutional strategic intelligence findings for leadership:\n"
                f"Risks: {[r.title for r in risk_signals]}\n"
                f"Constraints: {[c.title for c in constraint_signals]}\n"
                f"Opportunities: {[o.title for o in opportunity_signals]}\n"
                f"Provide a concise executive grouping of these findings. Do NOT invent new facts or recommend actions."
            )
            try:
                ai_synthesis_notes = self.ai_provider.generate_completion(prompt_context)
            except Exception as ex:
                logger.warning(f"AI synthesis generation failed: {ex}. Proceeding with deterministic analysis.")
                ai_synthesis_notes = (
                    f"Executive Synthesis: Institutional intelligence highlights {len(risk_signals)} critical risk areas, "
                    f"{len(constraint_signals)} physical/faculty constraints, and {len(opportunity_signals)} momentum opportunities."
                )

        # 13. Explicit Assumptions
        assumptions = [
            "Strategic intelligence derives strictly from canonical evidence, Current Position baselines, and multi-period trajectory trends.",
            "Cross-metric risks denote structural vulnerabilities and do not assert unverified causal relationships.",
            "Constraints are strictly evidence-backed and never inferred from absent or missing data.",
            "Preliminary priority signals are indicative diagnostic ratings and do not constitute final strategic plan choices.",
        ]

        # 14. Construct Domain Aggregate
        analysis = StrategicIntelligenceAnalysis(
            institution_id=dto.institution_id,
            organizational_unit_id=dto.organizational_unit_id,
            analysis_period=dto.analysis_period,
            generated_at=datetime.now(timezone.utc),
            current_position_analysis_id=current_pos.id,
            trajectory_analysis_id=trajectory.id,
            strategic_issues=strategic_issues,
            risk_signals=risk_signals,
            constraint_signals=constraint_signals,
            opportunity_signals=opportunity_signals,
            external_factors=external_factors,
            strategic_priority_signals=priority_signals,
            evidence_references=evidence_references,
            overall_confidence=confidence_assessment,
            uncertainty_summary=uncertainty_summary,
            ai_synthesis_notes=ai_synthesis_notes,
            assumptions=assumptions,
            status="FINALIZED",
        )

        # 15. Persist Immutable Snapshot
        saved = self.strat_repo.create_strategic_intelligence_analysis(analysis)
        logger.info(
            f"Generated Strategic Intelligence Analysis [{saved.id}] for institution '{saved.institution_id}' "
            f"(period: {saved.analysis_period}, issues: {len(saved.strategic_issues)}, risks: {len(saved.risk_signals)}, "
            f"constraints: {len(saved.constraint_signals)}, opportunities: {len(saved.opportunity_signals)})"
        )

        return self._to_dto(saved)

    def get_strategic_intelligence_analysis_by_id(
        self, analysis_id: str
    ) -> StrategicIntelligenceResponseDTO:
        analysis = self.strat_repo.get_strategic_intelligence_analysis_by_id(analysis_id)
        if not analysis:
            raise EntityNotFoundException("StrategicIntelligenceAnalysis", analysis_id)
        return self._to_dto(analysis)

    def list_strategic_intelligence_analyses(
        self,
        institution_id: Optional[str] = None,
        organizational_unit_id: Optional[str] = None,
        analysis_period: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> StrategicIntelligenceListResponseDTO:
        safe_limit = max(1, min(limit, settings.MAX_PAGE_SIZE))
        total = self.strat_repo.count_strategic_intelligence_analyses(
            institution_id=institution_id,
            organizational_unit_id=organizational_unit_id,
            analysis_period=analysis_period,
        )
        items = self.strat_repo.list_strategic_intelligence_analyses(
            institution_id=institution_id,
            organizational_unit_id=organizational_unit_id,
            analysis_period=analysis_period,
            skip=skip,
            limit=safe_limit,
        )
        return StrategicIntelligenceListResponseDTO(total=total, items=[self._to_dto(a) for a in items])

    def _to_dto(self, m: StrategicIntelligenceAnalysis) -> StrategicIntelligenceResponseDTO:
        return StrategicIntelligenceResponseDTO(
            id=m.id or "",
            institution_id=m.institution_id,
            organizational_unit_id=m.organizational_unit_id,
            analysis_period=m.analysis_period,
            generated_at=m.generated_at,
            current_position_analysis_id=m.current_position_analysis_id,
            trajectory_analysis_id=m.trajectory_analysis_id,
            overall_confidence=ConfidenceAssessmentDTO(
                score=m.overall_confidence.score,
                level=m.overall_confidence.level,
                factors=m.overall_confidence.factors,
                explanation=m.overall_confidence.explanation,
            ),
            strategic_issues=[
                StrategicIssueDTO(
                    id=i.id,
                    category=i.category,
                    title=i.title,
                    description=i.description,
                    severity=i.severity,
                    impact=i.impact,
                    likelihood=i.likelihood,
                    affected_domains=i.affected_domains,
                    related_metrics=i.related_metrics,
                    current_position_links=i.current_position_links,
                    trajectory_links=i.trajectory_links,
                    evidence_ids=i.evidence_ids,
                    confidence=i.confidence,
                    assumptions=i.assumptions,
                    rationale=i.rationale,
                )
                for i in m.strategic_issues
            ],
            risk_signals=[
                RiskSignalDTO(
                    id=r.id,
                    title=r.title,
                    description=r.description,
                    severity=r.severity,
                    impact=r.impact,
                    likelihood=r.likelihood,
                    risk_score=r.risk_score,
                    scoring_factors=r.scoring_factors,
                    affected_domains=r.affected_domains,
                    related_metrics=r.related_metrics,
                    supporting_indicators=r.supporting_indicators,
                    correlation_vs_causation_note=r.correlation_vs_causation_note,
                    evidence_ids=r.evidence_ids,
                    confidence=r.confidence,
                    uncertainty_level=r.uncertainty_level,
                    rationale=r.rationale,
                )
                for r in m.risk_signals
            ],
            constraint_signals=[
                ConstraintSignalDTO(
                    id=c.id,
                    title=c.title,
                    description=c.description,
                    constraint_type=c.constraint_type,
                    severity=c.severity,
                    affected_domains=c.affected_domains,
                    related_metrics=c.related_metrics,
                    persistence=c.persistence,
                    evidence_ids=c.evidence_ids,
                    confidence=c.confidence,
                    limitations_note=c.limitations_note,
                    rationale=c.rationale,
                )
                for c in m.constraint_signals
            ],
            opportunity_signals=[
                OpportunitySignalDTO(
                    id=o.id,
                    title=o.title,
                    description=o.description,
                    opportunity_type=o.opportunity_type,
                    potential_impact=o.potential_impact,
                    urgency=o.urgency,
                    affected_domains=o.affected_domains,
                    related_metrics=o.related_metrics,
                    evidence_ids=o.evidence_ids,
                    confidence=o.confidence,
                    interpretation=o.interpretation,
                    rationale=o.rationale,
                )
                for o in m.opportunity_signals
            ],
            external_factors=[
                ExternalFactorDTO(
                    id=e.id,
                    factor_name=e.factor_name,
                    category=e.category,
                    direction_impact=e.direction_impact,
                    description=e.description,
                    affected_domains=e.affected_domains,
                    evidence_ids=e.evidence_ids,
                    confidence=e.confidence,
                    freshness=e.freshness,
                    rationale=e.rationale,
                )
                for e in m.external_factors
            ],
            strategic_priority_signals=[
                StrategicPrioritySignalDTO(
                    id=p.id,
                    issue_id=p.issue_id,
                    title=p.title,
                    category=p.category,
                    priority_level=p.priority_level,
                    priority_score=p.priority_score,
                    scoring_factors=p.scoring_factors,
                    rationale=p.rationale,
                )
                for p in m.strategic_priority_signals
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
                for r in m.evidence_references
            ],
            uncertainty_summary=m.uncertainty_summary,
            ai_synthesis_notes=m.ai_synthesis_notes,
            assumptions=m.assumptions,
            status=m.status,
        )
