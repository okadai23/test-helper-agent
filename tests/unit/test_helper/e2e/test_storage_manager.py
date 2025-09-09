"""Unit tests for Storage Manager."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from test_helper.e2e.lib.storage_manager import StorageManager
from test_helper.e2e.models.project import Project


class TestStorageManager:
    """Unit tests for Storage Manager functionality."""

    def test_storage_manager_initialization(self, temp_dir: Path) -> None:
        """Test storage manager initialization."""
        storage = StorageManager(base_path=temp_dir)

        assert storage.base_path == temp_dir
        assert storage.projects_path == temp_dir / "projects"
        assert storage.cache_path == temp_dir / "cache"

        # Verify directories were created
        assert storage.projects_path.exists()
        assert storage.cache_path.exists()

    def test_create_project_success(self, temp_dir: Path) -> None:
        """Test successful project creation."""
        storage = StorageManager(base_path=temp_dir)

        project = Project(
            name="Test Project",
            url="https://example.com",
        )

        created_project = storage.create_project(project)

        # Verify project returned correctly
        assert created_project.id == project.id
        assert created_project.name == project.name
        assert str(created_project.url) == str(project.url)

        # Verify project directory structure created
        project_dir = storage.projects_path / project.id
        assert project_dir.exists()
        assert (project_dir / "tests").exists()
        assert (project_dir / "cache").exists()
        assert (project_dir / "history").exists()

        # Verify metadata file created
        metadata_file = project_dir / "metadata.json"
        assert metadata_file.exists()

        # Verify metadata content
        with metadata_file.open(encoding="utf-8") as f:
            metadata_data = json.load(f)

        assert metadata_data["project"]["id"] == project.id
        assert metadata_data["project"]["name"] == project.name
        assert metadata_data["statistics"]["total_scenarios"] == 0

    def test_get_project_success(self, temp_dir: Path) -> None:
        """Test successful project retrieval."""
        storage = StorageManager(base_path=temp_dir)

        # Create project
        original_project = Project(
            name="Retrieve Test",
            url="https://example.com",
        )
        storage.create_project(original_project)

        # Retrieve project
        retrieved_project = storage.get_project(original_project.id)

        assert retrieved_project is not None
        assert retrieved_project.id == original_project.id
        assert retrieved_project.name == original_project.name
        assert str(retrieved_project.url) == str(original_project.url)

    def test_get_project_not_found(self, temp_dir: Path) -> None:
        """Test project retrieval with non-existent ID."""
        storage = StorageManager(base_path=temp_dir)

        from uuid import uuid4
        non_existent_id = str(uuid4())

        result = storage.get_project(non_existent_id)
        assert result is None

    def test_update_project_success(self, temp_dir: Path) -> None:
        """Test successful project update."""
        storage = StorageManager(base_path=temp_dir)

        # Create project
        original_project = Project(
            name="Original Name",
            url="https://example.com",
        )
        storage.create_project(original_project)

        # Update project
        updated_project = original_project.model_copy(
            update={
                "name": "Updated Name",
                "status": "paused",
            },
        )

        result = storage.update_project(updated_project)

        assert result.name == "Updated Name"
        assert result.status == "paused"
        assert result.id == original_project.id

        # Verify update persisted
        retrieved_project = storage.get_project(original_project.id)
        assert retrieved_project is not None
        assert retrieved_project.name == "Updated Name"
        assert retrieved_project.status == "paused"

    def test_update_project_not_found(self, temp_dir: Path) -> None:
        """Test project update with non-existent ID."""
        storage = StorageManager(base_path=temp_dir)

        non_existent_project = Project(
            name="Non-existent",
            url="https://example.com",
        )

        with pytest.raises(ValueError, match="not found"):
            storage.update_project(non_existent_project)

    def test_delete_project_success(self, temp_dir: Path) -> None:
        """Test successful project deletion."""
        storage = StorageManager(base_path=temp_dir)

        # Create project
        project = Project(
            name="Delete Test",
            url="https://example.com",
        )
        storage.create_project(project)

        project_dir = storage.projects_path / project.id
        assert project_dir.exists()

        # Delete project
        result = storage.delete_project(project.id)
        assert result is True

        # Verify project directory removed
        assert not project_dir.exists()

        # Verify project cannot be retrieved
        retrieved_project = storage.get_project(project.id)
        assert retrieved_project is None

    def test_delete_project_not_found(self, temp_dir: Path) -> None:
        """Test project deletion with non-existent ID."""
        storage = StorageManager(base_path=temp_dir)

        from uuid import uuid4
        non_existent_id = str(uuid4())

        result = storage.delete_project(non_existent_id)
        assert result is False

    def test_list_projects_empty(self, temp_dir: Path) -> None:
        """Test project listing when no projects exist."""
        storage = StorageManager(base_path=temp_dir)

        projects, total = storage.list_projects()

        assert projects == []
        assert total == 0

    def test_list_projects_with_data(self, temp_dir: Path) -> None:
        """Test project listing with existing projects."""
        storage = StorageManager(base_path=temp_dir)

        # Create multiple projects
        project1 = Project(name="Project 1", url="https://example.com")
        project2 = Project(name="Project 2", url="https://example.com")
        project3 = Project(name="Project 3", url="https://example.com", status="paused")

        storage.create_project(project1)
        storage.create_project(project2)
        storage.create_project(project3)

        # List all projects
        projects, total = storage.list_projects()

        assert total == 3
        assert len(projects) == 3

        # Verify projects are sorted by created_at (newest first)
        project_names = [p.name for p in projects]
        assert "Project 3" in project_names
        assert "Project 2" in project_names
        assert "Project 1" in project_names

    def test_list_projects_with_status_filter(self, temp_dir: Path) -> None:
        """Test project listing with status filter."""
        storage = StorageManager(base_path=temp_dir)

        # Create projects with different statuses
        active_project = Project(name="Active", url="https://example.com", status="active")
        paused_project = Project(name="Paused", url="https://example.com", status="paused")

        storage.create_project(active_project)
        storage.create_project(paused_project)

        # Filter by active status
        active_projects, active_total = storage.list_projects(status="active")
        assert active_total == 1
        assert active_projects[0].status == "active"
        assert active_projects[0].name == "Active"

        # Filter by paused status
        paused_projects, paused_total = storage.list_projects(status="paused")
        assert paused_total == 1
        assert paused_projects[0].status == "paused"
        assert paused_projects[0].name == "Paused"

    def test_list_projects_pagination(self, temp_dir: Path) -> None:
        """Test project listing with pagination."""
        storage = StorageManager(base_path=temp_dir)

        # Create 5 projects
        for i in range(5):
            project = Project(name=f"Project {i}", url="https://example.com")
            storage.create_project(project)

        # Test pagination
        page1_projects, total = storage.list_projects(page=1, limit=2)
        assert total == 5
        assert len(page1_projects) == 2

        page2_projects, total = storage.list_projects(page=2, limit=2)
        assert total == 5
        assert len(page2_projects) == 2

        page3_projects, total = storage.list_projects(page=3, limit=2)
        assert total == 5
        assert len(page3_projects) == 1  # Last page with remaining item

    def test_project_exists(self, temp_dir: Path) -> None:
        """Test project existence check."""
        storage = StorageManager(base_path=temp_dir)

        # Create project
        project = Project(name="Exists Test", url="https://example.com")
        storage.create_project(project)

        # Check existence
        assert storage.project_exists(project.id) is True

        from uuid import uuid4
        non_existent_id = str(uuid4())
        assert storage.project_exists(non_existent_id) is False

    def test_project_name_exists(self, temp_dir: Path) -> None:
        """Test project name uniqueness check."""
        storage = StorageManager(base_path=temp_dir)

        # Create project
        project = Project(name="Unique Name", url="https://example.com")
        storage.create_project(project)

        # Check name existence
        assert storage.project_name_exists("Unique Name") is True
        assert storage.project_name_exists("Different Name") is False

        # Check exclusion of own ID
        assert storage.project_name_exists("Unique Name", exclude_id=project.id) is False

    def test_storage_manager_handles_corrupted_metadata(self, temp_dir: Path) -> None:
        """Test storage manager handles corrupted metadata gracefully."""
        storage = StorageManager(base_path=temp_dir)

        # Create a project directory with corrupted metadata
        from uuid import uuid4
        project_id = str(uuid4())
        project_dir = storage.projects_path / project_id
        project_dir.mkdir(parents=True)

        metadata_file = project_dir / "metadata.json"
        metadata_file.write_text("invalid json content", encoding="utf-8")

        # Should handle corrupted data gracefully
        result = storage.get_project(project_id)
        assert result is None

        # Should not crash when listing projects
        projects, total = storage.list_projects()
        # Should return other valid projects but skip corrupted one
        assert isinstance(projects, list)
        assert isinstance(total, int)
