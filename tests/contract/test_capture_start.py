"""Contract tests for POST /api/v1/projects/{id}/capture endpoint."""

from __future__ import annotations

from typing import Any
from uuid import UUID, uuid4

from fastapi import status
from fastapi.testclient import TestClient


class TestStartCaptureContract:
    """Contract tests for capture session start endpoint."""

    def test_start_capture_success(
        self,
        mock_project_data: dict[str, Any],
    ) -> None:
        """Test successful capture session start.

        This test MUST FAIL until the API endpoint is implemented.
        It verifies the contract for POST /api/v1/projects/{id}/capture.
        """
        # This will fail because the API endpoint doesn't exist yet
        from test_helper.e2e.api.app import app

        client = TestClient(app)

        # Create project first
        create_response = client.post(
            "/api/v1/projects",
            json=mock_project_data,
        )
        assert create_response.status_code == status.HTTP_201_CREATED
        project = create_response.json()
        project_id = project["id"]

        # Start capture session
        capture_request = {
            "browser_config": {
                "browser": "chromium",
                "headless": True,
                "viewport": {"width": 1280, "height": 720},
            },
        }
        response = client.post(
            f"/api/v1/projects/{project_id}/capture",
            json=capture_request,
        )

        # Verify response status
        assert response.status_code == status.HTTP_201_CREATED

        # Verify response structure
        capture_session = response.json()
        assert "id" in capture_session
        assert "project_id" in capture_session
        assert "started_at" in capture_session
        assert "ended_at" in capture_session
        assert "status" in capture_session
        assert "browser_session_id" in capture_session
        assert "captured_interactions" in capture_session

        # Verify data types
        assert isinstance(UUID(capture_session["id"]), UUID)
        assert isinstance(UUID(capture_session["project_id"]), UUID)
        assert isinstance(capture_session["browser_session_id"], str)
        assert isinstance(capture_session["captured_interactions"], list)

        # Verify data values
        assert capture_session["project_id"] == project_id
        assert capture_session["status"] == "active"
        assert capture_session["ended_at"] is None  # Still active
        assert capture_session["captured_interactions"] == []  # Empty initially

    def test_start_capture_with_custom_browser_config(
        self,
        mock_project_data: dict[str, Any],
    ) -> None:
        """Test capture start with custom browser configuration.

        This test MUST FAIL until browser config handling is implemented.
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

        # Start capture with custom browser config
        capture_request = {
            "browser_config": {
                "browser": "firefox",
                "headless": False,
                "viewport": {"width": 1920, "height": 1080},
                "locale": "ja-JP",
                "timezone": "Asia/Tokyo",
            },
        }
        response = client.post(
            f"/api/v1/projects/{project_id}/capture",
            json=capture_request,
        )

        assert response.status_code == status.HTTP_201_CREATED
        capture_session = response.json()

        # Browser config should be applied but not necessarily returned in response
        # The actual browser session should use these settings
        assert capture_session["status"] == "active"
        assert capture_session["browser_session_id"] is not None

    def test_start_capture_project_not_found(self) -> None:
        """Test capture start fails with non-existent project.

        This test MUST FAIL until 404 handling is implemented.
        """
        from test_helper.e2e.api.app import app

        client = TestClient(app)

        non_existent_id = str(uuid4())
        capture_request = {
            "browser_config": {
                "browser": "chromium",
                "headless": True,
            },
        }
        response = client.post(
            f"/api/v1/projects/{non_existent_id}/capture",
            json=capture_request,
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        error = response.json()
        assert "error" in error
        assert "not found" in error["message"].lower()

    def test_start_capture_invalid_project_uuid(self) -> None:
        """Test capture start fails with invalid project UUID.

        This test MUST FAIL until UUID validation is implemented.
        """
        from test_helper.e2e.api.app import app

        client = TestClient(app)

        invalid_uuid = "invalid-uuid-format"
        capture_request = {
            "browser_config": {
                "browser": "chromium",
                "headless": True,
            },
        }
        response = client.post(
            f"/api/v1/projects/{invalid_uuid}/capture",
            json=capture_request,
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        error = response.json()
        assert "error" in error

    def test_start_capture_invalid_browser_type(
        self,
        mock_project_data: dict[str, Any],
    ) -> None:
        """Test capture start fails with invalid browser type.

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

        # Try to start capture with invalid browser
        capture_request = {
            "browser_config": {
                "browser": "invalid_browser",
                "headless": True,
            },
        }
        response = client.post(
            f"/api/v1/projects/{project_id}/capture",
            json=capture_request,
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        error = response.json()
        assert "error" in error
        assert "browser" in error["message"].lower()

    def test_start_capture_concurrent_session_conflict(
        self,
        mock_project_data: dict[str, Any],
    ) -> None:
        """Test capture start fails when session already active.

        This test MUST FAIL until concurrent session handling is implemented.
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

        # Start first capture session
        capture_request = {
            "browser_config": {
                "browser": "chromium",
                "headless": True,
            },
        }
        response1 = client.post(
            f"/api/v1/projects/{project_id}/capture",
            json=capture_request,
        )
        assert response1.status_code == status.HTTP_201_CREATED

        # Try to start second capture session (should conflict)
        response2 = client.post(
            f"/api/v1/projects/{project_id}/capture",
            json=capture_request,
        )
        assert response2.status_code == status.HTTP_409_CONFLICT
        error = response2.json()
        assert "error" in error
        assert (
            "active" in error["message"].lower()
            or "conflict" in error["message"].lower()
        )

    def test_start_capture_missing_browser_config(
        self,
        mock_project_data: dict[str, Any],
    ) -> None:
        """Test capture start with missing browser configuration.

        This test MUST FAIL until default browser config handling is implemented.
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

        # Start capture without browser config (should use project defaults)
        response = client.post(
            f"/api/v1/projects/{project_id}/capture",
            json={},
        )

        assert response.status_code == status.HTTP_201_CREATED
        capture_session = response.json()
        assert capture_session["status"] == "active"
        assert capture_session["browser_session_id"] is not None

    def test_start_capture_invalid_viewport_dimensions(
        self,
        mock_project_data: dict[str, Any],
    ) -> None:
        """Test capture start fails with invalid viewport dimensions.

        This test MUST FAIL until viewport validation is implemented.
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

        # Try to start capture with invalid viewport
        capture_request = {
            "browser_config": {
                "browser": "chromium",
                "headless": True,
                "viewport": {"width": -100, "height": 0},  # Invalid dimensions
            },
        }
        response = client.post(
            f"/api/v1/projects/{project_id}/capture",
            json=capture_request,
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        error = response.json()
        assert "error" in error
        assert (
            "viewport" in error["message"].lower()
            or "dimension" in error["message"].lower()
        )

    def test_start_capture_response_format(
        self,
        mock_project_data: dict[str, Any],
    ) -> None:
        """Test capture start response format compliance.

        This test MUST FAIL until proper response formatting is implemented.
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

        # Start capture
        capture_request = {
            "browser_config": {
                "browser": "chromium",
                "headless": True,
            },
        }
        response = client.post(
            f"/api/v1/projects/{project_id}/capture",
            json=capture_request,
        )

        assert response.status_code == status.HTTP_201_CREATED

        # Verify content type
        assert response.headers["content-type"] == "application/json"

        # Verify JSON structure
        capture_session = response.json()
        assert isinstance(capture_session, dict)

        # Verify required fields and types
        required_fields = {
            "id": str,
            "project_id": str,
            "started_at": str,
            "status": str,
            "browser_session_id": str,
            "captured_interactions": list,
        }

        for field, expected_type in required_fields.items():
            assert field in capture_session
            assert isinstance(capture_session[field], expected_type)

        # Verify datetime format (ISO 8601)
        import datetime

        datetime.datetime.fromisoformat(
            capture_session["started_at"].replace("Z", "+00:00"),
        )

    def test_start_capture_project_archived_status(
        self,
        mock_project_data: dict[str, Any],
    ) -> None:
        """Test capture start fails for archived project.

        This test MUST FAIL until project status validation is implemented.
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

        # Archive the project
        patch_response = client.patch(
            f"/api/v1/projects/{project_id}",
            json={"status": "archived"},
        )
        assert patch_response.status_code == status.HTTP_200_OK

        # Try to start capture on archived project
        capture_request = {
            "browser_config": {
                "browser": "chromium",
                "headless": True,
            },
        }
        response = client.post(
            f"/api/v1/projects/{project_id}/capture",
            json=capture_request,
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        error = response.json()
        assert "error" in error
        assert (
            "archived" in error["message"].lower()
            or "inactive" in error["message"].lower()
        )
