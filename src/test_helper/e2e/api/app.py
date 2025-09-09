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
        description="API for managing test automation projects and AI-driven test generation",
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

    # Future routers will be added here for capture, tests, executions, and fixes

    @app.get("/health")
    async def health_check() -> dict[str, str]:
        """Health check endpoint."""
        return {"status": "healthy", "service": "e2e-test-automation"}

    logger.info("FastAPI app created for E2E Test Automation")
    return app


# Create the app instance
app = create_app()
