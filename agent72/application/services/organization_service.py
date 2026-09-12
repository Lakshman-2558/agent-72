"""Organization and Institutional Context Application Service."""

from typing import List, Optional
from agent72.domain.interfaces.organization_repository import IOrganizationRepository
from agent72.domain.models.organization import Institution, OrganizationalUnit
from agent72.application.dtos.organization_dto import (
    InstitutionCreateDTO,
    InstitutionResponseDTO,
    InstitutionListResponseDTO,
    OrganizationalUnitCreateDTO,
    OrganizationalUnitResponseDTO,
    OrganizationalUnitListResponseDTO,
)
from agent72.core.exceptions import EntityNotFoundException, ValidationError
from agent72.core.logging import get_logger

logger = get_logger(__name__)


class OrganizationService:
    """Service for managing institutions and organizational structure."""

    def __init__(self, repository: IOrganizationRepository) -> None:
        self.repository = repository

    def _unit_to_dto(self, unit: OrganizationalUnit) -> OrganizationalUnitResponseDTO:
        return OrganizationalUnitResponseDTO(
            id=unit.id or "",
            institution_id=unit.institution_id,
            code=unit.code,
            name=unit.name,
            unit_type=unit.unit_type,
            status=unit.status,
            parent_unit_id=unit.parent_unit_id,
            created_at=unit.created_at,
            updated_at=unit.updated_at,
        )

    def _institution_to_dto(self, inst: Institution) -> InstitutionResponseDTO:
        return InstitutionResponseDTO(
            id=inst.id or "",
            code=inst.code,
            name=inst.name,
            institution_type=inst.institution_type,
            status=inst.status,
            created_at=inst.created_at,
            updated_at=inst.updated_at,
            units=[self._unit_to_dto(u) for u in inst.units],
        )

    def create_institution(self, dto: InstitutionCreateDTO) -> InstitutionResponseDTO:
        existing = self.repository.get_institution_by_code(dto.code)
        if existing:
            raise ValidationError(f"Institution with code '{dto.code}' already exists.")

        domain_inst = Institution(
            code=dto.code,
            name=dto.name,
            institution_type=dto.institution_type,
            status=dto.status,
        )
        created = self.repository.create_institution(domain_inst)
        logger.info(f"Created institution '{created.name}' [{created.code}]")
        return self._institution_to_dto(created)

    def get_institution(self, institution_id: str) -> InstitutionResponseDTO:
        inst = self.repository.get_institution_by_id(institution_id)
        if not inst:
            raise EntityNotFoundException("Institution", institution_id)
        return self._institution_to_dto(inst)

    def list_institutions(self, skip: int = 0, limit: int = 50) -> InstitutionListResponseDTO:
        institutions = self.repository.list_institutions(skip=skip, limit=limit)
        items = [self._institution_to_dto(i) for i in institutions]
        return InstitutionListResponseDTO(total=len(items), items=items)

    def create_unit(self, dto: OrganizationalUnitCreateDTO) -> OrganizationalUnitResponseDTO:
        # Verify institution exists
        inst = self.repository.get_institution_by_id(dto.institution_id)
        if not inst:
            raise EntityNotFoundException("Institution", dto.institution_id)

        domain_unit = OrganizationalUnit(
            institution_id=dto.institution_id,
            code=dto.code,
            name=dto.name,
            unit_type=dto.unit_type,
            status=dto.status,
            parent_unit_id=dto.parent_unit_id,
        )
        created = self.repository.create_unit(domain_unit)
        logger.info(f"Created organizational unit '{created.name}' under institution '{dto.institution_id}'")
        return self._unit_to_dto(created)

    def list_units(self, institution_id: str) -> OrganizationalUnitListResponseDTO:
        units = self.repository.list_units_by_institution(institution_id)
        items = [self._unit_to_dto(u) for u in units]
        return OrganizationalUnitListResponseDTO(total=len(items), items=items)
