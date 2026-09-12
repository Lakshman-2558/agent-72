"""Abstract Repository Protocol for Institutions and Units."""

from abc import ABC, abstractmethod
from typing import List, Optional
from agent72.domain.models.organization import Institution, OrganizationalUnit


class IOrganizationRepository(ABC):
    """Abstract interface defining persistence operations for institutions and units."""

    @abstractmethod
    def get_institution_by_id(self, institution_id: str) -> Optional[Institution]:
        pass

    @abstractmethod
    def get_institution_by_code(self, code: str) -> Optional[Institution]:
        pass

    @abstractmethod
    def list_institutions(self, skip: int = 0, limit: int = 50) -> List[Institution]:
        pass

    @abstractmethod
    def create_institution(self, institution: Institution) -> Institution:
        pass

    @abstractmethod
    def get_unit_by_id(self, unit_id: str) -> Optional[OrganizationalUnit]:
        pass

    @abstractmethod
    def list_units_by_institution(self, institution_id: str) -> List[OrganizationalUnit]:
        pass

    @abstractmethod
    def create_unit(self, unit: OrganizationalUnit) -> OrganizationalUnit:
        pass
