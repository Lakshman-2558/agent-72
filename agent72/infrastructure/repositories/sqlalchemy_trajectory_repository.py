"""SQLAlchemy 2.0 implementation of ITrajectoryRepository."""

from datetime import date, datetime
from typing import Any, Dict, List, Optional
from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from agent72.domain.interfaces.trajectory_repository import ITrajectoryRepository
from agent72.domain.models.analysis import ConfidenceAssessment
from agent72.domain.models.evidence import (
    FreshnessStatus,
    MetricDirection,
    MetricDomain,
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
)
from agent72.infrastructure.database.models import TrajectoryAnalysisModel


class SQLAlchemyTrajectoryRepository(ITrajectoryRepository):
    """Concrete repository for managing persistent, immutable trajectory analysis snapshots."""

    def __init__(self, session: Session):
        self.session = session

    def _obs_to_dict(self, o: PeriodObservation) -> Dict[str, Any]:
        return {
            "period": o.period,
            "numeric_value": o.numeric_value,
            "evidence_id": o.evidence_id,
            "as_of_date": o.as_of_date.isoformat() if o.as_of_date else None,
            "quality_tier": o.quality_tier.value if isinstance(o.quality_tier, QualityTier) else str(o.quality_tier),
            "confidence_score": o.confidence_score,
            "is_stale": o.is_stale,
        }

    def _dict_to_obs(self, d: Any) -> PeriodObservation:
        if isinstance(d, (int, float)):
            return PeriodObservation(
                period="",
                numeric_value=float(d),
                quality_tier=QualityTier.VERIFIED,
                confidence_score=0.9,
            )
        if not isinstance(d, dict):
            return PeriodObservation(
                period="",
                numeric_value=0.0,
                quality_tier=QualityTier.ESTIMATED,
                confidence_score=0.5,
            )
        as_of_raw = d.get("as_of_date")
        as_of = None
        if as_of_raw and isinstance(as_of_raw, str):
            try:
                as_of = date.fromisoformat(as_of_raw.split("T")[0])
            except Exception:
                as_of = None
        return PeriodObservation(
            period=str(d.get("period", "")),
            numeric_value=float(d.get("numeric_value", 0.0)),
            evidence_id=d.get("evidence_id"),
            as_of_date=as_of,
            quality_tier=QualityTier(d.get("quality_tier", "PROVISIONAL")) if d.get("quality_tier") in QualityTier.__members__.values() else QualityTier.PROVISIONAL,
            confidence_score=float(d.get("confidence_score", 0.0)),
            is_stale=bool(d.get("is_stale", False)),
        )

    def _metric_to_dict(self, m: TrajectoryMetric) -> Dict[str, Any]:
        return {
            "metric_key": m.metric_key,
            "metric_name": m.metric_name,
            "domain": m.domain.value if isinstance(m.domain, MetricDomain) else str(m.domain),
            "unit": m.unit,
            "direction": m.direction.value if isinstance(m.direction, MetricDirection) else str(m.direction),
            "observations": [self._obs_to_dict(o) for o in m.observations],
            "latest_value": m.latest_value,
            "earliest_value": m.earliest_value,
            "latest_period": m.latest_period,
            "earliest_period": m.earliest_period,
            "absolute_change": m.absolute_change,
            "percentage_change": m.percentage_change,
            "change_direction": m.change_direction,
            "trend_status": m.trend_status.value if isinstance(m.trend_status, TrajectoryStatus) else str(m.trend_status),
            "consistency": m.consistency.value if isinstance(m.consistency, ConsistencyRating) else str(m.consistency),
            "volatility": m.volatility,
            "volatility_score": m.volatility_score,
            "acceleration": m.acceleration.value if isinstance(m.acceleration, AccelerationStatus) else str(m.acceleration),
            "confidence_score": m.confidence_score,
            "evidence_ids": m.evidence_ids,
        }

    def _dict_to_metric(self, d: Any) -> TrajectoryMetric:
        if not isinstance(d, dict):
            return TrajectoryMetric(
                metric_key=str(d),
                metric_name=str(d),
                domain=MetricDomain.ACADEMIC_PERFORMANCE,
                unit="",
                observations=[],
            )
        domain_val = d.get("domain", "ACADEMIC_PERFORMANCE")
        domain = MetricDomain(domain_val) if domain_val in MetricDomain.__members__.values() else MetricDomain.ACADEMIC_PERFORMANCE
        dir_val = d.get("direction", "HIGHER_IS_BETTER")
        direction = MetricDirection(dir_val) if dir_val in MetricDirection.__members__.values() else MetricDirection.HIGHER_IS_BETTER
        trend_val = d.get("trend_status", "INSUFFICIENT_DATA")
        trend_status = TrajectoryStatus(trend_val) if trend_val in TrajectoryStatus.__members__.values() else TrajectoryStatus.INSUFFICIENT_DATA
        cons_val = d.get("consistency", "INSUFFICIENT_DATA")
        consistency = ConsistencyRating(cons_val) if cons_val in ConsistencyRating.__members__.values() else ConsistencyRating.INSUFFICIENT_DATA
        accel_val = d.get("acceleration", "INSUFFICIENT_DATA")
        acceleration = AccelerationStatus(accel_val) if accel_val in AccelerationStatus.__members__.values() else AccelerationStatus.INSUFFICIENT_DATA

        return TrajectoryMetric(
            metric_key=str(d.get("metric_key", "")),
            metric_name=str(d.get("metric_name", "")),
            domain=domain,
            unit=str(d.get("unit", "")),
            direction=direction,
            observations=[self._dict_to_obs(o) for o in (d.get("observations") or [])],
            latest_value=d.get("latest_value"),
            earliest_value=d.get("earliest_value"),
            latest_period=d.get("latest_period"),
            earliest_period=d.get("earliest_period"),
            absolute_change=d.get("absolute_change", d.get("net_change")),
            percentage_change=d.get("percentage_change"),
            change_direction=d.get("change_direction"),
            trend_status=trend_status,
            consistency=consistency,
            volatility=d.get("volatility"),
            volatility_score=d.get("volatility_score"),
            acceleration=acceleration,
            confidence_score=float(d.get("confidence_score", d.get("confidence", 0.0))),
            evidence_ids=d.get("evidence_ids", []),
        )

    def _signal_to_dict(self, s: TrajectorySignal) -> Dict[str, Any]:
        return {
            "metric_key": s.metric_key,
            "signal_type": s.signal_type,
            "status": s.status,
            "interpretation": s.interpretation,
            "title": s.title,
            "description": s.description,
            "severity": s.severity,
            "rationale": s.rationale,
        }

    def _dict_to_signal(self, d: Any) -> TrajectorySignal:
        if isinstance(d, str):
            return TrajectorySignal(
                metric_key="",
                signal_type="",
                status="",
                interpretation=d,
                title=d,
                description=d,
                severity="MEDIUM",
                rationale="",
            )
        if not isinstance(d, dict):
            return TrajectorySignal(
                metric_key=str(d),
                signal_type="",
                status="",
                interpretation=str(d),
                title=str(d),
                description=str(d),
                severity="MEDIUM",
                rationale="",
            )
        return TrajectorySignal(
            metric_key=str(d.get("metric_key", "")),
            signal_type=str(d.get("signal_type", "")),
            status=str(d.get("status", "")),
            interpretation=str(d.get("interpretation", d.get("signal", ""))),
            title=str(d.get("title", d.get("signal", ""))),
            description=str(d.get("description", d.get("signal", ""))),
            severity=str(d.get("severity", "MEDIUM")),
            rationale=str(d.get("rationale", "")),
        )

    def _limitation_to_dict(self, l: TrajectoryDataLimitation) -> Dict[str, Any]:
        return {
            "metric_key": l.metric_key,
            "limitation_type": l.limitation_type,
            "description": l.description,
            "observation_count": l.observation_count,
            "rationale": l.rationale,
        }

    def _dict_to_limitation(self, d: Any) -> TrajectoryDataLimitation:
        if isinstance(d, str):
            return TrajectoryDataLimitation(
                metric_key="",
                limitation_type="INSUFFICIENT_DATA",
                description=d,
                observation_count=0,
                rationale="",
            )
        if not isinstance(d, dict):
            return TrajectoryDataLimitation(
                metric_key=str(d),
                limitation_type="INSUFFICIENT_DATA",
                description=str(d),
                observation_count=0,
                rationale="",
            )
        return TrajectoryDataLimitation(
            metric_key=str(d.get("metric_key", "")),
            limitation_type=str(d.get("limitation_type", "INSUFFICIENT_DATA")),
            description=str(d.get("description", "")),
            observation_count=int(d.get("observation_count", 0)),
            rationale=str(d.get("rationale", "")),
        )

    def _ref_to_dict(self, ref: TrajectoryEvidenceReference) -> Dict[str, Any]:
        return {
            "evidence_id": ref.evidence_id,
            "metric_key": ref.metric_key,
            "period": ref.period,
            "as_of_date": ref.as_of_date.isoformat() if ref.as_of_date else None,
            "source_name": ref.source_name,
            "source_type": ref.source_type.value if isinstance(ref.source_type, SourceType) else str(ref.source_type),
            "confidence_score": ref.confidence_score,
            "quality_tier": ref.quality_tier.value if isinstance(ref.quality_tier, QualityTier) else str(ref.quality_tier),
            "freshness_status": ref.freshness_status.value if isinstance(ref.freshness_status, FreshnessStatus) else str(ref.freshness_status),
        }

    def _dict_to_ref(self, d: Any) -> TrajectoryEvidenceReference:
        if isinstance(d, str):
            return TrajectoryEvidenceReference(
                evidence_id=d,
                metric_key="",
                period="",
                as_of_date=date.today(),
                source_name=d,
                source_type=SourceType.MANUAL,
                confidence_score=1.0,
                quality_tier=QualityTier.VERIFIED,
                freshness_status=FreshnessStatus.FRESH,
            )
        if not isinstance(d, dict):
            return TrajectoryEvidenceReference(
                evidence_id=str(d),
                metric_key="",
                period="",
                as_of_date=date.today(),
                source_name=str(d),
                source_type=SourceType.MANUAL,
                confidence_score=1.0,
                quality_tier=QualityTier.PROVISIONAL,
                freshness_status=FreshnessStatus.FRESH,
            )
        as_of_raw = d.get("as_of_date")
        as_of = None
        if as_of_raw and isinstance(as_of_raw, str):
            try:
                as_of = date.fromisoformat(as_of_raw.split("T")[0])
            except Exception:
                as_of = date.today()
        return TrajectoryEvidenceReference(
            evidence_id=str(d.get("evidence_id", "")),
            metric_key=str(d.get("metric_key", "")),
            period=str(d.get("period", "")),
            as_of_date=as_of,
            source_name=str(d.get("source_name", "")),
            source_type=SourceType(d.get("source_type", "MANUAL")) if d.get("source_type") in SourceType.__members__.values() else SourceType.MANUAL,
            confidence_score=float(d.get("confidence_score", 0.0)),
            quality_tier=QualityTier(d.get("quality_tier", "PROVISIONAL")) if d.get("quality_tier") in QualityTier.__members__.values() else QualityTier.PROVISIONAL,
            freshness_status=FreshnessStatus(d.get("freshness_status", "FRESH")) if d.get("freshness_status") in FreshnessStatus.__members__.values() else FreshnessStatus.FRESH,
        )

    def _to_domain(self, model: TrajectoryAnalysisModel) -> TrajectoryAnalysis:
        confidence = ConfidenceAssessment(
            score=model.overall_confidence_score,
            level=model.confidence_level,
            factors=model.confidence_factors.get("factors", {}) if isinstance(model.confidence_factors, dict) else {},
            explanation=model.confidence_factors.get("explanation", "") if isinstance(model.confidence_factors, dict) else "",
        )

        return TrajectoryAnalysis(
            id=model.id,
            institution_id=model.institution_id,
            organizational_unit_id=model.unit_id,
            analysis_period=model.analysis_period,
            generated_at=model.generated_at,
            metric_trends=[self._dict_to_metric(m) for m in (model.metric_trends or [])],
            trajectory_signals=[self._dict_to_signal(s) for s in (model.trajectory_signals or [])],
            data_limitations=[self._dict_to_limitation(l) for l in (model.data_limitations or [])],
            evidence_references=[self._dict_to_ref(r) for r in (model.evidence_references or [])],
            assumptions=model.assumptions or [],
            overall_confidence=confidence,
            status=model.status,
        )

    def create_trajectory_analysis(self, analysis: TrajectoryAnalysis) -> TrajectoryAnalysis:
        model = TrajectoryAnalysisModel(
            id=analysis.id,
            institution_id=analysis.institution_id,
            unit_id=analysis.organizational_unit_id,
            analysis_period=analysis.analysis_period,
            generated_at=analysis.generated_at,
            overall_confidence_score=analysis.overall_confidence.score,
            confidence_level=analysis.overall_confidence.level,
            confidence_factors={
                "factors": analysis.overall_confidence.factors,
                "explanation": analysis.overall_confidence.explanation,
            },
            metric_trends=[self._metric_to_dict(m) for m in analysis.metric_trends],
            trajectory_signals=[self._signal_to_dict(s) for s in analysis.trajectory_signals],
            data_limitations=[self._limitation_to_dict(l) for l in analysis.data_limitations],
            evidence_references=[self._ref_to_dict(r) for r in analysis.evidence_references],
            assumptions=analysis.assumptions,
            status=analysis.status,
        )

        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return self._to_domain(model)

    def get_trajectory_analysis_by_id(self, analysis_id: str) -> Optional[TrajectoryAnalysis]:
        stmt = select(TrajectoryAnalysisModel).where(TrajectoryAnalysisModel.id == analysis_id)
        model = self.session.scalar(stmt)
        if not model:
            return None
        return self._to_domain(model)

    def list_trajectory_analyses(
        self,
        institution_id: Optional[str] = None,
        organizational_unit_id: Optional[str] = None,
        analysis_period: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> List[TrajectoryAnalysis]:
        stmt = select(TrajectoryAnalysisModel)
        if institution_id:
            stmt = stmt.where(TrajectoryAnalysisModel.institution_id == institution_id)
        if organizational_unit_id:
            stmt = stmt.where(TrajectoryAnalysisModel.unit_id == organizational_unit_id)
        if analysis_period:
            stmt = stmt.where(TrajectoryAnalysisModel.analysis_period == analysis_period)

        stmt = stmt.order_by(desc(TrajectoryAnalysisModel.generated_at)).offset(skip).limit(limit)
        models = self.session.scalars(stmt).all()
        return [self._to_domain(m) for m in models]

    def count_trajectory_analyses(
        self,
        institution_id: Optional[str] = None,
        organizational_unit_id: Optional[str] = None,
        analysis_period: Optional[str] = None,
    ) -> int:
        stmt = select(func.count()).select_from(TrajectoryAnalysisModel)
        if institution_id:
            stmt = stmt.where(TrajectoryAnalysisModel.institution_id == institution_id)
        if organizational_unit_id:
            stmt = stmt.where(TrajectoryAnalysisModel.unit_id == organizational_unit_id)
        if analysis_period:
            stmt = stmt.where(TrajectoryAnalysisModel.analysis_period == analysis_period)

        return self.session.scalar(stmt) or 0
