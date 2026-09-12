"""Domain entities for Institutional Organization Context."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional


class EntityStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    ARCHIVED = "ARCHIVED"


class UnitType(str, Enum):
    UNIVERSITY = "UNIVERSITY"
    COLLEGE = "COLLEGE"
    FACULTY = "FACULTY"
    SCHOOL = "SCHOOL"
    DEPARTMENT = "DEPARTMENT"
    CENTER = "CENTER"
    DIVISION = "DIVISION"


@dataclass
class OrganizationalUnit:
    """Department, School, or Center within an Institution."""
    id: Optional[str] = None
    institution_id: str = ""
    code: str = ""
    name: str = ""
    unit_type: UnitType = UnitType.DEPARTMENT
    status: EntityStatus = EntityStatus.ACTIVE
    parent_unit_id: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class Institution:
    """Aggregate Root representing an Institution / University."""
    id: Optional[str] = None
    code: str = ""
    name: str = ""
    institution_type: UnitType = UnitType.UNIVERSITY
    status: EntityStatus = EntityStatus.ACTIVE
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    units: List[OrganizationalUnit] = field(default_factory=list)
