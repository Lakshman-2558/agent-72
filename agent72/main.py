"""FastAPI Application Entry Point for Agent 72 Strategic Planning Agent."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from agent72.api.middleware.request_context import RequestContextMiddleware
from agent72.api.v1.router import api_v1_router
from agent72.core.config import settings
from agent72.core.exceptions import Agent72Exception
from agent72.core.logging import get_logger, setup_logging
from agent72.infrastructure.database.base import Base
from agent72.infrastructure.database.session import engine

# Setup structured logging
setup_logging(log_level=settings.LOG_LEVEL, environment=settings.ENVIRONMENT)
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan context manager for startup and shutdown hooks."""
    logger.info(
        f"Starting {settings.PROJECT_NAME} v{settings.VERSION} "
        f"[Environment: {settings.ENVIRONMENT}, Database: {'SQLite' if settings.is_sqlite else 'PostgreSQL'}]"
    )

    # Ensure base tables exist in all environments (SQLite or Postgres)
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database schema verified / initialized.")
        
        # Auto-seed initial datasets if the database is newly initialized and empty
        from agent72.infrastructure.database.session import SessionLocal
        from agent72.infrastructure.database.models import InstitutionModel
        with SessionLocal() as db:
            inst_count = db.query(InstitutionModel).count()
            if inst_count == 0:
                logger.info("Empty database detected on startup. Auto-seeding initial Vignan's University datasets...")
                try:
                    from scripts.seed_demo_trajectory import seed_demo_data
                    from scripts.seed_multi_period_data import seed_multi_period_data
                    from scripts.update_to_vignan import update_to_vignan
                    seed_demo_data()
                    seed_multi_period_data()
                    update_to_vignan()
                    logger.info("Initial institutional dataset seeded successfully.")
                except Exception as seed_err:
                    logger.warning(f"Startup auto-seed encountered non-fatal error: {seed_err}")
    except Exception as e:
        logger.warning(f"Database initialization check: {e}")

    yield

    # Clean shutdown
    logger.info("Shutting down Agent 72 application.")
    engine.dispose()


def create_application() -> FastAPI:
    """Application factory for Agent 72."""
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description=settings.DESCRIPTION,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        openapi_tags=[
            {
                "name": "Health & Observability",
                "description": "Liveness, readiness probes, and dependency status checks.",
            },
            {
                "name": "Strategic Plans",
                "description": "Lifecycle management of Institutional Strategic Plans, objectives, and options.",
            },
        ],
    )

    # Middleware: Observability & Tracing
    app.add_middleware(RequestContextMiddleware)

    # Middleware: CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Exception Handlers
    @app.exception_handler(Agent72Exception)
    async def handle_agent_exception(request: Request, exc: Agent72Exception) -> JSONResponse:
        logger.warning(
            f"Handled application error: {exc.message} "
            f"status={exc.status_code} path={request.url.path} "
            f"request_id={getattr(request.state, 'request_id', 'unknown')}"
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": exc.__class__.__name__,
                    "message": exc.message,
                    "details": exc.details,
                    "request_id": getattr(request.state, "request_id", None),
                }
            },
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
        logger.info(f"Validation error on {request.url.path}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": {
                    "code": "RequestValidationError",
                    "message": "Input validation failed. Please check payload parameters.",
                    "details": jsonable_encoder(exc.errors()),
                    "request_id": getattr(request.state, "request_id", None),
                }
            },
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
        logger.error(f"Unhandled exception on {request.url.path}: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": {
                    "code": "InternalServerError",
                    "message": "An unexpected internal error occurred. Please try again later.",
                    "request_id": getattr(request.state, "request_id", None),
                }
            },
        )

    # Master Router
    app.include_router(api_v1_router)

    # Mount frontend static distribution if built
    from pathlib import Path
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import FileResponse

    frontend_dist_dir = Path(__file__).resolve().parent / "frontend" / "dist"
    frontend_assets_dir = frontend_dist_dir / "assets"

    if frontend_dist_dir.exists():
        if frontend_assets_dir.exists():
            app.mount("/ui/assets", StaticFiles(directory=str(frontend_assets_dir)), name="ui_assets")

        @app.get("/ui", include_in_schema=False)
        @app.get("/ui/{full_path:path}", include_in_schema=False)
        async def serve_ui(full_path: str = ""):
            if full_path:
                candidate = frontend_dist_dir / full_path
                if candidate.is_file():
                    return FileResponse(str(candidate))
            index_path = frontend_dist_dir / "index.html"
            if index_path.exists():
                return FileResponse(str(index_path))
            return JSONResponse(status_code=404, content={"message": "Frontend build index.html not found."})

        @app.get("/{image_name}.png", include_in_schema=False)
        async def serve_root_image(image_name: str):
            candidate = frontend_dist_dir / f"{image_name}.png"
            if candidate.is_file():
                return FileResponse(str(candidate))
            return JSONResponse(status_code=404, content={"message": "Image not found"})

    # Root endpoint for quick redirection
    @app.get("/", include_in_schema=False)
    def root():
        return {
            "name": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "status": "online",
            "docs": "/docs",
            "health": "/api/v1/health",
            "ui": "/ui",
        }

    return app



app = create_application()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "agent72.main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.DEBUG,
    )
