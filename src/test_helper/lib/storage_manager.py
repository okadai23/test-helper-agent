"""Storage manager for E2E test projects."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any, cast

if TYPE_CHECKING:  # pragma: no cover - type imports only
    from pathlib import Path

from test_helper.models.project import Project
from test_helper.utils.file_handler import FileHandler
from test_helper.utils.logger import get_logger
from test_helper.utils.settings import get_e2e_settings

logger = get_logger(__name__)


class StorageManager:
    """Manages file-based storage for E2E test projects."""

    def __init__(self, base_path: Path | None = None) -> None:
        """Initialize storage manager.

        Args:
            base_path: Base directory for storage. If None, uses default from settings.

        """
        settings = get_e2e_settings()
        self.base_path = base_path or settings.e2e_data_path
        self.projects_path = self.base_path / "projects"
        self.cache_path = self.base_path / "cache"
        self.file_handler = FileHandler()

        # Ensure directories exist
        self.projects_path.mkdir(parents=True, exist_ok=True)
        self.cache_path.mkdir(parents=True, exist_ok=True)

        logger.info(
            "Storage manager initialized",
            base_path=str(self.base_path),
            projects_path=str(self.projects_path),
            cache_path=str(self.cache_path),
        )

    def create_project(self, project: Project) -> Project:
        """Create a new project with storage structure.

        Args:
            project: Project model to create.

        Returns:
            Created project with ID.

        """
        project_dir = self.projects_path / project.id

        # Create project directory structure
        project_dir.mkdir(parents=True, exist_ok=True)
        (project_dir / "tests").mkdir(exist_ok=True)
        (project_dir / "cache").mkdir(exist_ok=True)
        (project_dir / "history").mkdir(exist_ok=True)

        # Save project metadata
        metadata = {
            "project": project.model_dump(mode="json"),
            "statistics": {
                "total_scenarios": 0,
                "total_tests": 0,
                "total_executions": 0,
                "last_execution": None,
            },
        }

        metadata_file = project_dir / "metadata.json"
        with metadata_file.open("w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)

        logger.info(
            "Project created",
            project_id=project.id,
            name=project.name,
            path=str(project_dir),
        )

        return project

    def get_project(self, project_id: str) -> Project | None:
        """Get project by ID.

        Args:
            project_id: Project UUID.

        Returns:
            Project if found, None otherwise.

        """
        project_dir = self.projects_path / project_id
        metadata_file = project_dir / "metadata.json"

        if not metadata_file.exists():
            logger.warning("Project not found", project_id=project_id)
            return None

        try:
            with metadata_file.open(encoding="utf-8") as f:
                metadata = json.load(f)

            project_data = metadata["project"]
            project = Project(**project_data)
        except Exception as e:
            logger.error(
                "Failed to load project",
                project_id=project_id,
                error=str(e),
            )
            return None
        else:
            logger.info("Project retrieved", project_id=project_id, name=project.name)
            return project

    def update_project(self, project: Project) -> Project:
        """Update an existing project.

        Args:
            project: Updated project model.

        Returns:
            Updated project.

        """
        project_dir = self.projects_path / project.id
        metadata_file = project_dir / "metadata.json"

        if not metadata_file.exists():
            msg = f"Project {project.id} not found"
            raise ValueError(msg)

        # Load existing metadata to preserve statistics
        with metadata_file.open(encoding="utf-8") as f:
            metadata = json.load(f)

        # Update project data
        metadata["project"] = project.model_dump(mode="json")

        # Save updated metadata
        with metadata_file.open("w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)

        logger.info("Project updated", project_id=project.id, name=project.name)
        return project

    def delete_project(self, project_id: str) -> bool:
        """Delete a project and all its data.

        Args:
            project_id: Project UUID to delete.

        Returns:
            True if deleted successfully.

        """
        project_dir = self.projects_path / project_id

        if not project_dir.exists():
            logger.warning("Project directory not found", project_id=project_id)
            return False

        try:
            # Remove all files and directories recursively
            import shutil

            shutil.rmtree(project_dir)
        except Exception as e:
            logger.error(
                "Failed to delete project",
                project_id=project_id,
                error=str(e),
            )
            return False
        else:
            logger.info("Project deleted", project_id=project_id)
            return True

    def list_projects(
        self,
        status: str | None = None,
        page: int = 1,
        limit: int = 20,
    ) -> tuple[list[Project], int]:
        """List projects with optional filtering and pagination.

        Args:
            status: Filter by project status.
            page: Page number (1-indexed).
            limit: Items per page.

        Returns:
            Tuple of (projects, total_count).

        """
        all_projects: list[Project] = []

        # Load all projects
        for project_dir in self.projects_path.iterdir():
            if not project_dir.is_dir():
                continue

            metadata_file = project_dir / "metadata.json"
            if not metadata_file.exists():
                continue

            try:
                with metadata_file.open(encoding="utf-8") as f:
                    metadata: dict[str, Any] = json.load(f)

                project_data_obj = metadata["project"]
                project_data = cast("dict[str, Any]", project_data_obj)
                project = Project(**project_data)

                # Apply status filter
                if status and project.status != status:
                    continue

                all_projects.append(project)

            except Exception as e:
                logger.error(
                    "Failed to load project",
                    project_dir=str(project_dir),
                    error=str(e),
                )
                continue

        # Sort by created_at (newest first)
        all_projects.sort(key=lambda p: p.created_at, reverse=True)

        # Apply pagination
        total: int = len(all_projects)
        start: int = (page - 1) * limit
        end: int = start + limit
        paginated: list[Project] = all_projects[start:end]

        logger.info(
            "Projects listed",
            total=total,
            page=page,
            limit=limit,
            returned=len(paginated),
        )

        return paginated, total

    def project_exists(self, project_id: str) -> bool:
        """Check if a project exists.

        Args:
            project_id: Project UUID.

        Returns:
            True if project exists.

        """
        project_dir = self.projects_path / project_id
        metadata_file = project_dir / "metadata.json"
        return metadata_file.exists()

    def project_name_exists(self, name: str, exclude_id: str | None = None) -> bool:
        """Check if a project name already exists.

        Args:
            name: Project name to check.
            exclude_id: Project ID to exclude from check (for updates).

        Returns:
            True if name exists.

        """
        for project_dir in self.projects_path.iterdir():
            if not project_dir.is_dir():
                continue

            # Skip if this is the excluded ID
            if exclude_id and project_dir.name == exclude_id:
                continue

            metadata_file = project_dir / "metadata.json"
            if not metadata_file.exists():
                continue

            try:
                with metadata_file.open(encoding="utf-8") as f:
                    metadata = json.load(f)

                if metadata["project"]["name"] == name:
                    return True

            except Exception as e:
                logger.error(
                    "Failed to check project name",
                    project_dir=str(project_dir),
                    error=str(e),
                )
                continue

        return False
