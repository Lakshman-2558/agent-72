"""Organization & Institutional Context API endpoints."""

from fastapi import APIRouter, Depends, Query, status
from agent72.api.dependencies import get_organization_service
from agent72.application.dtos.organization_dto import (
    InstitutionCreateDTO,
    InstitutionResponseDTO,
    InstitutionListResponseDTO,
    OrganizationalUnitCreateDTO,
    OrganizationalUnitResponseDTO,
    OrganizationalUnitListResponseDTO,
)
from agent72.application.services.organization_service import OrganizationService

router = APIRouter(prefix="/organizations", tags=["Institutional Context"])


@router.post(
    "/institutions",
    response_model=InstitutionResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new Institution",
    description="Registers an institution or university with canonical code and metadata.",
)
def create_institution(
    dto: InstitutionCreateDTO,
    service: OrganizationService = Depends(get_organization_service),
) -> InstitutionResponseDTO:
    return service.create_institution(dto)


@router.get(
    "/institutions",
    response_model=InstitutionListResponseDTO,
    summary="List Institutions",
    description="Lists all registered institutions with pagination.",
)
def list_institutions(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    service: OrganizationService = Depends(get_organization_service),
) -> InstitutionListResponseDTO:
    return service.list_institutions(skip=skip, limit=limit)


@router.get(
    "/institutions/{institution_id}",
    response_model=InstitutionResponseDTO,
    summary="Get Institution by ID",
    description="Fetches an institution along with its associated departments/units.",
)
def get_institution(
    institution_id: str,
    service: OrganizationService = Depends(get_organization_service),
) -> InstitutionResponseDTO:
    return service.get_institution(institution_id)


@router.post(
    "/units",
    response_model=OrganizationalUnitResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Create Organizational Unit",
    description="Creates a department, school, or center under an institution.",
)
def create_unit(
    dto: OrganizationalUnitCreateDTO,
    service: OrganizationService = Depends(get_organization_service),
) -> OrganizationalUnitResponseDTO:
    return service.create_unit(dto)


@router.get(
    "/institutions/{institution_id}/units",
    response_model=OrganizationalUnitListResponseDTO,
    summary="List Units for Institution",
    description="Lists all departments and schools associated with an institution.",
)
def list_units_for_institution(
    institution_id: str,
    service: OrganizationService = Depends(get_organization_service),
) -> OrganizationalUnitListResponseDTO:
    return service.list_units(institution_id)
