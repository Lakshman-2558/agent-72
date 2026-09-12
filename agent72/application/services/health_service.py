"""Health check service for Agent 72 application."""

import time
from typing import Any, Dict
from sqlalchemy import text
from sqlalchemy.orm import Session
from agent72.core.config import settings
from agent72.domain.interfaces.ai_provider import IAIProvider
from agent72.core.logging import get_logger

logger = get_logger(__name__)

_START_TIME = time.time()


class HealthService:
    """Evaluates the readiness and liveness of Agent 72 components."""

    def __init__(self, db: Session, ai_provider: IAIProvider) -> None:
        self.db = db
        self.ai_provider = ai_provider

    def check_liveness(self) -> Dict[str, Any]:
        """Basic liveness probe confirming the HTTP server is responsive."""
        return {
            "status": "alive",
            "uptime_seconds": round(time.time() - _START_TIME, 2),
            "timestamp": time.time(),
        }

    def check_readiness(self) -> Dict[str, Any]:
        """Comprehensive readiness probe verifying database and AI provider dependencies."""
        db_status = "healthy"
        db_details = {}

        try:
            start_db = time.time()
            self.db.execute(text("SELECT 1"))
            db_latency = round((time.time() - start_db) * 1000, 2)
            db_details = {
                "status": "healthy",
                "latency_ms": db_latency,
                "engine": "sqlite" if settings.is_sqlite else "postgresql",
            }
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
            db_status = "unhealthy"
            db_details = {
                "status": "unhealthy",
                "error": str(e),
                "engine": "sqlite" if settings.is_sqlite else "postgresql",
            }

        ai_health = self.ai_provider.health_check()

        overall_status = "healthy" if db_status == "healthy" and ai_health.get("status") == "healthy" else "degraded"

        return {
            "status": overall_status,
            "version": settings.VERSION,
            "environment": settings.ENVIRONMENT,
            "uptime_seconds": round(time.time() - _START_TIME, 2),
            "dependencies": {
                "database": db_details,
                "ai_provider": ai_health,
            },
        }
