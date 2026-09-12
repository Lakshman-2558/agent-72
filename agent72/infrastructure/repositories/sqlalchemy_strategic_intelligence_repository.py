"""SQLAlchemy 2.0 implementation of IStrategicIntelligenceRepository."""

from datetime import date, datetime
from typing import Any, Dict, List, Optional
from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from agent72.domain.interfaces.strategic_intelligence_repository import IStrategicIntelligenceRepository
from agent72.domain.models.analysis import ConfidenceAssessment
from agent72.domain.models.evidence import (
    FreshnessStatus,
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
from agent72.infrastructure.database.models import StrategicIntelligenceAnalysisModel


class SQLAlchemyStrategicIntelligenceRepository(IStrategicIntelligenceRepository):
    """Concrete repository for managing persistent, immutable strategic intelligence snapshots."""

    def __init__(self, session: Session):
        self.session = session

    def _ref_to_dict(self, ref: EvidenceReference) -> Dict[str, Any]:
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

    def _dict_to_ref(self, d: Any) -> EvidenceReference:
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
        as_of = None
        if as_of_raw and isinstance(as_of_raw, str):
            try:
                as_of = date.fromisoformat(as_of_raw.split("T")[0])
            except Exception:
                as_of = date.today()
        elif isinstance(as_of_raw, (date, datetime)):
            as_of = as_of_raw if isinstance(as_of_raw, date) else as_of_raw.date()
        else:
            as_of = date.today()

        source_type_val = d.get("source_type", "MANUAL")
        source_type = SourceType(source_type_val) if source_type_val in SourceType.__members__.values() else SourceType.MANUAL

        qual_val = d.get("quality_tier", "PROVISIONAL")
        quality_tier = QualityTier(qual_val) if qual_val in QualityTier.__members__.values() else QualityTier.PROVISIONAL

        fresh_val = d.get("freshness_status", "FRESH")
        freshness_status = FreshnessStatus(fresh_val) if fresh_val in FreshnessStatus.__members__.values() else FreshnessStatus.FRESH

        return EvidenceReference(
            evidence_id=str(d.get("evidence_id", "")),
            metric_key=str(d.get("metric_key", "")),
            period=str(d.get("period", "")),
            as_of_date=as_of,
            source_name=str(d.get("source_name", "UNKNOWN")),
            source_type=source_type,
            confidence_score=float(d.get("confidence_score", 0.0)),
            quality_tier=quality_tier,
            freshness_status=freshness_status,
        )

    def _issue_to_dict(self, issue: StrategicIssue) -> Dict[str, Any]:
        return {
            "id": issue.id,
            "category": issue.category.value if isinstance(issue.category, IssueCategory) else str(issue.category),
            "title": issue.title,
            "description": issue.description,
            "severity": issue.severity.value if isinstance(issue.severity, RiskSeverity) else str(issue.severity),
            "impact": issue.impact.value if isinstance(issue.impact, ImpactLevel) else str(issue.impact),
            "likelihood": issue.likelihood.value if isinstance(issue.likelihood, LikelihoodLevel) else str(issue.likelihood),
            "affected_domains": [d.value if isinstance(d, MetricDomain) else str(d) for d in issue.affected_domains],
            "related_metrics": issue.related_metrics,
            "current_position_links": issue.current_position_links,
            "trajectory_links": issue.trajectory_links,
            "evidence_ids": issue.evidence_ids,
            "confidence": issue.confidence,
            "assumptions": issue.assumptions,
            "rationale": issue.rationale,
        }

    def _dict_to_issue(self, d: Dict[str, Any]) -> StrategicIssue:
        return StrategicIssue(
            id=d.get("id", ""),
            category=IssueCategory(d.get("category", "STRATEGIC_ISSUE")),
            title=d.get("title", ""),
            description=d.get("description", ""),
            severity=RiskSeverity(d.get("severity", "MEDIUM")),
            impact=ImpactLevel(d.get("impact", "MEDIUM")),
            likelihood=LikelihoodLevel(d.get("likelihood", "MEDIUM")),
            affected_domains=[MetricDomain(dom) for dom in d.get("affected_domains", [])],
            related_metrics=d.get("related_metrics", []),
            current_position_links=d.get("current_position_links", []),
            trajectory_links=d.get("trajectory_links", []),
            evidence_ids=d.get("evidence_ids", []),
            confidence=float(d.get("confidence", 0.8)),
            assumptions=d.get("assumptions", []),
            rationale=d.get("rationale", ""),
        )

    def _risk_to_dict(self, r: RiskSignal) -> Dict[str, Any]:
        return {
            "id": r.id,
            "title": r.title,
            "description": r.description,
            "severity": r.severity.value if isinstance(r.severity, RiskSeverity) else str(r.severity),
            "impact": r.impact.value if isinstance(r.impact, ImpactLevel) else str(r.impact),
            "likelihood": r.likelihood.value if isinstance(r.likelihood, LikelihoodLevel) else str(r.likelihood),
            "risk_score": r.risk_score,
            "scoring_factors": r.scoring_factors,
            "affected_domains": [d.value if isinstance(d, MetricDomain) else str(d) for d in r.affected_domains],
            "related_metrics": r.related_metrics,
            "supporting_indicators": r.supporting_indicators,
            "correlation_vs_causation_note": r.correlation_vs_causation_note,
            "evidence_ids": r.evidence_ids,
            "confidence": r.confidence,
            "uncertainty_level": r.uncertainty_level.value if isinstance(r.uncertainty_level, UncertaintyLevel) else str(r.uncertainty_level),
            "rationale": r.rationale,
        }

    def _dict_to_risk(self, d: Dict[str, Any]) -> RiskSignal:
        return RiskSignal(
            id=d.get("id", ""),
            title=d.get("title", ""),
            description=d.get("description", ""),
            severity=RiskSeverity(d.get("severity", "MEDIUM")),
            impact=ImpactLevel(d.get("impact", "MEDIUM")),
            likelihood=LikelihoodLevel(d.get("likelihood", "MEDIUM")),
            risk_score=float(d.get("risk_score", 0.5)),
            scoring_factors=d.get("scoring_factors", {}),
            affected_domains=[MetricDomain(dom) for dom in d.get("affected_domains", [])],
            related_metrics=d.get("related_metrics", []),
            supporting_indicators=d.get("supporting_indicators", []),
            correlation_vs_causation_note=d.get("correlation_vs_causation_note", ""),
            evidence_ids=d.get("evidence_ids", []),
            confidence=float(d.get("confidence", 0.8)),
            uncertainty_level=UncertaintyLevel(d.get("uncertainty_level", "MEDIUM")),
            rationale=d.get("rationale", ""),
        )

    def _constraint_to_dict(self, c: ConstraintSignal) -> Dict[str, Any]:
        return {
            "id": c.id,
            "title": c.title,
            "description": c.description,
            "constraint_type": c.constraint_type,
            "severity": c.severity.value if isinstance(c.severity, RiskSeverity) else str(c.severity),
            "affected_domains": [d.value if isinstance(d, MetricDomain) else str(d) for d in c.affected_domains],
            "related_metrics": c.related_metrics,
            "persistence": c.persistence,
            "evidence_ids": c.evidence_ids,
            "confidence": c.confidence,
            "limitations_note": c.limitations_note,
            "rationale": c.rationale,
        }

    def _dict_to_constraint(self, d: Dict[str, Any]) -> ConstraintSignal:
        return ConstraintSignal(
            id=d.get("id", ""),
            title=d.get("title", ""),
            description=d.get("description", ""),
            constraint_type=d.get("constraint_type", "CAPACITY"),
            severity=RiskSeverity(d.get("severity", "MEDIUM")),
            affected_domains=[MetricDomain(dom) for dom in d.get("affected_domains", [])],
            related_metrics=d.get("related_metrics", []),
            persistence=d.get("persistence", "MULTI_PERIOD"),
            evidence_ids=d.get("evidence_ids", []),
            confidence=float(d.get("confidence", 0.8)),
            limitations_note=d.get("limitations_note"),
            rationale=d.get("rationale", ""),
        )

    def _opp_to_dict(self, o: OpportunitySignal) -> Dict[str, Any]:
        return {
            "id": o.id,
            "title": o.title,
            "description": o.description,
            "opportunity_type": o.opportunity_type,
            "potential_impact": o.potential_impact.value if isinstance(o.potential_impact, ImpactLevel) else str(o.potential_impact),
            "urgency": o.urgency.value if isinstance(o.urgency, LikelihoodLevel) else str(o.urgency),
            "affected_domains": [d.value if isinstance(d, MetricDomain) else str(d) for d in o.affected_domains],
            "related_metrics": o.related_metrics,
            "evidence_ids": o.evidence_ids,
            "confidence": o.confidence,
            "interpretation": o.interpretation,
            "rationale": o.rationale,
        }

    def _dict_to_opp(self, d: Dict[str, Any]) -> OpportunitySignal:
        return OpportunitySignal(
            id=d.get("id", ""),
            title=d.get("title", ""),
            description=d.get("description", ""),
            opportunity_type=d.get("opportunity_type", "GROWTH"),
            potential_impact=ImpactLevel(d.get("potential_impact", "MEDIUM")),
            urgency=LikelihoodLevel(d.get("urgency", "MEDIUM")),
            affected_domains=[MetricDomain(dom) for dom in d.get("affected_domains", [])],
            related_metrics=d.get("related_metrics", []),
            evidence_ids=d.get("evidence_ids", []),
            confidence=float(d.get("confidence", 0.8)),
            interpretation=d.get("interpretation", ""),
            rationale=d.get("rationale", ""),
        )

    def _external_to_dict(self, ext: ExternalFactor) -> Dict[str, Any]:
        return {
            "id": ext.id,
            "factor_name": ext.factor_name,
            "category": ext.category.value if isinstance(ext.category, ExternalFactorCategory) else str(ext.category),
            "direction_impact": ext.direction_impact,
            "description": ext.description,
            "affected_domains": [d.value if isinstance(d, MetricDomain) else str(d) for d in ext.affected_domains],
            "evidence_ids": ext.evidence_ids,
            "confidence": ext.confidence,
            "freshness": ext.freshness.value if isinstance(ext.freshness, FreshnessStatus) else str(ext.freshness),
            "rationale": ext.rationale,
        }

    def _dict_to_external(self, d: Dict[str, Any]) -> ExternalFactor:
        return ExternalFactor(
            id=d.get("id", ""),
            factor_name=d.get("factor_name", ""),
            category=ExternalFactorCategory(d.get("category", "MARKET_SHIFT")),
            direction_impact=d.get("direction_impact", "NEUTRAL"),
            description=d.get("description", ""),
            affected_domains=[MetricDomain(dom) for dom in d.get("affected_domains", [])],
            evidence_ids=d.get("evidence_ids", []),
            confidence=float(d.get("confidence", 0.8)),
            freshness=FreshnessStatus(d.get("freshness", "FRESH")),
            rationale=d.get("rationale", ""),
        )

    def _priority_to_dict(self, p: StrategicPrioritySignal) -> Dict[str, Any]:
        return {
            "id": p.id,
            "issue_id": p.issue_id,
            "title": p.title,
            "category": p.category.value if isinstance(p.category, IssueCategory) else str(p.category),
            "priority_level": p.priority_level,
            "priority_score": p.priority_score,
            "scoring_factors": p.scoring_factors,
            "rationale": p.rationale,
        }

    def _dict_to_priority(self, d: Dict[str, Any]) -> StrategicPrioritySignal:
        return StrategicPrioritySignal(
            id=d.get("id", ""),
            issue_id=d.get("issue_id", ""),
            title=d.get("title", ""),
            category=IssueCategory(d.get("category", "STRATEGIC_ISSUE")),
            priority_level=d.get("priority_level", "MEDIUM"),
            priority_score=float(d.get("priority_score", 0.5)),
            scoring_factors=d.get("scoring_factors", {}),
            rationale=d.get("rationale", ""),
        )

    def _to_domain(self, model: StrategicIntelligenceAnalysisModel) -> StrategicIntelligenceAnalysis:
        return StrategicIntelligenceAnalysis(
            id=model.id,
            institution_id=model.institution_id,
            organizational_unit_id=model.unit_id,
            analysis_period=model.analysis_period,
            generated_at=model.generated_at,
            current_position_analysis_id=model.current_position_analysis_id,
            trajectory_analysis_id=model.trajectory_analysis_id,
            overall_confidence=ConfidenceAssessment(
                score=model.overall_confidence_score,
                level=model.confidence_level,
                factors=model.confidence_factors,
                explanation=model.confidence_factors.get("explanation", ""),
            ),
            strategic_issues=[self._dict_to_issue(i) for i in model.strategic_issues],
            risk_signals=[self._dict_to_risk(r) for r in model.risk_signals],
            constraint_signals=[self._dict_to_constraint(c) for c in model.constraint_signals],
            opportunity_signals=[self._dict_to_opp(o) for o in model.opportunity_signals],
            external_factors=[self._dict_to_external(e) for e in model.external_factors],
            strategic_priority_signals=[self._dict_to_priority(p) for p in model.strategic_priority_signals],
            evidence_references=[self._dict_to_ref(r) for r in model.evidence_references],
            uncertainty_summary=model.uncertainty_summary,
            ai_synthesis_notes=model.ai_synthesis_notes,
            assumptions=model.assumptions,
            status=model.status,
        )

    def create_strategic_intelligence_analysis(
        self, analysis: StrategicIntelligenceAnalysis
    ) -> StrategicIntelligenceAnalysis:
        model = StrategicIntelligenceAnalysisModel(
            id=analysis.id,
            institution_id=analysis.institution_id,
            unit_id=analysis.organizational_unit_id,
            analysis_period=analysis.analysis_period,
            generated_at=analysis.generated_at,
            current_position_analysis_id=analysis.current_position_analysis_id,
            trajectory_analysis_id=analysis.trajectory_analysis_id,
            overall_confidence_score=analysis.overall_confidence.score,
            confidence_level=analysis.overall_confidence.level,
            confidence_factors={
                **analysis.overall_confidence.factors,
                "explanation": analysis.overall_confidence.explanation,
            },
            strategic_issues=[self._issue_to_dict(i) for i in analysis.strategic_issues],
            risk_signals=[self._risk_to_dict(r) for r in analysis.risk_signals],
            constraint_signals=[self._constraint_to_dict(c) for c in analysis.constraint_signals],
            opportunity_signals=[self._opp_to_dict(o) for o in analysis.opportunity_signals],
            external_factors=[self._external_to_dict(e) for e in analysis.external_factors],
            strategic_priority_signals=[self._priority_to_dict(p) for p in analysis.strategic_priority_signals],
            evidence_references=[self._ref_to_dict(r) for r in analysis.evidence_references],
            uncertainty_summary=analysis.uncertainty_summary,
            ai_synthesis_notes=analysis.ai_synthesis_notes,
            assumptions=analysis.assumptions,
            status=analysis.status,
        )
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return self._to_domain(model)

    def get_strategic_intelligence_analysis_by_id(
        self, analysis_id: str
    ) -> Optional[StrategicIntelligenceAnalysis]:
        stmt = select(StrategicIntelligenceAnalysisModel).where(
            StrategicIntelligenceAnalysisModel.id == analysis_id
        )
        model = self.session.execute(stmt).scalar_one_or_none()
        if not model:
            return None
        return self._to_domain(model)

    def list_strategic_intelligence_analyses(
        self,
        institution_id: Optional[str] = None,
        organizational_unit_id: Optional[str] = None,
        analysis_period: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> List[StrategicIntelligenceAnalysis]:
        stmt = select(StrategicIntelligenceAnalysisModel)
        if institution_id:
            stmt = stmt.where(StrategicIntelligenceAnalysisModel.institution_id == institution_id)
        if organizational_unit_id is not None:
            stmt = stmt.where(StrategicIntelligenceAnalysisModel.unit_id == organizational_unit_id)
        if analysis_period:
            stmt = stmt.where(StrategicIntelligenceAnalysisModel.analysis_period == analysis_period)

        stmt = stmt.order_by(desc(StrategicIntelligenceAnalysisModel.generated_at)).offset(skip).limit(limit)
        models = self.session.execute(stmt).scalars().all()
        return [self._to_domain(m) for m in models]

    def count_strategic_intelligence_analyses(
        self,
        institution_id: Optional[str] = None,
        organizational_unit_id: Optional[str] = None,
        analysis_period: Optional[str] = None,
    ) -> int:
        stmt = select(func.count(StrategicIntelligenceAnalysisModel.id))
        if institution_id:
            stmt = stmt.where(StrategicIntelligenceAnalysisModel.institution_id == institution_id)
        if organizational_unit_id is not None:
            stmt = stmt.where(StrategicIntelligenceAnalysisModel.unit_id == organizational_unit_id)
        if analysis_period:
            stmt = stmt.where(StrategicIntelligenceAnalysisModel.analysis_period == analysis_period)

        return self.session.execute(stmt).scalar_one() or 0
