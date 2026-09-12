"""Health check API endpoints."""

from typing import Any, Dict
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from agent72.api.dependencies import get_health_service
from agent72.application.services.health_service import HealthService

router = APIRouter(prefix="/health", tags=["Health & Observability"])


@router.get(
    "",
    summary="Application Readiness Probe",
    description="Verifies operational status of Agent 72, including database connectivity and AI provider availability.",
    response_description="System health status report",
)
def readiness_check(health_service: HealthService = Depends(get_health_service)) -> JSONResponse:
    report = health_service.check_readiness()
    http_status = status.HTTP_200_OK if report["status"] == "healthy" else status.HTTP_503_SERVICE_UNAVAILABLE
    return JSONResponse(status_code=http_status, content=report)


@router.get(
    "/live",
    summary="Application Liveness Probe",
    description="Fast lightweight ping verifying that the application process is running and responsive.",
    response_description="Basic uptime and status",
)
def liveness_check(health_service: HealthService = Depends(get_health_service)) -> Dict[str, Any]:
    return health_service.check_liveness()
