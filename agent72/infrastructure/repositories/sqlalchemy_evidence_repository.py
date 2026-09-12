"""SQLAlchemy implementation of IEvidenceRepository."""

import uuid
from datetime import date
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session

from agent72.domain.interfaces.evidence_repository import IEvidenceRepository
from agent72.domain.models.evidence import (
    InstitutionalEvidence,
    MetricDefinition,
    MetricDomain,
    MetricDirection,
    QualityTier,
    SourceType,
    IngestionBatchLog,
)
from agent72.infrastructure.database.models import (
    InstitutionalEvidenceModel,
    MetricDefinitionModel,
    IngestionBatchLogModel,
)


class SQLAlchemyEvidenceRepository(IEvidenceRepository):
    """Data-access repository for institutional metrics, time-series evidence, and audit logs."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def _def_to_domain(self, model: MetricDefinitionModel) -> MetricDefinition:
        direction_val = getattr(model, "direction", "HIGHER_IS_BETTER") or "HIGHER_IS_BETTER"
        return MetricDefinition(
            id=model.id,
            metric_key=model.metric_key,
            name=model.name,
            domain=MetricDomain(model.domain),
            direction=MetricDirection(direction_val),
            default_unit=model.default_unit,
            description=model.description,
            created_at=model.created_at,
        )

    def _evidence_to_domain(self, model: InstitutionalEvidenceModel) -> InstitutionalEvidence:
        return InstitutionalEvidence(
            id=model.id,
            institution_id=model.institution_id,
            unit_id=model.unit_id,
            metric_key=model.metric_key,
            domain=MetricDomain(model.domain),
            numeric_value=model.numeric_value,
            text_value=model.text_value,
            unit=model.unit,
            period=model.period,
            period_start=model.period_start,
            period_end=model.period_end,
            as_of_date=model.as_of_date,
            captured_at=model.captured_at,
            source_type=SourceType(model.source_type),
            source_name=model.source_name,
            source_reference=model.source_reference,
            confidence_score=model.confidence_score,
            quality_tier=QualityTier(model.quality_tier),
            is_stale=model.is_stale,
            external_record_id=model.external_record_id,
            idempotency_key=model.idempotency_key,
            ingestion_batch_id=model.ingestion_batch_id,
        )

    def _batch_log_to_domain(self, model: IngestionBatchLogModel) -> IngestionBatchLog:
        return IngestionBatchLog(
            id=model.id,
            batch_id=model.batch_id,
            source_name=model.source_name,
            received_count=model.received_count,
            inserted_count=model.inserted_count,
            duplicate_count=model.duplicate_count,
            rejected_count=model.rejected_count,
            error_summary=model.error_summary,
            created_at=model.created_at,
        )

    def create_metric_definition(self, definition: MetricDefinition) -> MetricDefinition:
        def_id = definition.id or str(uuid.uuid4())
        dir_val = definition.direction.value if isinstance(definition.direction, MetricDirection) else str(definition.direction)
        model = MetricDefinitionModel(
            id=def_id,
            metric_key=definition.metric_key,
            name=definition.name,
            domain=definition.domain.value,
            direction=dir_val,
            default_unit=definition.default_unit,
            description=definition.description,
        )
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return self._def_to_domain(model)

    def get_metric_definition(self, metric_key: str) -> Optional[MetricDefinition]:
        stmt = select(MetricDefinitionModel).where(MetricDefinitionModel.metric_key == metric_key)
        model = self.session.execute(stmt).scalar_one_or_none()
        if not model:
            return None
        return self._def_to_domain(model)

    def list_metric_definitions(self, domain: Optional[MetricDomain] = None) -> List[MetricDefinition]:
        stmt = select(MetricDefinitionModel).order_by(MetricDefinitionModel.metric_key)
        if domain:
            stmt = stmt.where(MetricDefinitionModel.domain == domain.value)
        models = self.session.execute(stmt).scalars().all()
        return [self._def_to_domain(m) for m in models]

    def find_existing_evidence(self, institution_id: str, idempotency_key: str) -> Optional[InstitutionalEvidence]:
        stmt = (
            select(InstitutionalEvidenceModel)
            .where(
                InstitutionalEvidenceModel.institution_id == institution_id,
                InstitutionalEvidenceModel.idempotency_key == idempotency_key,
            )
            .limit(1)
        )
        model = self.session.execute(stmt).scalar_one_or_none()
        if not model:
            return None
        return self._evidence_to_domain(model)

    def record_evidence(self, evidence: InstitutionalEvidence) -> InstitutionalEvidence:
        ev_id = evidence.id or str(uuid.uuid4())
        model = InstitutionalEvidenceModel(
            id=ev_id,
            institution_id=evidence.institution_id,
            unit_id=evidence.unit_id,
            metric_key=evidence.metric_key,
            domain=evidence.domain.value,
            numeric_value=evidence.numeric_value,
            text_value=evidence.text_value,
            unit=evidence.unit,
            period=evidence.period,
            period_start=evidence.period_start,
            period_end=evidence.period_end,
            as_of_date=evidence.as_of_date,
            captured_at=evidence.captured_at,
            source_type=evidence.source_type.value,
            source_name=evidence.source_name,
            source_reference=evidence.source_reference,
            confidence_score=evidence.confidence_score,
            quality_tier=evidence.quality_tier.value,
            is_stale=evidence.is_stale,
            external_record_id=evidence.external_record_id,
            idempotency_key=evidence.idempotency_key,
            ingestion_batch_id=evidence.ingestion_batch_id,
        )
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return self._evidence_to_domain(model)

    def record_evidence_batch(self, evidence_items: List[InstitutionalEvidence]) -> List[InstitutionalEvidence]:
        models = []
        for ev in evidence_items:
            ev_id = ev.id or str(uuid.uuid4())
            model = InstitutionalEvidenceModel(
                id=ev_id,
                institution_id=ev.institution_id,
                unit_id=ev.unit_id,
                metric_key=ev.metric_key,
                domain=ev.domain.value,
                numeric_value=ev.numeric_value,
                text_value=ev.text_value,
                unit=ev.unit,
                period=ev.period,
                period_start=ev.period_start,
                period_end=ev.period_end,
                as_of_date=ev.as_of_date,
                captured_at=ev.captured_at,
                source_type=ev.source_type.value,
                source_name=ev.source_name,
                source_reference=ev.source_reference,
                confidence_score=ev.confidence_score,
                quality_tier=ev.quality_tier.value,
                is_stale=ev.is_stale,
                external_record_id=ev.external_record_id,
                idempotency_key=ev.idempotency_key,
                ingestion_batch_id=ev.ingestion_batch_id,
            )
            models.append(model)

        self.session.add_all(models)
        self.session.commit()
        for m in models:
            self.session.refresh(m)
        return [self._evidence_to_domain(m) for m in models]

    def query_evidence(
        self,
        institution_id: str,
        unit_id: Optional[str] = None,
        metric_key: Optional[str] = None,
        domain: Optional[MetricDomain] = None,
        period: Optional[str] = None,
        as_of_date_start: Optional[date] = None,
        as_of_date_end: Optional[date] = None,
        source_type: Optional[SourceType] = None,
        source_name: Optional[str] = None,
        quality_tier: Optional[QualityTier] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> List[InstitutionalEvidence]:
        stmt = (
            select(InstitutionalEvidenceModel)
            .where(InstitutionalEvidenceModel.institution_id == institution_id)
            .order_by(InstitutionalEvidenceModel.period.desc(), InstitutionalEvidenceModel.as_of_date.desc())
            .offset(skip)
            .limit(limit)
        )

        if unit_id:
            stmt = stmt.where(InstitutionalEvidenceModel.unit_id == unit_id)
        if metric_key:
            stmt = stmt.where(InstitutionalEvidenceModel.metric_key == metric_key)
        if domain:
            stmt = stmt.where(InstitutionalEvidenceModel.domain == domain.value)
        if period:
            stmt = stmt.where(InstitutionalEvidenceModel.period == period)
        if as_of_date_start:
            stmt = stmt.where(InstitutionalEvidenceModel.as_of_date >= as_of_date_start)
        if as_of_date_end:
            stmt = stmt.where(InstitutionalEvidenceModel.as_of_date <= as_of_date_end)
        if source_type:
            stmt = stmt.where(InstitutionalEvidenceModel.source_type == source_type.value)
        if source_name:
            stmt = stmt.where(InstitutionalEvidenceModel.source_name == source_name)
        if quality_tier:
            stmt = stmt.where(InstitutionalEvidenceModel.quality_tier == quality_tier.value)

        models = self.session.execute(stmt).scalars().all()
        return [self._evidence_to_domain(m) for m in models]

    def get_latest_evidence(
        self,
        institution_id: str,
        metric_key: str,
        unit_id: Optional[str] = None,
    ) -> Optional[InstitutionalEvidence]:
        stmt = (
            select(InstitutionalEvidenceModel)
            .where(
                InstitutionalEvidenceModel.institution_id == institution_id,
                InstitutionalEvidenceModel.metric_key == metric_key,
            )
            .order_by(InstitutionalEvidenceModel.period.desc(), InstitutionalEvidenceModel.as_of_date.desc())
            .limit(1)
        )
        if unit_id:
            stmt = stmt.where(InstitutionalEvidenceModel.unit_id == unit_id)

        model = self.session.execute(stmt).scalar_one_or_none()
        if not model:
            return None
        return self._evidence_to_domain(model)

    def get_historical_series(
        self,
        institution_id: str,
        metric_key: str,
        unit_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> List[InstitutionalEvidence]:
        """Returns chronological time series sorted ascending by period."""
        stmt = (
            select(InstitutionalEvidenceModel)
            .where(
                InstitutionalEvidenceModel.institution_id == institution_id,
                InstitutionalEvidenceModel.metric_key == metric_key,
            )
            .order_by(InstitutionalEvidenceModel.period.asc(), InstitutionalEvidenceModel.as_of_date.asc())
            .offset(skip)
            .limit(limit)
        )
        if unit_id:
            stmt = stmt.where(InstitutionalEvidenceModel.unit_id == unit_id)

        models = self.session.execute(stmt).scalars().all()
        return [self._evidence_to_domain(m) for m in models]

    def get_evidence_by_domain(
        self,
        institution_id: str,
        domain: MetricDomain,
        period: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> List[InstitutionalEvidence]:
        stmt = (
            select(InstitutionalEvidenceModel)
            .where(
                InstitutionalEvidenceModel.institution_id == institution_id,
                InstitutionalEvidenceModel.domain == domain.value,
            )
            .order_by(InstitutionalEvidenceModel.metric_key.asc(), InstitutionalEvidenceModel.period.desc())
            .offset(skip)
            .limit(limit)
        )
        if period:
            stmt = stmt.where(InstitutionalEvidenceModel.period == period)

        models = self.session.execute(stmt).scalars().all()
        return [self._evidence_to_domain(m) for m in models]

    def record_batch_log(self, batch_log: IngestionBatchLog) -> IngestionBatchLog:
        log_id = batch_log.id or str(uuid.uuid4())
        model = IngestionBatchLogModel(
            id=log_id,
            batch_id=batch_log.batch_id,
            source_name=batch_log.source_name,
            received_count=batch_log.received_count,
            inserted_count=batch_log.inserted_count,
            duplicate_count=batch_log.duplicate_count,
            rejected_count=batch_log.rejected_count,
            error_summary=batch_log.error_summary,
        )
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return self._batch_log_to_domain(model)

    def get_batch_log(self, batch_id: str) -> Optional[IngestionBatchLog]:
        stmt = select(IngestionBatchLogModel).where(IngestionBatchLogModel.batch_id == batch_id)
        model = self.session.execute(stmt).scalar_one_or_none()
        if not model:
            return None
        return self._batch_log_to_domain(model)

    def find_by_batch_id(self, batch_id: str) -> List[InstitutionalEvidence]:
        stmt = (
            select(InstitutionalEvidenceModel)
            .where(InstitutionalEvidenceModel.ingestion_batch_id == batch_id)
            .order_by(InstitutionalEvidenceModel.captured_at.asc())
        )
        models = self.session.execute(stmt).scalars().all()
        return [self._evidence_to_domain(m) for m in models]
