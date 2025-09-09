"""Contract tests for POST /api/v1/projects endpoint."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import status
from fastapi.testclient import TestClient


class TestCreateProjectContract:
    """Contract tests for project creation endpoint."""

    def test_create_project_success(
        self,
        mock_project_data: dict[str, Any],
    ) -> None:
        """Test successful project creation with valid data.

        This test MUST FAIL until the API endpoint is implemented.
        It verifies the contract for POST /api/v1/projects.
        """
        # This will fail because the API endpoint doesn't exist yet
        from test_helper.e2e.api.app import app

        client = TestClient(app)

        response = client.post(
            "/api/v1/projects",
            json=mock_project_data,
        )

        # Verify response status
        assert response.status_code == status.HTTP_201_CREATED

        # Verify response structure
        project = response.json()
        assert "id" in project
        assert "name" in project
        assert "url" in project
        assert "created_at" in project
        assert "updated_at" in project
        assert "status" in project
        assert "browser_config" in project
        assert "test_count" in project

        # Verify data types
        assert isinstance(UUID(project["id"]), UUID)
        assert isinstance(project["name"], str)
        assert isinstance(project["url"], str)
        assert isinstance(project["status"], str)
        assert isinstance(project["test_count"], int)

        # Verify data values
        assert project["name"] == mock_project_data["name"]
        assert project["url"] == mock_project_data["url"]
        assert project["status"] == "active"
        assert project["test_count"] == 0

    def test_create_project_missing_required_fields(self) -> None:
        """Test project creation fails with missing required fields.

        This test MUST FAIL until validation is implemented.
        """
        from test_helper.e2e.api.app import app

        client = TestClient(app)

        # Missing name
        response = client.post(
            "/api/v1/projects",
            json={"url": "https://example.com"},
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        error = response.json()
        assert "error" in error
        assert "name" in error["message"].lower()

        # Missing URL
        response = client.post(
            "/api/v1/projects",
            json={"name": "Test Project"},
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        error = response.json()
        assert "error" in error
        assert "url" in error["message"].lower()

    def test_create_project_invalid_url(self) -> None:
        """Test project creation fails with invalid URL.

        This test MUST FAIL until URL validation is implemented.
        """
        from test_helper.e2e.api.app import app

        client = TestClient(app)

        response = client.post(
            "/api/v1/projects",
            json={
                "name": "Test Project",
                "url": "invalid-url",
            },
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        error = response.json()
        assert "error" in error
        assert "url" in error["message"].lower()

    def test_create_project_name_too_long(self) -> None:
        """Test project creation fails with name too long.

        This test MUST FAIL until name length validation is implemented.
        """
        from test_helper.e2e.api.app import app

        client = TestClient(app)

        long_name = "a" * 101  # Max length is 100
        response = client.post(
            "/api/v1/projects",
            json={
                "name": long_name,
                "url": "https://example.com",
            },
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        error = response.json()
        assert "error" in error
        assert "name" in error["message"].lower()

    def test_create_project_duplicate_name(
        self,
        mock_project_data: dict[str, Any],
    ) -> None:
        """Test project creation fails with duplicate name.

        This test MUST FAIL until duplicate name checking is implemented.
        """
        from test_helper.e2e.api.app import app

        client = TestClient(app)

        # Create first project
        response1 = client.post(
            "/api/v1/projects",
            json=mock_project_data,
        )
        assert response1.status_code == status.HTTP_201_CREATED

        # Try to create second project with same name
        response2 = client.post(
            "/api/v1/projects",
            json=mock_project_data,
        )
        assert response2.status_code == status.HTTP_409_CONFLICT
        error = response2.json()
        assert "error" in error
        assert (
            "name" in error["message"].lower() or "exists" in error["message"].lower()
        )

    def test_create_project_with_browser_config(
        self,
        mock_project_data: dict[str, Any],
    ) -> None:
        """Test project creation with custom browser configuration.

        This test MUST FAIL until browser config handling is implemented.
        """
        from test_helper.e2e.api.app import app

        client = TestClient(app)

        project_data = mock_project_data.copy()
        project_data["browser_config"] = {
            "browser": "firefox",
            "headless": False,
            "viewport": {"width": 1920, "height": 1080},
            "locale": "ja-JP",
            "timezone": "Asia/Tokyo",
        }

        response = client.post(
            "/api/v1/projects",
            json=project_data,
        )

        assert response.status_code == status.HTTP_201_CREATED
        project = response.json()

        browser_config = project["browser_config"]
        assert browser_config["browser"] == "firefox"
        assert browser_config["headless"] is False
        assert browser_config["viewport"]["width"] == 1920
        assert browser_config["viewport"]["height"] == 1080
        assert browser_config["locale"] == "ja-JP"
        assert browser_config["timezone"] == "Asia/Tokyo"

    def test_create_project_with_metadata(
        self,
        mock_project_data: dict[str, Any],
    ) -> None:
        """Test project creation with custom metadata.

        This test MUST FAIL until metadata handling is implemented.
        """
        from test_helper.e2e.api.app import app

        client = TestClient(app)

        project_data = mock_project_data.copy()
        project_data["metadata"] = {
            "environment": "staging",
            "team": "qa",
            "priority": "high",
        }

        response = client.post(
            "/api/v1/projects",
            json=project_data,
        )

        assert response.status_code == status.HTTP_201_CREATED
        project = response.json()

        metadata = project["metadata"]
        assert metadata["environment"] == "staging"
        assert metadata["team"] == "qa"
        assert metadata["priority"] == "high"

    def test_create_project_invalid_browser_type(
        self,
        mock_project_data: dict[str, Any],
    ) -> None:
        """Test project creation fails with invalid browser type.

        This test MUST FAIL until browser type validation is implemented.
        """
        from test_helper.e2e.api.app import app

        client = TestClient(app)

        project_data = mock_project_data.copy()
        project_data["browser_config"] = {
            "browser": "invalid_browser",  # Not chromium, firefox, or webkit
            "headless": True,
        }

        response = client.post(
            "/api/v1/projects",
            json=project_data,
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        error = response.json()
        assert "error" in error
        assert "browser" in error["message"].lower()
