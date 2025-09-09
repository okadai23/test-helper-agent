"""Project management API endpoints."""

from __future__ import annotations

from datetime import datetime, UTC
from typing import Any

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field, HttpUrl

from test_helper.e2e.lib.storage_manager import StorageManager
from test_helper.e2e.models.browser_config import BrowserConfig
from test_helper.e2e.models.project import Project
from test_helper.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/projects", tags=["Projects"])

# Initialize storage manager
storage = StorageManager()


# Request/Response models
class CreateProjectRequest(BaseModel):
    """Request model for creating a project."""

    name: str = Field(..., min_length=1, max_length=100)
    url: HttpUrl = Field(..., description="Target application URL")
    browser_config: BrowserConfig | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class UpdateProjectRequest(BaseModel):
    """Request model for updating a project."""

    name: str | None = Field(None, min_length=1, max_length=100)
    url: HttpUrl | None = None
    status: str | None = Field(None, pattern=r"^(active|archived|paused)$")
    browser_config: BrowserConfig | None = None
    metadata: dict[str, Any] | None = None


class ProjectListResponse(BaseModel):
    """Response model for project list."""

    items: list[Project]
    total: int
    page: int
    limit: int


@router.post("", status_code=status.HTTP_201_CREATED, response_model=Project)
async def create_project(request: CreateProjectRequest) -> Project:
    """Create a new test project."""
    logger.info("Creating project", name=request.name, url=str(request.url))

    # Check if project name already exists
    if storage.project_name_exists(request.name):
        logger.warning("Project name already exists", name=request.name)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": "CONFLICT",
                "message": f"Project with name '{request.name}' already exists",
            },
        )

    # Create project
    project = Project(
        name=request.name,
        url=request.url,
        browser_config=request.browser_config or BrowserConfig(),
        metadata=request.metadata,
    )

    try:
        created_project = storage.create_project(project)
        logger.info("Project created successfully", project_id=created_project.id)
        return created_project
    except Exception as e:
        logger.error("Failed to create project", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "INTERNAL_ERROR",
                "message": "Failed to create project",
            },
        ) from e


@router.get("", response_model=ProjectListResponse)
async def list_projects(
    status_filter: str | None = Query(
        None, alias="status", pattern=r"^(active|archived|paused)$",
    ),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
) -> ProjectListResponse:
    """List all test projects with optional filtering and pagination."""
    logger.info("Listing projects", status=status_filter, page=page, limit=limit)

    try:
        projects, total = storage.list_projects(
            status=status_filter, page=page, limit=limit,
        )

        return ProjectListResponse(
            items=projects,
            total=total,
            page=page,
            limit=limit,
        )
    except Exception as e:
        logger.error("Failed to list projects", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "INTERNAL_ERROR",
                "message": "Failed to list projects",
            },
        ) from e


@router.get("/{project_id}", response_model=Project)
async def get_project(project_id: str) -> Project:
    """Get project details by ID."""
    logger.info("Getting project", project_id=project_id)

    # Validate UUID format
    try:
        from uuid import UUID

        UUID(project_id)
    except ValueError as e:
        logger.warning("Invalid project ID format", project_id=project_id)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "INVALID_UUID",
                "message": f"Invalid UUID format: {project_id}",
            },
        ) from e

    project = storage.get_project(project_id)
    if not project:
        logger.warning("Project not found", project_id=project_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "NOT_FOUND",
                "message": f"Project {project_id} not found",
            },
        )

    logger.info("Project retrieved successfully", project_id=project_id)
    return project


@router.patch("/{project_id}", response_model=Project)
async def update_project(project_id: str, request: UpdateProjectRequest) -> Project:
    """Update project configuration."""
    logger.info("Updating project", project_id=project_id)

    # Validate UUID format
    try:
        from uuid import UUID

        UUID(project_id)
    except ValueError as e:
        logger.warning("Invalid project ID format", project_id=project_id)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "INVALID_UUID",
                "message": f"Invalid UUID format: {project_id}",
            },
        ) from e

    # Get existing project
    existing_project = storage.get_project(project_id)
    if not existing_project:
        logger.warning("Project not found for update", project_id=project_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "NOT_FOUND",
                "message": f"Project {project_id} not found",
            },
        )

    # Check for duplicate name if name is being updated
    if request.name and request.name != existing_project.name:
        if storage.project_name_exists(request.name, exclude_id=project_id):
            logger.warning("Project name already exists", name=request.name)
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "error": "CONFLICT",
                    "message": f"Project with name '{request.name}' already exists",
                },
            )

    # Update project fields
    update_data = request.model_dump(exclude_unset=True)
    updated_fields = {}

    for field, value in update_data.items():
        if value is not None:
            updated_fields[field] = value

    # Update timestamp
    updated_fields["updated_at"] = datetime.now(UTC)

    # Create updated project
    updated_project = existing_project.model_copy(update=updated_fields)

    try:
        saved_project = storage.update_project(updated_project)
        logger.info(
            "Project updated successfully",
            project_id=project_id,
            updated_fields=list(updated_fields.keys()),
        )
        return saved_project
    except Exception as e:
        logger.error("Failed to update project", project_id=project_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "INTERNAL_ERROR",
                "message": "Failed to update project",
            },
        ) from e


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(project_id: str) -> None:
    """Delete a project and all its data."""
    logger.info("Deleting project", project_id=project_id)

    # Validate UUID format
    try:
        from uuid import UUID

        UUID(project_id)
    except ValueError as e:
        logger.warning("Invalid project ID format", project_id=project_id)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "INVALID_UUID",
                "message": f"Invalid UUID format: {project_id}",
            },
        ) from e

    # Check if project exists
    if not storage.project_exists(project_id):
        logger.warning("Project not found for deletion", project_id=project_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "NOT_FOUND",
                "message": f"Project {project_id} not found",
            },
        )

    try:
        success = storage.delete_project(project_id)
        if success:
            logger.info("Project deleted successfully", project_id=project_id)
        else:
            logger.error("Failed to delete project", project_id=project_id)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "error": "INTERNAL_ERROR",
                    "message": "Failed to delete project",
                },
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to delete project", project_id=project_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "INTERNAL_ERROR",
                "message": "Failed to delete project",
            },
        ) from e
