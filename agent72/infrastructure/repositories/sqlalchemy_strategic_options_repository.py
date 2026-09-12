"""SQLAlchemy 2.0 implementation of IStrategicOptionsRepository."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from agent72.domain.interfaces.strategic_options_repository import IStrategicOptionsRepository
from agent72.domain.models.strategic_options import (
    FeasibilityLevel,
    OptionCategory,
    OptionEvaluation,
    OptionStatus,
    PriorityLevel,
    Scenario,
    ScenarioType,
    StrategicOption,
    StrategicOptionsAnalysis,
)
from agent72.infrastructure.database.models import StrategicOptionsAnalysisModel


class SQLAlchemyStrategicOptionsRepository(IStrategicOptionsRepository):
    """Concrete repository for managing persistent, immutable strategic options snapshots."""

    def __init__(self, session: Session):
        self.session = session

    def _option_to_dict(self, opt: StrategicOption) -> Dict[str, Any]:
        return {
            "id": opt.id,
            "institution_id": opt.institution_id,
            "organizational_unit_id": opt.organizational_unit_id,
            "category": opt.category.value if isinstance(opt.category, OptionCategory) else str(opt.category),
            "title": opt.title,
            "description": opt.description,
            "strategic_rationale": opt.strategic_rationale,
            "addressed_issue_ids": opt.addressed_issue_ids,
            "addressed_risk_ids": opt.addressed_risk_ids,
            "opportunity_ids": opt.opportunity_ids,
            "related_metrics": opt.related_metrics,
            "evidence_ids": opt.evidence_ids,
            "expected_outcomes": opt.expected_outcomes,
            "assumptions": opt.assumptions,
            "dependencies": opt.dependencies,
            "feasibility": opt.feasibility.value if isinstance(opt.feasibility, FeasibilityLevel) else str(opt.feasibility),
            "resource_requirement": opt.resource_requirement,
            "implementation_risk": opt.implementation_risk,
            "confidence": opt.confidence,
            "status": opt.status.value if isinstance(opt.status, OptionStatus) else str(opt.status),
            "trade_offs": opt.trade_offs,
        }

    def _dict_to_option(self, d: Dict[str, Any]) -> StrategicOption:
        return StrategicOption(
            id=d.get("id", ""),
            institution_id=d.get("institution_id", ""),
            organizational_unit_id=d.get("organizational_unit_id"),
            category=OptionCategory(d.get("category", "IMPROVEMENT")),
            title=d.get("title", ""),
            description=d.get("description", ""),
            strategic_rationale=d.get("strategic_rationale", ""),
            addressed_issue_ids=d.get("addressed_issue_ids", []),
            addressed_risk_ids=d.get("addressed_risk_ids", []),
            opportunity_ids=d.get("opportunity_ids", []),
            related_metrics=d.get("related_metrics", []),
            evidence_ids=d.get("evidence_ids", []),
            expected_outcomes=d.get("expected_outcomes", []),
            assumptions=d.get("assumptions", []),
            dependencies=d.get("dependencies", []),
            feasibility=FeasibilityLevel(d.get("feasibility", "MEDIUM")),
            resource_requirement=d.get("resource_requirement", "MEDIUM"),
            implementation_risk=d.get("implementation_risk", "MEDIUM"),
            confidence=float(d.get("confidence", 0.8)),
            status=OptionStatus(d.get("status", "PROPOSED")),
            trade_offs=d.get("trade_offs", []),
        )

    def _scenario_to_dict(self, sc: Scenario) -> Dict[str, Any]:
        return {
            "id": sc.id,
            "option_id": sc.option_id,
            "scenario_type": sc.scenario_type.value if isinstance(sc.scenario_type, ScenarioType) else str(sc.scenario_type),
            "title": sc.title,
            "description": sc.description,
            "assumptions": sc.assumptions,
            "expected_effects": sc.expected_effects,
            "risks": sc.risks,
            "opportunities": sc.opportunities,
            "uncertainty": sc.uncertainty,
            "confidence": sc.confidence,
            "evidence_ids": sc.evidence_ids,
        }

    def _dict_to_scenario(self, d: Dict[str, Any]) -> Scenario:
        return Scenario(
            id=d.get("id", ""),
            option_id=d.get("option_id", ""),
            scenario_type=ScenarioType(d.get("scenario_type", "BASELINE")),
            title=d.get("title", ""),
            description=d.get("description", ""),
            assumptions=d.get("assumptions", []),
            expected_effects=d.get("expected_effects", []),
            risks=d.get("risks", []),
            opportunities=d.get("opportunities", []),
            uncertainty=d.get("uncertainty", "MEDIUM"),
            confidence=float(d.get("confidence", 0.8)),
            evidence_ids=d.get("evidence_ids", []),
        )

    def _eval_to_dict(self, ev: OptionEvaluation) -> Dict[str, Any]:
        return {
            "option_id": ev.option_id,
            "strategic_alignment_score": ev.strategic_alignment_score,
            "impact_score": ev.impact_score,
            "feasibility_score": ev.feasibility_score,
            "resource_efficiency_score": ev.resource_efficiency_score,
            "implementation_risk_score": ev.implementation_risk_score,
            "urgency_score": ev.urgency_score,
            "evidence_strength_score": ev.evidence_strength_score,
            "total_score": ev.total_score,
            "priority_level": ev.priority_level.value if isinstance(ev.priority_level, PriorityLevel) else str(ev.priority_level),
            "trade_offs": ev.trade_offs,
            "rationale": ev.rationale,
        }

    def _dict_to_eval(self, d: Dict[str, Any]) -> OptionEvaluation:
        return OptionEvaluation(
            option_id=d.get("option_id", ""),
            strategic_alignment_score=float(d.get("strategic_alignment_score", 0.0)),
            impact_score=float(d.get("impact_score", 0.0)),
            feasibility_score=float(d.get("feasibility_score", 0.0)),
            resource_efficiency_score=float(d.get("resource_efficiency_score", 0.0)),
            implementation_risk_score=float(d.get("implementation_risk_score", 0.0)),
            urgency_score=float(d.get("urgency_score", 0.0)),
            evidence_strength_score=float(d.get("evidence_strength_score", 0.0)),
            total_score=float(d.get("total_score", 0.0)),
            priority_level=PriorityLevel(d.get("priority_level", "MEDIUM")),
            trade_offs=d.get("trade_offs", []),
            rationale=d.get("rationale", ""),
        )

    def create_analysis(
        self, analysis: StrategicOptionsAnalysis
    ) -> StrategicOptionsAnalysis:
        """Persist a complete immutable strategic options analysis."""
        model = StrategicOptionsAnalysisModel(
            id=analysis.id,
            institution_id=analysis.institution_id,
            unit_id=analysis.organizational_unit_id,
            analysis_period=analysis.analysis_period,
            generated_at=analysis.generated_at,
            strategic_intelligence_analysis_id=analysis.strategic_intelligence_analysis_id,
            options=[self._option_to_dict(o) for o in analysis.options],
            scenarios=[self._scenario_to_dict(s) for s in analysis.scenarios],
            evaluations=[self._eval_to_dict(e) for e in analysis.evaluations],
            prioritized_option_ids=analysis.prioritized_option_ids,
            assumptions=analysis.assumptions,
            uncertainty=analysis.uncertainty,
            data_limitations=analysis.data_limitations,
            decision_support_disclaimer=analysis.decision_support_disclaimer,
            engine_version=analysis.engine_version,
            ai_synthesis_notes=analysis.ai_synthesis_notes,
            status=analysis.status,
            created_at=analysis.created_at,
        )

        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return self._to_domain(model)

    def get_analysis_by_id(
        self, analysis_id: str
    ) -> Optional[StrategicOptionsAnalysis]:
        """Retrieve a specific strategic options snapshot by ID."""
        stmt = select(StrategicOptionsAnalysisModel).where(
            StrategicOptionsAnalysisModel.id == analysis_id
        )
        result = self.session.execute(stmt).scalars().first()
        if not result:
            return None
        return self._to_domain(result)

    def list_analyses(
        self,
        institution_id: Optional[str] = None,
        organizational_unit_id: Optional[str] = None,
        analysis_period: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> List[StrategicOptionsAnalysis]:
        """List historical strategic options analyses with filtering and pagination."""
        stmt = select(StrategicOptionsAnalysisModel)

        if institution_id:
            stmt = stmt.where(StrategicOptionsAnalysisModel.institution_id == institution_id)
        if organizational_unit_id:
            stmt = stmt.where(StrategicOptionsAnalysisModel.unit_id == organizational_unit_id)
        if analysis_period:
            stmt = stmt.where(StrategicOptionsAnalysisModel.analysis_period == analysis_period)

        stmt = stmt.order_by(desc(StrategicOptionsAnalysisModel.generated_at)).offset(skip).limit(limit)
        results = self.session.execute(stmt).scalars().all()
        return [self._to_domain(r) for r in results]

    def count_analyses(
        self,
        institution_id: Optional[str] = None,
        organizational_unit_id: Optional[str] = None,
        analysis_period: Optional[str] = None,
    ) -> int:
        """Count matching strategic options analyses for pagination."""
        stmt = select(func.count(StrategicOptionsAnalysisModel.id))

        if institution_id:
            stmt = stmt.where(StrategicOptionsAnalysisModel.institution_id == institution_id)
        if organizational_unit_id:
            stmt = stmt.where(StrategicOptionsAnalysisModel.unit_id == organizational_unit_id)
        if analysis_period:
            stmt = stmt.where(StrategicOptionsAnalysisModel.analysis_period == analysis_period)

        return self.session.execute(stmt).scalar_one()

    def _to_domain(self, model: StrategicOptionsAnalysisModel) -> StrategicOptionsAnalysis:
        """Convert SQLAlchemy model to pure domain aggregate."""
        options = [self._dict_to_option(o) for o in (model.options or [])]
        scenarios = [self._dict_to_scenario(s) for s in (model.scenarios or [])]
        evaluations = [self._dict_to_eval(e) for e in (model.evaluations or [])]

        return StrategicOptionsAnalysis(
            id=model.id,
            institution_id=model.institution_id,
            organizational_unit_id=model.unit_id,
            analysis_period=model.analysis_period,
            generated_at=model.generated_at,
            strategic_intelligence_analysis_id=model.strategic_intelligence_analysis_id,
            options=options,
            scenarios=scenarios,
            evaluations=evaluations,
            prioritized_option_ids=model.prioritized_option_ids or [],
            assumptions=model.assumptions or [],
            uncertainty=model.uncertainty or {},
            data_limitations=model.data_limitations or [],
            decision_support_disclaimer=model.decision_support_disclaimer,
            engine_version=model.engine_version or "1.0.0",
            ai_synthesis_notes=model.ai_synthesis_notes,
            status=model.status,
            created_at=model.created_at,
        )
