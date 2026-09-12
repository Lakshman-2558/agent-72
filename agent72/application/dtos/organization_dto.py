"""Pydantic DTOs for Institution and Organizational Context."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field
from agent72.domain.models.organization import EntityStatus, UnitType


class OrganizationalUnitBaseDTO(BaseModel):
    code: str = Field(..., min_length=1, max_length=50, description="Department or Unit code, e.g. 'CSE'")
    name: str = Field(..., min_length=2, max_length=255, description="Full Unit name")
    unit_type: UnitType = Field(default=UnitType.DEPARTMENT, description="Unit level/type")
    status: EntityStatus = Field(default=EntityStatus.ACTIVE)
    parent_unit_id: Optional[str] = Field(None, description="Optional parent school/faculty ID")


class OrganizationalUnitCreateDTO(OrganizationalUnitBaseDTO):
    institution_id: str = Field(..., min_length=1, description="Parent institution UUID")


class OrganizationalUnitResponseDTO(OrganizationalUnitBaseDTO):
    model_config = ConfigDict(from_attributes=True)
    id: str
    institution_id: str
    created_at: datetime
    updated_at: datetime


class OrganizationalUnitListResponseDTO(BaseModel):
    total: int
    items: List[OrganizationalUnitResponseDTO]


class InstitutionBaseDTO(BaseModel):
    code: str = Field(..., min_length=2, max_length=50, description="Unique institution code, e.g. 'APEX-UNIV'")
    name: str = Field(..., min_length=2, max_length=255, description="Full institution name")
    institution_type: UnitType = Field(default=UnitType.UNIVERSITY)
    status: EntityStatus = Field(default=EntityStatus.ACTIVE)


class InstitutionCreateDTO(InstitutionBaseDTO):
    pass


class InstitutionResponseDTO(InstitutionBaseDTO):
    model_config = ConfigDict(from_attributes=True)
    id: str
    created_at: datetime
    updated_at: datetime
    units: List[OrganizationalUnitResponseDTO] = Field(default_factory=list)


class InstitutionListResponseDTO(BaseModel):
    total: int
    items: List[InstitutionResponseDTO]
