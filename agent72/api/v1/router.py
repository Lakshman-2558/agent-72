"""API v1 master router."""

from fastapi import APIRouter
from agent72.api.v1.endpoints.health import router as health_router
from agent72.api.v1.endpoints.plans import router as plans_router
from agent72.api.v1.endpoints.organizations import router as organizations_router
from agent72.api.v1.endpoints.evidence import router as evidence_router
from agent72.api.v1.endpoints.analysis import router as analysis_router
from agent72.api.v1.endpoints.trajectory import router as trajectory_router
from agent72.api.v1.endpoints.strategic_intelligence import router as strategic_intelligence_router
from agent72.api.v1.endpoints.strategic_options import router as strategic_options_router

api_v1_router = APIRouter(prefix="/api/v1")

api_v1_router.include_router(health_router)
api_v1_router.include_router(organizations_router)
api_v1_router.include_router(evidence_router)
api_v1_router.include_router(plans_router)
api_v1_router.include_router(analysis_router)
api_v1_router.include_router(trajectory_router)
api_v1_router.include_router(strategic_intelligence_router)
api_v1_router.include_router(strategic_options_router)


