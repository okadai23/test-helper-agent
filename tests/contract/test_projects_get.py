"""Contract tests for GET /api/v1/projects/{id} endpoint."""

from __future__ import annotations

from typing import Any
from uuid import UUID, uuid4

from fastapi import status
from fastapi.testclient import TestClient


class TestGetProjectContract:
    """Contract tests for project retrieval endpoint."""

    def test_get_project_success(
        self,
        mock_project_data: dict[str, Any],
    ) -> None:
        """Test successful project retrieval with valid ID.

        This test MUST FAIL until the API endpoint is implemented.
        It verifies the contract for GET /api/v1/projects/{id}.
        """
        # This will fail because the API endpoint doesn't exist yet
        from test_helper.e2e.api.app import app

        client = TestClient(app)

        # First create a project
        create_response = client.post(
            "/api/v1/projects",
            json=mock_project_data,
        )
        assert create_response.status_code == status.HTTP_201_CREATED
        project = create_response.json()
        project_id = project["id"]

        # Then retrieve it
        response = client.get(f"/api/v1/projects/{project_id}")

        # Verify response status
        assert response.status_code == status.HTTP_200_OK

        # Verify response structure
        retrieved_project = response.json()
        assert "id" in retrieved_project
        assert "name" in retrieved_project
        assert "url" in retrieved_project
        assert "created_at" in retrieved_project
        assert "updated_at" in retrieved_project
        assert "status" in retrieved_project
        assert "browser_config" in retrieved_project
        assert "test_count" in retrieved_project

        # Verify data types
        assert isinstance(UUID(retrieved_project["id"]), UUID)
        assert isinstance(retrieved_project["name"], str)
        assert isinstance(retrieved_project["url"], str)
        assert isinstance(retrieved_project["status"], str)
        assert isinstance(retrieved_project["test_count"], int)

        # Verify data values match created project
        assert retrieved_project["id"] == project["id"]
        assert retrieved_project["name"] == project["name"]
        assert retrieved_project["url"] == project["url"]
        assert retrieved_project["status"] == project["status"]

    def test_get_project_not_found(self) -> None:
        """Test project retrieval fails with non-existent ID.

        This test MUST FAIL until 404 handling is implemented.
        """
        from test_helper.e2e.api.app import app

        client = TestClient(app)

        non_existent_id = str(uuid4())
        response = client.get(f"/api/v1/projects/{non_existent_id}")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        error = response.json()
        assert "error" in error
        assert "message" in error
        assert "not found" in error["message"].lower()

    def test_get_project_invalid_uuid(self) -> None:
        """Test project retrieval fails with invalid UUID format.

        This test MUST FAIL until UUID validation is implemented.
        """
        from test_helper.e2e.api.app import app

        client = TestClient(app)

        invalid_uuid = "invalid-uuid-format"
        response = client.get(f"/api/v1/projects/{invalid_uuid}")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        error = response.json()
        assert "error" in error
        assert (
            "uuid" in error["message"].lower() or "invalid" in error["message"].lower()
        )

    def test_get_project_includes_metadata(
        self,
        mock_project_data: dict[str, Any],
    ) -> None:
        """Test that retrieved project includes all metadata.

        This test MUST FAIL until metadata handling is implemented.
        """
        from test_helper.e2e.api.app import app

        client = TestClient(app)

        # Create project with metadata
        project_data = mock_project_data.copy()
        project_data["metadata"] = {
            "environment": "test",
            "team": "qa",
            "priority": "high",
        }

        create_response = client.post(
            "/api/v1/projects",
            json=project_data,
        )
        assert create_response.status_code == status.HTTP_201_CREATED
        project = create_response.json()
        project_id = project["id"]

        # Retrieve project
        response = client.get(f"/api/v1/projects/{project_id}")
        assert response.status_code == status.HTTP_200_OK

        retrieved_project = response.json()
        assert "metadata" in retrieved_project
        metadata = retrieved_project["metadata"]
        assert metadata["environment"] == "test"
        assert metadata["team"] == "qa"
        assert metadata["priority"] == "high"

    def test_get_project_includes_browser_config(
        self,
        mock_project_data: dict[str, Any],
    ) -> None:
        """Test that retrieved project includes browser configuration.

        This test MUST FAIL until browser config handling is implemented.
        """
        from test_helper.e2e.api.app import app

        client = TestClient(app)

        # Create project with custom browser config
        project_data = mock_project_data.copy()
        project_data["browser_config"] = {
            "browser": "firefox",
            "headless": False,
            "viewport": {"width": 1920, "height": 1080},
            "locale": "ja-JP",
            "timezone": "Asia/Tokyo",
        }

        create_response = client.post(
            "/api/v1/projects",
            json=project_data,
        )
        assert create_response.status_code == status.HTTP_201_CREATED
        project = create_response.json()
        project_id = project["id"]

        # Retrieve project
        response = client.get(f"/api/v1/projects/{project_id}")
        assert response.status_code == status.HTTP_200_OK

        retrieved_project = response.json()
        assert "browser_config" in retrieved_project
        browser_config = retrieved_project["browser_config"]
        assert browser_config["browser"] == "firefox"
        assert browser_config["headless"] is False
        assert browser_config["viewport"]["width"] == 1920
        assert browser_config["viewport"]["height"] == 1080
        assert browser_config["locale"] == "ja-JP"
        assert browser_config["timezone"] == "Asia/Tokyo"

    def test_get_project_includes_statistics(
        self,
        mock_project_data: dict[str, Any],
    ) -> None:
        """Test that retrieved project includes usage statistics.

        This test MUST FAIL until statistics tracking is implemented.
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

        # Retrieve project
        response = client.get(f"/api/v1/projects/{project_id}")
        assert response.status_code == status.HTTP_200_OK

        retrieved_project = response.json()

        # Verify initial statistics
        assert retrieved_project["test_count"] == 0
        assert "last_execution" in retrieved_project
        assert retrieved_project["last_execution"] is None  # No executions yet

    def test_get_project_response_format(
        self,
        mock_project_data: dict[str, Any],
    ) -> None:
        """Test that project response follows expected JSON format.

        This test MUST FAIL until response formatting is implemented.
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

        # Retrieve project
        response = client.get(f"/api/v1/projects/{project_id}")
        assert response.status_code == status.HTTP_200_OK

        # Verify content type
        assert response.headers["content-type"] == "application/json"

        # Verify JSON structure is valid
        project_data = response.json()
        assert isinstance(project_data, dict)

        # Verify required fields exist and have correct types
        required_fields = {
            "id": str,
            "name": str,
            "url": str,
            "created_at": str,
            "updated_at": str,
            "status": str,
            "browser_config": dict,
            "test_count": int,
            "metadata": dict,
        }

        for field, expected_type in required_fields.items():
            assert field in project_data
            assert isinstance(project_data[field], expected_type)

        # Verify datetime format (ISO 8601)
        import datetime

        datetime.datetime.fromisoformat(
            project_data["created_at"].replace("Z", "+00:00"),
        )
        datetime.datetime.fromisoformat(
            project_data["updated_at"].replace("Z", "+00:00"),
        )
