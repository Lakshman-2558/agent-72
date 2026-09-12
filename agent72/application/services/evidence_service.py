"""Evidence and Institutional Metrics Application Service."""

import uuid
from datetime import date
from typing import List, Optional
from agent72.core.config import settings
from agent72.domain.interfaces.evidence_repository import IEvidenceRepository
from agent72.domain.interfaces.organization_repository import IOrganizationRepository
from agent72.domain.models.evidence import (
    InstitutionalEvidence,
    MetricDefinition,
    MetricDomain,
    QualityTier,
    SourceType,
    IngestionBatchLog,
)
from agent72.application.dtos.evidence_dto import (
    EvidenceIngestionDTO,
    EvidenceBatchIngestionDTO,
    EvidenceResponseDTO,
    EvidenceListResponseDTO,
    BatchIngestionResultDTO,
    IngestionErrorDTO,
    FreshnessInfoDTO,
    HistoricalSeriesItemDTO,
    HistoricalSeriesResponseDTO,
    MetricDefinitionCreateDTO,
    MetricDefinitionResponseDTO,
    MetricDefinitionListResponseDTO,
)
from agent72.application.services.normalization import EvidenceNormalizer
from agent72.application.services.idempotency import IdempotencyService
from agent72.application.services.freshness import EvidenceFreshnessService
from agent72.core.exceptions import EntityNotFoundException, ValidationError
from agent72.core.logging import get_logger

logger = get_logger(__name__)


class EvidenceService:
    """Service orchestrating metric definitions, canonical normalization, idempotency, and evidence ingestion."""

    def __init__(
        self,
        evidence_repository: IEvidenceRepository,
        organization_repository: Optional[IOrganizationRepository] = None,
        freshness_service: Optional[EvidenceFreshnessService] = None,
    ) -> None:
        self.evidence_repo = evidence_repository
        self.org_repo = organization_repository
        self.freshness_service = freshness_service or EvidenceFreshnessService()

    def _def_to_dto(self, model: MetricDefinition) -> MetricDefinitionResponseDTO:
        return MetricDefinitionResponseDTO(
            id=model.id or "",
            metric_key=model.metric_key,
            name=model.name,
            domain=model.domain,
            direction=model.direction,
            default_unit=model.default_unit,
            description=model.description,
            created_at=model.created_at,
        )

    def _evidence_to_dto(self, ev: InstitutionalEvidence) -> EvidenceResponseDTO:
        # Dynamically evaluate freshness if not already evaluated
        if not ev.freshness:
            self.freshness_service.enrich_evidence(ev)

        freshness_dto = None
        if ev.freshness:
            freshness_dto = FreshnessInfoDTO(
                status=ev.freshness.status,
                age_days=ev.freshness.age_days,
                threshold_days=ev.freshness.threshold_days,
                as_of_date=ev.freshness.as_of_date,
            )

        return EvidenceResponseDTO(
            id=ev.id or "",
            institution_id=ev.institution_id,
            unit_id=ev.unit_id,
            metric_key=ev.metric_key,
            domain=ev.domain,
            numeric_value=ev.numeric_value,
            text_value=ev.text_value,
            unit=ev.unit,
            period=ev.period,
            period_start=ev.period_start,
            period_end=ev.period_end,
            as_of_date=ev.as_of_date,
            captured_at=ev.captured_at,
            source_type=ev.source_type,
            source_name=ev.source_name,
            source_reference=ev.source_reference,
            confidence_score=ev.confidence_score,
            quality_tier=ev.quality_tier,
            is_stale=ev.is_stale,
            external_record_id=ev.external_record_id,
            idempotency_key=ev.idempotency_key,
            ingestion_batch_id=ev.ingestion_batch_id,
            freshness=freshness_dto,
        )

    def create_metric_definition(self, dto: MetricDefinitionCreateDTO) -> MetricDefinitionResponseDTO:
        normalized_key = EvidenceNormalizer.normalize_metric_key(dto.metric_key)
        existing = self.evidence_repo.get_metric_definition(normalized_key)
        if existing:
            raise ValidationError(f"Metric definition with key '{normalized_key}' already exists.")

        domain_def = MetricDefinition(
            metric_key=normalized_key,
            name=dto.name.strip(),
            domain=dto.domain,
            direction=dto.direction,
            default_unit=EvidenceNormalizer.normalize_unit(dto.default_unit),
            description=dto.description.strip() if dto.description else None,
        )
        created = self.evidence_repo.create_metric_definition(domain_def)
        logger.info(f"Registered metric definition '{created.name}' [{created.metric_key}]")
        return self._def_to_dto(created)

    def get_metric_definition(self, metric_key: str) -> MetricDefinitionResponseDTO:
        normalized_key = EvidenceNormalizer.normalize_metric_key(metric_key)
        defn = self.evidence_repo.get_metric_definition(normalized_key)
        if not defn:
            raise EntityNotFoundException("MetricDefinition", metric_key)
        return self._def_to_dto(defn)

    def list_metric_definitions(self, domain: Optional[MetricDomain] = None) -> MetricDefinitionListResponseDTO:
        defs = self.evidence_repo.list_metric_definitions(domain=domain)
        items = [self._def_to_dto(d) for d in defs]
        return MetricDefinitionListResponseDTO(total=len(items), items=items)

    def _validate_and_normalize_evidence_item(
        self,
        dto: EvidenceIngestionDTO,
        auto_register_metrics: bool = False,
    ) -> InstitutionalEvidence:
        """Validates scope, normalizes fields, verifies metric definitions, and constructs domain entity."""
        # 1. Normalize fields
        norm_metric_key = EvidenceNormalizer.normalize_metric_key(dto.metric_key)
        norm_domain = EvidenceNormalizer.normalize_domain(dto.domain)
        norm_unit = EvidenceNormalizer.normalize_unit(dto.unit)
        norm_period = EvidenceNormalizer.normalize_academic_period(dto.period)
        norm_num_val, norm_txt_val = EvidenceNormalizer.validate_and_normalize_value(
            dto.numeric_value, dto.text_value
        )

        # 2. Verify Institution scope
        if self.org_repo:
            inst = self.org_repo.get_institution_by_id(dto.institution_id)
            if not inst:
                raise ValidationError(f"Institution with ID '{dto.institution_id}' does not exist.")

            if dto.unit_id:
                unit = self.org_repo.get_unit_by_id(dto.unit_id)
                if not unit:
                    raise ValidationError(f"Organizational unit with ID '{dto.unit_id}' does not exist.")
                if unit.institution_id != dto.institution_id:
                    raise ValidationError(
                        f"Unit '{dto.unit_id}' does not belong to institution '{dto.institution_id}'."
                    )

        # 3. Check Metric Definition in catalog (Rule #3: No silent metric creation)
        metric_def = self.evidence_repo.get_metric_definition(norm_metric_key)
        if not metric_def:
            if auto_register_metrics:
                if not dto.display_name or not dto.display_name.strip():
                    raise ValidationError(
                        f"Metric '{norm_metric_key}' does not exist. Auto-registration requires 'display_name'."
                    )
                # Register definition with explicit metadata
                from agent72.domain.models.evidence import MetricDirection
                auto_dir = dto.direction or MetricDirection.HIGHER_IS_BETTER
                new_def = MetricDefinition(
                    metric_key=norm_metric_key,
                    name=dto.display_name.strip(),
                    domain=norm_domain,
                    direction=auto_dir,
                    default_unit=norm_unit,
                    description=dto.metric_description or f"Auto-registered indicator for {dto.display_name}",
                )
                self.evidence_repo.create_metric_definition(new_def)
                logger.info(f"Auto-registered metric definition '{new_def.name}' [{norm_metric_key}]")
            else:
                raise ValidationError(
                    f"Metric definition '{norm_metric_key}' is not registered in catalog. Register metric first or provide complete auto-registration metadata."
                )

        # 4. Generate deterministic Idempotency Key (Rule #1: Safe fingerprint)
        idempotency_key = IdempotencyService.generate_idempotency_key(
            source_name=dto.source_name,
            external_record_id=dto.external_record_id,
            institution_id=dto.institution_id,
            unit_id=dto.unit_id,
            metric_key=norm_metric_key,
            numeric_value=norm_num_val,
            text_value=norm_txt_val,
            period=norm_period,
            as_of_date=dto.as_of_date,
        )

        domain_ev = InstitutionalEvidence(
            institution_id=dto.institution_id,
            unit_id=dto.unit_id,
            metric_key=norm_metric_key,
            domain=norm_domain,
            numeric_value=norm_num_val,
            text_value=norm_txt_val,
            unit=norm_unit,
            period=norm_period,
            period_start=dto.period_start,
            period_end=dto.period_end,
            as_of_date=dto.as_of_date,
            source_type=dto.source_type,
            source_name=dto.source_name.strip(),
            source_reference=dto.source_reference.strip() if dto.source_reference else None,
            confidence_score=dto.confidence_score,
            quality_tier=dto.quality_tier,
            external_record_id=dto.external_record_id.strip() if dto.external_record_id else None,
            idempotency_key=idempotency_key,
        )
        domain_ev.validate_provenance()
        return domain_ev

    def ingest_evidence(
        self,
        dto: EvidenceIngestionDTO,
        auto_register_metrics: bool = False,
    ) -> EvidenceResponseDTO:
        """Ingests a single evidence item with normalization and idempotency check."""
        domain_ev = self._validate_and_normalize_evidence_item(dto, auto_register_metrics=auto_register_metrics)

        # Idempotency check: if identical record exists, return it without duplicate insertion
        existing = self.evidence_repo.find_existing_evidence(domain_ev.institution_id, domain_ev.idempotency_key or "")
        if existing:
            logger.info(
                f"Idempotent duplicate detected for metric '{domain_ev.metric_key}' [{domain_ev.idempotency_key}]. Returning existing record."
            )
            return self._evidence_to_dto(existing)

        saved = self.evidence_repo.record_evidence(domain_ev)
        logger.info(f"Ingested evidence '{saved.metric_key}' for institution '{saved.institution_id}' (period: {saved.period})")
        return self._evidence_to_dto(saved)

    def ingest_batch(self, batch_dto: EvidenceBatchIngestionDTO) -> BatchIngestionResultDTO:
        """
        Processes a bulk ingestion batch with partial failure handling, idempotency,
        and audit log recording (Rule #2: Link batch_id to evidence).
        """
        batch_id = batch_dto.batch_id or str(uuid.uuid4())
        total = len(batch_dto.items)
        inserted_items: List[InstitutionalEvidence] = []
        result_items: List[InstitutionalEvidence] = []
        duplicate_count = 0
        rejected_count = 0
        errors: List[IngestionErrorDTO] = []
        seen_idempotency_in_batch = set()

        if batch_dto.items:
            first_item = batch_dto.items[0]
            source_name = first_item.get("source_name", "Unknown") if isinstance(first_item, dict) else getattr(first_item, "source_name", "Unknown")
        else:
            source_name = "Unknown"

        for idx, raw_item in enumerate(batch_dto.items):
            try:
                if isinstance(raw_item, dict):
                    item_dto = EvidenceIngestionDTO.model_validate(raw_item)
                else:
                    item_dto = raw_item

                domain_ev = self._validate_and_normalize_evidence_item(
                    item_dto, auto_register_metrics=batch_dto.auto_register_metrics
                )
                domain_ev.ingestion_batch_id = batch_id

                # Intra-batch deduplication
                if domain_ev.idempotency_key in seen_idempotency_in_batch:
                    duplicate_count += 1
                    continue

                # Persistent storage deduplication
                existing = self.evidence_repo.find_existing_evidence(
                    domain_ev.institution_id, domain_ev.idempotency_key or ""
                )
                if existing:
                    duplicate_count += 1
                    result_items.append(existing)
                    seen_idempotency_in_batch.add(domain_ev.idempotency_key)
                    continue

                seen_idempotency_in_batch.add(domain_ev.idempotency_key)
                inserted_items.append(domain_ev)

            except Exception as e:
                rejected_count += 1
                error_msg = str(e)
                metric_key = raw_item.get("metric_key", "unknown") if isinstance(raw_item, dict) else getattr(raw_item, "metric_key", "unknown")
                errors.append(
                    IngestionErrorDTO(
                        index=idx,
                        metric_key=metric_key,
                        error=error_msg,
                    )
                )

        # Bulk-insert all validated non-duplicate records
        if inserted_items:
            persisted = self.evidence_repo.record_evidence_batch(inserted_items)
            result_items.extend(persisted)

        # Auditability (Rule #2: Ingestion batch audit log)
        error_summary = "; ".join([f"[{err.index}] {err.metric_key}: {err.error}" for err in errors[:5]])
        if len(errors) > 5:
            error_summary += f"; ... and {len(errors) - 5} more"

        batch_log = IngestionBatchLog(
            batch_id=batch_id,
            source_name=source_name,
            received_count=total,
            inserted_count=len(inserted_items),
            duplicate_count=duplicate_count,
            rejected_count=rejected_count,
            error_summary=error_summary if errors else None,
        )
        self.evidence_repo.record_batch_log(batch_log)

        logger.info(
            f"Batch {batch_id} complete: total={total}, inserted={len(inserted_items)}, "
            f"duplicates={duplicate_count}, rejected={rejected_count}"
        )

        return BatchIngestionResultDTO(
            batch_id=batch_id,
            total=total,
            inserted=len(inserted_items),
            duplicates=duplicate_count,
            rejected=rejected_count,
            errors=errors,
            items=[self._evidence_to_dto(r) for r in result_items],
        )

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
    ) -> EvidenceListResponseDTO:
        # Rule #6: Enforce pagination bounds
        safe_limit = max(1, min(limit, settings.MAX_PAGE_SIZE))
        safe_skip = max(0, skip)

        records = self.evidence_repo.query_evidence(
            institution_id=institution_id,
            unit_id=unit_id,
            metric_key=EvidenceNormalizer.normalize_metric_key(metric_key) if metric_key else None,
            domain=domain,
            period=period,
            as_of_date_start=as_of_date_start,
            as_of_date_end=as_of_date_end,
            source_type=source_type,
            source_name=source_name,
            quality_tier=quality_tier,
            skip=safe_skip,
            limit=safe_limit,
        )
        items = [self._evidence_to_dto(r) for r in records]
        return EvidenceListResponseDTO(total=len(items), items=items)

    def get_latest_evidence(
        self,
        institution_id: str,
        metric_key: str,
        unit_id: Optional[str] = None,
    ) -> EvidenceResponseDTO:
        norm_key = EvidenceNormalizer.normalize_metric_key(metric_key)
        record = self.evidence_repo.get_latest_evidence(
            institution_id=institution_id, metric_key=norm_key, unit_id=unit_id
        )
        if not record:
            raise EntityNotFoundException("InstitutionalEvidence", f"{institution_id}/{norm_key}")
        return self._evidence_to_dto(record)

    def get_historical_series(
        self,
        institution_id: str,
        metric_key: str,
        unit_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> HistoricalSeriesResponseDTO:
        """Retrieves chronological time-series observations for a metric."""
        norm_key = EvidenceNormalizer.normalize_metric_key(metric_key)
        safe_limit = max(1, min(limit, settings.MAX_PAGE_SIZE))
        safe_skip = max(0, skip)

        records = self.evidence_repo.get_historical_series(
            institution_id=institution_id,
            metric_key=norm_key,
            unit_id=unit_id,
            skip=safe_skip,
            limit=safe_limit,
        )

        domain = records[0].domain if records else MetricDomain.ACADEMIC_PERFORMANCE
        unit = records[0].unit if records else ""

        series_items = []
        for r in records:
            if not r.freshness:
                self.freshness_service.enrich_evidence(r)
            series_items.append(
                HistoricalSeriesItemDTO(
                    period=r.period,
                    numeric_value=r.numeric_value,
                    text_value=r.text_value,
                    as_of_date=r.as_of_date,
                    captured_at=r.captured_at,
                    source_name=r.source_name,
                    confidence_score=r.confidence_score,
                    quality_tier=r.quality_tier,
                    freshness_status=r.freshness.status if r.freshness else FreshnessStatus.FRESH,
                )
            )

        return HistoricalSeriesResponseDTO(
            institution_id=institution_id,
            unit_id=unit_id,
            metric_key=norm_key,
            domain=domain,
            unit=unit,
            total_observations=len(series_items),
            series=series_items,
        )

    def get_batch_audit(self, batch_id: str) -> dict:
        """Retrieves audit log and all associated evidence records for a batch."""
        log = self.evidence_repo.get_batch_log(batch_id)
        if not log:
            raise EntityNotFoundException("IngestionBatchLog", batch_id)

        records = self.evidence_repo.find_by_batch_id(batch_id)
        return {
            "batch_id": log.batch_id,
            "source_name": log.source_name,
            "received_count": log.received_count,
            "inserted_count": log.inserted_count,
            "duplicate_count": log.duplicate_count,
            "rejected_count": log.rejected_count,
            "error_summary": log.error_summary,
            "created_at": log.created_at,
            "records": [self._evidence_to_dto(r) for r in records],
        }
