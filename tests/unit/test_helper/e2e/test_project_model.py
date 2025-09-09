"""Unit tests for Project model validation."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from test_helper.e2e.models.browser_config import BrowserConfig, ViewportSize
from test_helper.e2e.models.project import Project


class TestProjectModel:
    """Unit tests for Project model validation."""

    def test_project_creation_with_defaults(self) -> None:
        """Test project creation with minimal required fields."""
        project = Project(
            name="Test Project",
            url="https://example.com",
        )

        assert project.name == "Test Project"
        assert str(project.url) == "https://example.com/"
        assert project.status == "active"
        assert project.test_count == 0
        assert project.retention_days == 30
        assert project.max_test_files == 100
        assert isinstance(project.browser_config, BrowserConfig)
        assert project.metadata == {}
        assert project.last_execution is None

    def test_project_creation_with_custom_values(self) -> None:
        """Test project creation with custom values."""
        browser_config = BrowserConfig(
            browser="firefox",
            headless=False,
            viewport=ViewportSize(width=1920, height=1080),
        )

        metadata = {"team": "qa", "environment": "staging"}

        project = Project(
            name="Custom Project",
            url="https://staging.example.com",
            status="paused",
            browser_config=browser_config,
            metadata=metadata,
            retention_days=60,
            max_test_files=200,
        )

        assert project.name == "Custom Project"
        assert str(project.url) == "https://staging.example.com/"
        assert project.status == "paused"
        assert project.browser_config.browser == "firefox"
        assert project.browser_config.headless is False
        assert project.browser_config.viewport.width == 1920
        assert project.metadata == metadata
        assert project.retention_days == 60
        assert project.max_test_files == 200

    def test_project_name_validation(self) -> None:
        """Test project name validation rules."""
        # Empty name should fail
        with pytest.raises(ValidationError):
            Project(name="", url="https://example.com")

        # Name too long should fail
        long_name = "a" * 101
        with pytest.raises(ValidationError):
            Project(name=long_name, url="https://example.com")

        # Valid name should pass
        project = Project(name="Valid Name", url="https://example.com")
        assert project.name == "Valid Name"

    def test_project_url_validation(self) -> None:
        """Test project URL validation rules."""
        # Invalid URL should fail
        with pytest.raises(ValidationError):
            Project(name="Test", url="invalid-url")

        # Valid URLs should pass
        valid_urls = [
            "https://example.com",
            "http://localhost:3000",
            "https://app.staging.example.com/path",
        ]

        for url in valid_urls:
            project = Project(name="Test", url=url)
            assert str(project.url) == url if url.endswith("/") else f"{url}/"

    def test_project_status_validation(self) -> None:
        """Test project status validation rules."""
        valid_statuses = ["active", "archived", "paused"]

        for status in valid_statuses:
            project = Project(name="Test", url="https://example.com", status=status)
            assert project.status == status

        # Invalid status should fail
        with pytest.raises(ValidationError):
            Project(name="Test", url="https://example.com", status="invalid")

    def test_project_retention_validation(self) -> None:
        """Test project retention days validation."""
        # Valid retention days
        project = Project(name="Test", url="https://example.com", retention_days=90)
        assert project.retention_days == 90

        # Too low should fail
        with pytest.raises(ValidationError):
            Project(name="Test", url="https://example.com", retention_days=0)

        # Too high should fail
        with pytest.raises(ValidationError):
            Project(name="Test", url="https://example.com", retention_days=400)

    def test_project_max_test_files_validation(self) -> None:
        """Test project max test files validation."""
        # Valid max test files
        project = Project(name="Test", url="https://example.com", max_test_files=500)
        assert project.max_test_files == 500

        # Too low should fail
        with pytest.raises(ValidationError):
            Project(name="Test", url="https://example.com", max_test_files=0)

        # Too high should fail
        with pytest.raises(ValidationError):
            Project(name="Test", url="https://example.com", max_test_files=2000)

    def test_project_test_count_validation(self) -> None:
        """Test project test count validation."""
        # Valid test count
        project = Project(name="Test", url="https://example.com", test_count=10)
        assert project.test_count == 10

        # Negative should fail
        with pytest.raises(ValidationError):
            Project(name="Test", url="https://example.com", test_count=-1)

    def test_project_timestamps(self) -> None:
        """Test that project timestamps are set correctly."""
        before = datetime.now(UTC)
        project = Project(name="Test", url="https://example.com")
        after = datetime.now(UTC)

        assert before <= project.created_at <= after
        assert before <= project.updated_at <= after
        # Timestamps should be very close (within 1 second)
        time_diff = abs((project.updated_at - project.created_at).total_seconds())
        assert time_diff < 1.0

    def test_project_id_generation(self) -> None:
        """Test that project IDs are generated as UUIDs."""
        project1 = Project(name="Test 1", url="https://example.com")
        project2 = Project(name="Test 2", url="https://example.com")

        # IDs should be different
        assert project1.id != project2.id

        # IDs should be valid UUIDs
        from uuid import UUID

        UUID(project1.id)  # Should not raise
        UUID(project2.id)  # Should not raise

    def test_project_serialization(self) -> None:
        """Test project serialization to JSON."""
        project = Project(
            name="Serialization Test",
            url="https://example.com",
            metadata={"key": "value"},
        )

        # Test model_dump
        data = project.model_dump()
        assert data["name"] == "Serialization Test"
        assert str(data["url"]) == "https://example.com/"
        assert data["metadata"] == {"key": "value"}

        # Test JSON mode
        json_data = project.model_dump(mode="json")
        assert isinstance(json_data["created_at"], str)
        assert isinstance(json_data["updated_at"], str)

    def test_project_deserialization(self) -> None:
        """Test project deserialization from JSON."""
        data = {
            "name": "Deserialization Test",
            "url": "https://example.com",
            "status": "paused",
            "metadata": {"environment": "test"},
            "browser_config": {
                "browser": "webkit",
                "headless": True,
                "viewport": {"width": 800, "height": 600},
            },
        }

        project = Project.model_validate(data)

        assert project.name == "Deserialization Test"
        assert str(project.url) == "https://example.com/"
        assert project.status == "paused"
        assert project.metadata == {"environment": "test"}
        assert project.browser_config.browser == "webkit"
        assert project.browser_config.viewport.width == 800
