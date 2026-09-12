"""Endpoints module exports."""

from agent72.api.v1.endpoints.health import router as health_router
from agent72.api.v1.endpoints.plans import router as plans_router
from agent72.api.v1.endpoints.organizations import router as organizations_router
from agent72.api.v1.endpoints.evidence import router as evidence_router

__all__ = [
    "health_router",
    "plans_router",
    "organizations_router",
    "evidence_router",
]
