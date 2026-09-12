"""SQLAlchemy implementation of IOrganizationRepository."""

import uuid
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session

from agent72.domain.interfaces.organization_repository import IOrganizationRepository
from agent72.domain.models.organization import (
    Institution,
    OrganizationalUnit,
    UnitType,
    EntityStatus,
)
from agent72.infrastructure.database.models import (
    InstitutionModel,
    OrganizationalUnitModel,
)


class SQLAlchemyOrganizationRepository(IOrganizationRepository):
    """Persistence repository for Institutions and Organizational Units."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def _unit_to_domain(self, model: OrganizationalUnitModel) -> OrganizationalUnit:
        return OrganizationalUnit(
            id=model.id,
            institution_id=model.institution_id,
            code=model.code,
            name=model.name,
            unit_type=UnitType(model.unit_type),
            status=EntityStatus(model.status),
            parent_unit_id=model.parent_unit_id,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _institution_to_domain(self, model: InstitutionModel) -> Institution:
        return Institution(
            id=model.id,
            code=model.code,
            name=model.name,
            institution_type=UnitType(model.institution_type),
            status=EntityStatus(model.status),
            created_at=model.created_at,
            updated_at=model.updated_at,
            units=[self._unit_to_domain(u) for u in model.units],
        )

    def get_institution_by_id(self, institution_id: str) -> Optional[Institution]:
        stmt = select(InstitutionModel).where(InstitutionModel.id == institution_id)
        model = self.session.execute(stmt).scalar_one_or_none()
        if not model:
            return None
        return self._institution_to_domain(model)

    def get_institution_by_code(self, code: str) -> Optional[Institution]:
        stmt = select(InstitutionModel).where(InstitutionModel.code == code)
        model = self.session.execute(stmt).scalar_one_or_none()
        if not model:
            return None
        return self._institution_to_domain(model)

    def list_institutions(self, skip: int = 0, limit: int = 50) -> List[Institution]:
        stmt = select(InstitutionModel).order_by(InstitutionModel.name).offset(skip).limit(limit)
        models = self.session.execute(stmt).scalars().all()
        return [self._institution_to_domain(m) for m in models]

    def create_institution(self, institution: Institution) -> Institution:
        inst_id = institution.id or str(uuid.uuid4())
        model = InstitutionModel(
            id=inst_id,
            code=institution.code,
            name=institution.name,
            institution_type=institution.institution_type.value,
            status=institution.status.value,
        )
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return self._institution_to_domain(model)

    def get_unit_by_id(self, unit_id: str) -> Optional[OrganizationalUnit]:
        stmt = select(OrganizationalUnitModel).where(OrganizationalUnitModel.id == unit_id)
        model = self.session.execute(stmt).scalar_one_or_none()
        if not model:
            return None
        return self._unit_to_domain(model)

    def list_units_by_institution(self, institution_id: str) -> List[OrganizationalUnit]:
        stmt = (
            select(OrganizationalUnitModel)
            .where(OrganizationalUnitModel.institution_id == institution_id)
            .order_by(OrganizationalUnitModel.code)
        )
        models = self.session.execute(stmt).scalars().all()
        return [self._unit_to_domain(m) for m in models]

    def create_unit(self, unit: OrganizationalUnit) -> OrganizationalUnit:
        unit_id = unit.id or str(uuid.uuid4())
        model = OrganizationalUnitModel(
            id=unit_id,
            institution_id=unit.institution_id,
            code=unit.code,
            name=unit.name,
            unit_type=unit.unit_type.value,
            status=unit.status.value,
            parent_unit_id=unit.parent_unit_id,
        )
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return self._unit_to_domain(model)
