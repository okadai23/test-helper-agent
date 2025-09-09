"""Main FastAPI application for E2E Test Automation API."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from test_helper.utils.logger import get_logger

logger = get_logger(__name__)


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="E2E Test Automation AI Agent API",
        description="API for managing test automation projects and executing AI-driven test generation and fixes",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add routers
    from .projects import router as projects_router

    app.include_router(projects_router, prefix="/api/v1")

    # TODO: Add other routers when implemented
    # from .capture import router as capture_router
    # from .tests import router as tests_router
    # from .executions import router as executions_router
    # from .fixes import router as fixes_router

    # app.include_router(capture_router, prefix="/api/v1")
    # app.include_router(tests_router, prefix="/api/v1")
    # app.include_router(executions_router, prefix="/api/v1")
    # app.include_router(fixes_router, prefix="/api/v1")

    @app.get("/health")
    async def health_check() -> dict[str, str]:
        """Health check endpoint."""
        return {"status": "healthy", "service": "e2e-test-automation"}

    logger.info("FastAPI app created for E2E Test Automation")
    return app


# Create the app instance
app = create_app()
