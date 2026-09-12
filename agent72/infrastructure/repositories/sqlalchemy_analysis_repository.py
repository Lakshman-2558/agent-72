"""SQLAlchemy 2.0 implementation of IAnalysisRepository."""

from datetime import date, datetime
from typing import Any, Dict, List, Optional
from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from agent72.domain.interfaces.analysis_repository import IAnalysisRepository
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
    MetricDirection,
    MetricDomain,
    QualityTier,
    SourceType,
)
from agent72.infrastructure.database.models import CurrentPositionAnalysisModel


class SQLAlchemyAnalysisRepository(IAnalysisRepository):
    """Concrete repository for managing persistent, immutable current-position analysis snapshots."""

    def __init__(self, session: Session):
        self.session = session

    def _finding_to_dict(self, f: PositionFinding) -> Dict[str, Any]:
        return {
            "id": f.id,
            "category": f.category.value if isinstance(f.category, FindingCategory) else str(f.category),
            "title": f.title,
            "description": f.description,
            "severity": f.severity.value if isinstance(f.severity, FindingSeverity) else str(f.severity),
            "metric_key": f.metric_key,
            "observed_value": f.observed_value,
            "comparison_value": f.comparison_value,
            "comparison_type": f.comparison_type.value if isinstance(f.comparison_type, ComparisonType) else str(f.comparison_type),
            "evidence_ids": f.evidence_ids,
            "confidence_score": f.confidence_score,
            "quality_tier": f.quality_tier.value if isinstance(f.quality_tier, QualityTier) else str(f.quality_tier),
            "freshness_status": f.freshness_status.value if isinstance(f.freshness_status, FreshnessStatus) else str(f.freshness_status),
            "rationale": f.rationale,
        }

    def _dict_to_finding(self, d: Any, default_category: FindingCategory = FindingCategory.STRENGTH) -> PositionFinding:
        if isinstance(d, str):
            return PositionFinding(
                category=default_category,
                title=d,
                description=d,
                severity=FindingSeverity.MEDIUM,
                confidence_score=1.0,
                quality_tier=QualityTier.VERIFIED,
                freshness_status=FreshnessStatus.FRESH,
            )
        if not isinstance(d, dict):
            return PositionFinding(
                category=default_category,
                title=str(d),
                description=str(d),
            )
        cat_val = d.get("category", default_category.value)
        category = FindingCategory(cat_val) if cat_val in FindingCategory.__members__.values() else default_category

        sev_val = d.get("severity", "MEDIUM")
        severity = FindingSeverity(sev_val) if sev_val in FindingSeverity.__members__.values() else FindingSeverity.MEDIUM

        comp_val = d.get("comparison_type", "NONE")
        comparison_type = ComparisonType(comp_val) if comp_val in ComparisonType.__members__.values() else ComparisonType.NONE

        qual_val = d.get("quality_tier", "VERIFIED")
        quality_tier = QualityTier(qual_val) if qual_val in QualityTier.__members__.values() else QualityTier.VERIFIED

        fresh_val = d.get("freshness_status", "FRESH")
        freshness_status = FreshnessStatus(fresh_val) if fresh_val in FreshnessStatus.__members__.values() else FreshnessStatus.FRESH

        return PositionFinding(
            id=d.get("id"),
            category=category,
            title=d.get("title", ""),
            description=d.get("description", ""),
            severity=severity,
            metric_key=d.get("metric_key"),
            observed_value=d.get("observed_value"),
            comparison_value=d.get("comparison_value"),
            comparison_type=comparison_type,
            evidence_ids=d.get("evidence_ids", []),
            confidence_score=float(d.get("confidence_score", 1.0)),
            quality_tier=quality_tier,
            freshness_status=freshness_status,
            rationale=d.get("rationale", ""),
        )

    def _metric_to_dict(self, m: MetricAssessment) -> Dict[str, Any]:
        return {
            "metric_key": m.metric_key,
            "metric_name": m.metric_name,
            "domain": m.domain.value if isinstance(m.domain, MetricDomain) else str(m.domain),
            "unit": m.unit,
            "direction": m.direction.value if isinstance(m.direction, MetricDirection) else str(m.direction),
            "latest_value": m.latest_value,
            "latest_period": m.latest_period,
            "previous_value": m.previous_value,
            "previous_period": m.previous_period,
            "change_direction": m.change_direction,
            "absolute_change": m.absolute_change,
            "percent_change": m.percent_change,
            "target_value": m.target_value,
            "target_variance": m.target_variance,
            "performance_status": m.performance_status.value if isinstance(m.performance_status, PerformanceStatus) else str(m.performance_status),
            "comparison_status": m.comparison_status,
            "freshness_status": m.freshness_status.value if isinstance(m.freshness_status, FreshnessStatus) else str(m.freshness_status),
            "quality_tier": m.quality_tier.value if isinstance(m.quality_tier, QualityTier) else str(m.quality_tier),
            "confidence_score": m.confidence_score,
            "evidence_id": m.evidence_id,
        }

    def _dict_to_metric(self, d: Any) -> MetricAssessment:
        if not isinstance(d, dict):
            return MetricAssessment(
                metric_key=str(d),
                metric_name=str(d),
                domain=MetricDomain.ACADEMIC_PERFORMANCE,
                unit="",
            )
        domain_val = d.get("domain", "ACADEMIC_PERFORMANCE")
        domain = MetricDomain(domain_val) if domain_val in MetricDomain.__members__.values() else MetricDomain.ACADEMIC_PERFORMANCE

        dir_val = d.get("direction", "HIGHER_IS_BETTER")
        direction = MetricDirection(dir_val) if dir_val in MetricDirection.__members__.values() else MetricDirection.HIGHER_IS_BETTER

        fresh_val = d.get("freshness_status", "FRESH")
        freshness_status = FreshnessStatus(fresh_val) if fresh_val in FreshnessStatus.__members__.values() else FreshnessStatus.FRESH

        qual_val = d.get("quality_tier", "VERIFIED")
        quality_tier = QualityTier(qual_val) if qual_val in QualityTier.__members__.values() else QualityTier.VERIFIED

        perf_raw = str(d.get("performance_status", "")).upper()
        if perf_raw in ("CRITICAL", "DEFICIT", "BELOW_TARGET"):
            perf_status = PerformanceStatus.BELOW_TARGET
        elif d.get("performance_status") in PerformanceStatus.__members__.values():
            perf_status = PerformanceStatus(d["performance_status"])
        else:
            perf_status = PerformanceStatus.NEUTRAL

        return MetricAssessment(
            metric_key=d.get("metric_key", ""),
            metric_name=d.get("metric_name", ""),
            domain=domain,
            unit=d.get("unit", ""),
            direction=direction,
            latest_value=d.get("latest_value", d.get("observed_value")),
            latest_period=d.get("latest_period"),
            previous_value=d.get("previous_value"),
            previous_period=d.get("previous_period"),
            change_direction=d.get("change_direction", d.get("historical_direction")),
            absolute_change=d.get("absolute_change"),
            percent_change=d.get("percent_change"),
            target_value=d.get("target_value"),
            target_variance=d.get("target_variance", d.get("gap")),
            performance_status=perf_status,
            comparison_status=d.get("comparison_status", "comparison_unavailable"),
            freshness_status=freshness_status,
            quality_tier=quality_tier,
            confidence_score=float(d.get("confidence_score", 1.0)),
            evidence_id=d.get("evidence_id"),
        )

    def _evidence_ref_to_dict(self, ref: EvidenceReference) -> Dict[str, Any]:
        return {
            "evidence_id": ref.evidence_id,
            "metric_key": ref.metric_key,
            "period": ref.period,
            "as_of_date": ref.as_of_date.isoformat() if isinstance(ref.as_of_date, (date, datetime)) else str(ref.as_of_date),
            "source_name": ref.source_name,
            "source_type": ref.source_type.value if isinstance(ref.source_type, SourceType) else str(ref.source_type),
            "confidence_score": ref.confidence_score,
            "quality_tier": ref.quality_tier.value if isinstance(ref.quality_tier, QualityTier) else str(ref.quality_tier),
            "freshness_status": ref.freshness_status.value if isinstance(ref.freshness_status, FreshnessStatus) else str(ref.freshness_status),
        }

    def _dict_to_evidence_ref(self, d: Any) -> EvidenceReference:
        if isinstance(d, str):
            return EvidenceReference(
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
            return EvidenceReference(
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
        if isinstance(as_of_raw, str):
            try:
                as_of = date.fromisoformat(as_of_raw.split("T")[0])
            except Exception:
                as_of = date.today()
        elif isinstance(as_of_raw, (date, datetime)):
            as_of = as_of_raw if isinstance(as_of_raw, date) else as_of_raw.date()
        else:
            as_of = date.today()

        return EvidenceReference(
            evidence_id=str(d.get("evidence_id", "")),
            metric_key=str(d.get("metric_key", "")),
            period=str(d.get("period", "")),
            as_of_date=as_of,
            source_name=str(d.get("source_name", "")),
            source_type=SourceType(d.get("source_type", "MANUAL")) if d.get("source_type") in SourceType.__members__.values() else SourceType.MANUAL,
            confidence_score=float(d.get("confidence_score", 1.0)),
            quality_tier=QualityTier(d.get("quality_tier", "VERIFIED")) if d.get("quality_tier") in QualityTier.__members__.values() else QualityTier.VERIFIED,
            freshness_status=FreshnessStatus(d.get("freshness_status", "FRESH")) if d.get("freshness_status") in FreshnessStatus.__members__.values() else FreshnessStatus.FRESH,
        )

    def _to_domain(self, model: CurrentPositionAnalysisModel) -> CurrentPositionAnalysis:
        confidence = ConfidenceAssessment(
            score=model.overall_confidence_score,
            level=model.confidence_level,
            factors=model.confidence_factors.get("factors", {}) if isinstance(model.confidence_factors, dict) else {},
            explanation=model.confidence_factors.get("explanation", "") if isinstance(model.confidence_factors, dict) else "",
        )

        return CurrentPositionAnalysis(
            id=model.id,
            institution_id=model.institution_id,
            organizational_unit_id=model.unit_id,
            analysis_period=model.analysis_period,
            generated_at=model.generated_at,
            key_metrics=[self._dict_to_metric(m) for m in (model.key_metrics or [])],
            strengths=[self._dict_to_finding(f, FindingCategory.STRENGTH) for f in (model.strengths or [])],
            weaknesses=[self._dict_to_finding(f, FindingCategory.WEAKNESS) for f in (model.weaknesses or [])],
            gaps=[self._dict_to_finding(f, FindingCategory.GAP) for f in (model.gaps or [])],
            constraints=[self._dict_to_finding(f, FindingCategory.CONSTRAINT) for f in (model.constraints or [])],
            structural_risks=[self._dict_to_finding(f, FindingCategory.STRUCTURAL_RISK) for f in (model.structural_risks or [])],
            opportunities=[self._dict_to_finding(f, FindingCategory.OPPORTUNITY) for f in (model.opportunities or [])],
            data_gaps=[self._dict_to_finding(f, FindingCategory.DATA_GAP) for f in (model.data_gaps or [])],
            evidence_references=[self._dict_to_evidence_ref(r) for r in (model.evidence_references or [])],
            assumptions=model.assumptions or [],
            overall_confidence=confidence,
            status=model.status,
            created_at=model.created_at,
        )

    def create_analysis(self, analysis: CurrentPositionAnalysis) -> CurrentPositionAnalysis:
        model = CurrentPositionAnalysisModel(
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
            key_metrics=[self._metric_to_dict(m) for m in analysis.key_metrics],
            strengths=[self._finding_to_dict(f) for f in analysis.strengths],
            weaknesses=[self._finding_to_dict(f) for f in analysis.weaknesses],
            gaps=[self._finding_to_dict(f) for f in analysis.gaps],
            constraints=[self._finding_to_dict(f) for f in analysis.constraints],
            structural_risks=[self._finding_to_dict(f) for f in analysis.structural_risks],
            opportunities=[self._finding_to_dict(f) for f in analysis.opportunities],
            data_gaps=[self._finding_to_dict(f) for f in analysis.data_gaps],
            evidence_references=[self._evidence_ref_to_dict(r) for r in analysis.evidence_references],
            assumptions=analysis.assumptions,
            status=analysis.status,
            created_at=analysis.created_at,
        )

        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return self._to_domain(model)

    def get_analysis_by_id(self, analysis_id: str) -> Optional[CurrentPositionAnalysis]:
        stmt = select(CurrentPositionAnalysisModel).where(CurrentPositionAnalysisModel.id == analysis_id)
        model = self.session.scalar(stmt)
        if not model:
            return None
        return self._to_domain(model)

    def list_analyses(
        self,
        institution_id: Optional[str] = None,
        organizational_unit_id: Optional[str] = None,
        analysis_period: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> List[CurrentPositionAnalysis]:
        stmt = select(CurrentPositionAnalysisModel)
        if institution_id:
            stmt = stmt.where(CurrentPositionAnalysisModel.institution_id == institution_id)
        if organizational_unit_id:
            stmt = stmt.where(CurrentPositionAnalysisModel.unit_id == organizational_unit_id)
        if analysis_period:
            stmt = stmt.where(CurrentPositionAnalysisModel.analysis_period == analysis_period)

        stmt = stmt.order_by(desc(CurrentPositionAnalysisModel.generated_at)).offset(skip).limit(limit)
        models = self.session.scalars(stmt).all()
        return [self._to_domain(m) for m in models]

    def count_analyses(
        self,
        institution_id: Optional[str] = None,
        organizational_unit_id: Optional[str] = None,
        analysis_period: Optional[str] = None,
    ) -> int:
        stmt = select(func.count()).select_from(CurrentPositionAnalysisModel)
        if institution_id:
            stmt = stmt.where(CurrentPositionAnalysisModel.institution_id == institution_id)
        if organizational_unit_id:
            stmt = stmt.where(CurrentPositionAnalysisModel.unit_id == organizational_unit_id)
        if analysis_period:
            stmt = stmt.where(CurrentPositionAnalysisModel.analysis_period == analysis_period)

        return self.session.scalar(stmt) or 0
