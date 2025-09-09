"""Contract tests for PATCH /api/v1/projects/{id} endpoint."""

from __future__ import annotations

from typing import Any
from uuid import uuid4

from fastapi import status
from fastapi.testclient import TestClient


class TestUpdateProjectContract:
    """Contract tests for project update endpoint."""

    def test_update_project_name_success(
        self,
        mock_project_data: dict[str, Any],
    ) -> None:
        """Test successful project name update.

        This test MUST FAIL until the API endpoint is implemented.
        It verifies the contract for PATCH /api/v1/projects/{id}.
        """
        # This will fail because the API endpoint doesn't exist yet
        from test_helper.e2e.api.app import app

        client = TestClient(app)

        # Create project
        create_response = client.post(
            "/api/v1/projects",
            json=mock_project_data,
        )
        assert create_response.status_code == status.HTTP_201_CREATED
        project = create_response.json()
        project_id = project["id"]
        original_name = project["name"]

        # Update project name
        update_data = {"name": "Updated Project Name"}
        response = client.patch(
            f"/api/v1/projects/{project_id}",
            json=update_data,
        )

        # Verify response status
        assert response.status_code == status.HTTP_200_OK

        # Verify response structure
        updated_project = response.json()
        assert updated_project["id"] == project_id
        assert updated_project["name"] == "Updated Project Name"
        assert updated_project["name"] != original_name

        # Verify updated_at timestamp changed
        assert updated_project["updated_at"] != project["updated_at"]

        # Verify other fields unchanged
        assert updated_project["url"] == project["url"]
        assert updated_project["status"] == project["status"]

    def test_update_project_url_success(
        self,
        mock_project_data: dict[str, Any],
    ) -> None:
        """Test successful project URL update.

        This test MUST FAIL until URL update handling is implemented.
        """
        from test_helper.e2e.api.app import app

        client = TestClient(app)

        # Create project
        create_response = client.post(
            "/api/v1/projects",
            json=mock_project_data,
        )
        assert create_response.status_code == status.HTTP_201_CREATED
        project = create_response.json()
        project_id = project["id"]

        # Update project URL
        new_url = "https://updated-example.com"
        update_data = {"url": new_url}
        response = client.patch(
            f"/api/v1/projects/{project_id}",
            json=update_data,
        )

        assert response.status_code == status.HTTP_200_OK
        updated_project = response.json()
        assert updated_project["url"] == new_url

    def test_update_project_status_success(
        self,
        mock_project_data: dict[str, Any],
    ) -> None:
        """Test successful project status update.

        This test MUST FAIL until status update handling is implemented.
        """
        from test_helper.e2e.api.app import app

        client = TestClient(app)

        # Create project (defaults to 'active')
        create_response = client.post(
            "/api/v1/projects",
            json=mock_project_data,
        )
        assert create_response.status_code == status.HTTP_201_CREATED
        project = create_response.json()
        project_id = project["id"]
        assert project["status"] == "active"

        # Update project status to paused
        update_data = {"status": "paused"}
        response = client.patch(
            f"/api/v1/projects/{project_id}",
            json=update_data,
        )

        assert response.status_code == status.HTTP_200_OK
        updated_project = response.json()
        assert updated_project["status"] == "paused"

    def test_update_project_browser_config_success(
        self,
        mock_project_data: dict[str, Any],
    ) -> None:
        """Test successful browser configuration update.

        This test MUST FAIL until browser config update is implemented.
        """
        from test_helper.e2e.api.app import app

        client = TestClient(app)

        # Create project
        create_response = client.post(
            "/api/v1/projects",
            json=mock_project_data,
        )
        assert create_response.status_code == status.HTTP_201_CREATED
        project = create_response.json()
        project_id = project["id"]

        # Update browser configuration
        new_browser_config = {
            "browser": "webkit",
            "headless": False,
            "viewport": {"width": 1440, "height": 900},
            "locale": "en-GB",
            "timezone": "Europe/London",
        }
        update_data = {"browser_config": new_browser_config}
        response = client.patch(
            f"/api/v1/projects/{project_id}",
            json=update_data,
        )

        assert response.status_code == status.HTTP_200_OK
        updated_project = response.json()
        browser_config = updated_project["browser_config"]
        assert browser_config["browser"] == "webkit"
        assert browser_config["headless"] is False
        assert browser_config["viewport"]["width"] == 1440
        assert browser_config["locale"] == "en-GB"

    def test_update_project_metadata_success(
        self,
        mock_project_data: dict[str, Any],
    ) -> None:
        """Test successful metadata update.

        This test MUST FAIL until metadata update handling is implemented.
        """
        from test_helper.e2e.api.app import app

        client = TestClient(app)

        # Create project with initial metadata
        project_data = mock_project_data.copy()
        project_data["metadata"] = {"initial": "value"}

        create_response = client.post(
            "/api/v1/projects",
            json=project_data,
        )
        assert create_response.status_code == status.HTTP_201_CREATED
        project = create_response.json()
        project_id = project["id"]

        # Update metadata
        new_metadata = {
            "environment": "production",
            "team": "frontend",
            "updated": True,
        }
        update_data = {"metadata": new_metadata}
        response = client.patch(
            f"/api/v1/projects/{project_id}",
            json=update_data,
        )

        assert response.status_code == status.HTTP_200_OK
        updated_project = response.json()
        metadata = updated_project["metadata"]
        assert metadata["environment"] == "production"
        assert metadata["team"] == "frontend"
        assert metadata["updated"] is True

    def test_update_project_multiple_fields(
        self,
        mock_project_data: dict[str, Any],
    ) -> None:
        """Test updating multiple fields in single request.

        This test MUST FAIL until multi-field updates are implemented.
        """
        from test_helper.e2e.api.app import app

        client = TestClient(app)

        # Create project
        create_response = client.post(
            "/api/v1/projects",
            json=mock_project_data,
        )
        assert create_response.status_code == status.HTTP_201_CREATED
        project = create_response.json()
        project_id = project["id"]

        # Update multiple fields
        update_data = {
            "name": "Multi-field Update Test",
            "status": "paused",
            "metadata": {"updated_fields": "multiple"},
        }
        response = client.patch(
            f"/api/v1/projects/{project_id}",
            json=update_data,
        )

        assert response.status_code == status.HTTP_200_OK
        updated_project = response.json()
        assert updated_project["name"] == "Multi-field Update Test"
        assert updated_project["status"] == "paused"
        assert updated_project["metadata"]["updated_fields"] == "multiple"

    def test_update_project_not_found(self) -> None:
        """Test project update fails with non-existent ID.

        This test MUST FAIL until 404 handling is implemented.
        """
        from test_helper.e2e.api.app import app

        client = TestClient(app)

        non_existent_id = str(uuid4())
        update_data = {"name": "Should Not Work"}
        response = client.patch(
            f"/api/v1/projects/{non_existent_id}",
            json=update_data,
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        error = response.json()
        assert "error" in error
        assert "not found" in error["message"].lower()

    def test_update_project_invalid_uuid(self) -> None:
        """Test project update fails with invalid UUID format.

        This test MUST FAIL until UUID validation is implemented.
        """
        from test_helper.e2e.api.app import app

        client = TestClient(app)

        invalid_uuid = "invalid-uuid-format"
        update_data = {"name": "Should Not Work"}
        response = client.patch(
            f"/api/v1/projects/{invalid_uuid}",
            json=update_data,
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        error = response.json()
        assert "error" in error

    def test_update_project_invalid_name_length(
        self,
        mock_project_data: dict[str, Any],
    ) -> None:
        """Test project update fails with invalid name length.

        This test MUST FAIL until name validation is implemented.
        """
        from test_helper.e2e.api.app import app

        client = TestClient(app)

        # Create project
        create_response = client.post(
            "/api/v1/projects",
            json=mock_project_data,
        )
        assert create_response.status_code == status.HTTP_201_CREATED
        project = create_response.json()
        project_id = project["id"]

        # Try to update with name too long
        long_name = "a" * 101  # Max length is 100
        update_data = {"name": long_name}
        response = client.patch(
            f"/api/v1/projects/{project_id}",
            json=update_data,
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        error = response.json()
        assert "error" in error
        assert "name" in error["message"].lower()

    def test_update_project_invalid_url_format(
        self,
        mock_project_data: dict[str, Any],
    ) -> None:
        """Test project update fails with invalid URL format.

        This test MUST FAIL until URL validation is implemented.
        """
        from test_helper.e2e.api.app import app

        client = TestClient(app)

        # Create project
        create_response = client.post(
            "/api/v1/projects",
            json=mock_project_data,
        )
        assert create_response.status_code == status.HTTP_201_CREATED
        project = create_response.json()
        project_id = project["id"]

        # Try to update with invalid URL
        update_data = {"url": "invalid-url-format"}
        response = client.patch(
            f"/api/v1/projects/{project_id}",
            json=update_data,
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        error = response.json()
        assert "error" in error
        assert "url" in error["message"].lower()

    def test_update_project_invalid_status(
        self,
        mock_project_data: dict[str, Any],
    ) -> None:
        """Test project update fails with invalid status value.

        This test MUST FAIL until status validation is implemented.
        """
        from test_helper.e2e.api.app import app

        client = TestClient(app)

        # Create project
        create_response = client.post(
            "/api/v1/projects",
            json=mock_project_data,
        )
        assert create_response.status_code == status.HTTP_201_CREATED
        project = create_response.json()
        project_id = project["id"]

        # Try to update with invalid status
        update_data = {"status": "invalid_status"}
        response = client.patch(
            f"/api/v1/projects/{project_id}",
            json=update_data,
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        error = response.json()
        assert "error" in error
        assert "status" in error["message"].lower()

    def test_update_project_invalid_browser_type(
        self,
        mock_project_data: dict[str, Any],
    ) -> None:
        """Test project update fails with invalid browser type.

        This test MUST FAIL until browser type validation is implemented.
        """
        from test_helper.e2e.api.app import app

        client = TestClient(app)

        # Create project
        create_response = client.post(
            "/api/v1/projects",
            json=mock_project_data,
        )
        assert create_response.status_code == status.HTTP_201_CREATED
        project = create_response.json()
        project_id = project["id"]

        # Try to update with invalid browser type
        invalid_browser_config = {
            "browser": "invalid_browser",  # Not chromium, firefox, or webkit
            "headless": True,
        }
        update_data = {"browser_config": invalid_browser_config}
        response = client.patch(
            f"/api/v1/projects/{project_id}",
            json=update_data,
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        error = response.json()
        assert "error" in error
        assert "browser" in error["message"].lower()

    def test_update_project_empty_request_body(
        self,
        mock_project_data: dict[str, Any],
    ) -> None:
        """Test project update with empty request body.

        This test MUST FAIL until empty body handling is implemented.
        """
        from test_helper.e2e.api.app import app

        client = TestClient(app)

        # Create project
        create_response = client.post(
            "/api/v1/projects",
            json=mock_project_data,
        )
        assert create_response.status_code == status.HTTP_201_CREATED
        project = create_response.json()
        project_id = project["id"]

        # Try to update with empty body
        response = client.patch(
            f"/api/v1/projects/{project_id}",
            json={},
        )

        # Empty body should be valid but result in no changes
        assert response.status_code == status.HTTP_200_OK
        updated_project = response.json()

        # Verify no changes except updated_at timestamp
        assert updated_project["name"] == project["name"]
        assert updated_project["url"] == project["url"]
        assert updated_project["status"] == project["status"]
