"""Contract tests for DELETE /api/v1/projects/{id} endpoint."""

from __future__ import annotations

from typing import Any
from uuid import uuid4

from fastapi import status
from fastapi.testclient import TestClient


class TestDeleteProjectContract:
    """Contract tests for project deletion endpoint."""

    def test_delete_project_success(
        self,
        mock_project_data: dict[str, Any],
    ) -> None:
        """Test successful project deletion.

        This test MUST FAIL until the API endpoint is implemented.
        It verifies the contract for DELETE /api/v1/projects/{id}.
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

        # Delete project
        response = client.delete(f"/api/v1/projects/{project_id}")

        # Verify response status (204 No Content)
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify no response body
        assert response.content == b""

        # Verify project is actually deleted by trying to retrieve it
        get_response = client.get(f"/api/v1/projects/{project_id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_project_not_found(self) -> None:
        """Test project deletion fails with non-existent ID.

        This test MUST FAIL until 404 handling is implemented.
        """
        from test_helper.e2e.api.app import app

        client = TestClient(app)

        non_existent_id = str(uuid4())
        response = client.delete(f"/api/v1/projects/{non_existent_id}")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        error = response.json()
        assert "error" in error
        assert "message" in error
        assert "not found" in error["message"].lower()

    def test_delete_project_invalid_uuid(self) -> None:
        """Test project deletion fails with invalid UUID format.

        This test MUST FAIL until UUID validation is implemented.
        """
        from test_helper.e2e.api.app import app

        client = TestClient(app)

        invalid_uuid = "invalid-uuid-format"
        response = client.delete(f"/api/v1/projects/{invalid_uuid}")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        error = response.json()
        assert "error" in error
        assert (
            "uuid" in error["message"].lower() or "invalid" in error["message"].lower()
        )

    def test_delete_project_with_tests_cascade(
        self,
        mock_project_data: dict[str, Any],
    ) -> None:
        """Test project deletion cascades to associated tests.

        This test MUST FAIL until cascade deletion is implemented.
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

        # TODO: Create some test scenarios for this project
        # This would require implementing test creation endpoints first
        # For now, we just verify the project deletion works

        # Delete project
        response = client.delete(f"/api/v1/projects/{project_id}")
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify project is deleted
        get_response = client.get(f"/api/v1/projects/{project_id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

        # TODO: Verify associated tests are also deleted
        # This test will be enhanced once test management endpoints exist

    def test_delete_project_cleans_up_files(
        self,
        mock_project_data: dict[str, Any],
    ) -> None:
        """Test project deletion cleans up associated files.

        This test MUST FAIL until file cleanup is implemented.
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

        # Delete project
        response = client.delete(f"/api/v1/projects/{project_id}")
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # TODO: Verify project directory is cleaned up
        # This would require access to the storage system
        # For now, we just verify the HTTP contract

    def test_delete_project_idempotent(
        self,
        mock_project_data: dict[str, Any],
    ) -> None:
        """Test project deletion is idempotent.

        This test MUST FAIL until idempotent deletion is implemented.
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

        # Delete project first time
        response1 = client.delete(f"/api/v1/projects/{project_id}")
        assert response1.status_code == status.HTTP_204_NO_CONTENT

        # Delete project second time (should be idempotent)
        response2 = client.delete(f"/api/v1/projects/{project_id}")
        # Some implementations return 404, others return 204
        # We'll accept either as valid for idempotent DELETE
        assert response2.status_code in (
            status.HTTP_204_NO_CONTENT,
            status.HTTP_404_NOT_FOUND,
        )

    def test_delete_project_prevents_access_to_subresources(
        self,
        mock_project_data: dict[str, Any],
    ) -> None:
        """Test that deleting project prevents access to its subresources.

        This test MUST FAIL until subresource cleanup is implemented.
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

        # Delete project
        response = client.delete(f"/api/v1/projects/{project_id}")
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify access to project subresources returns 404
        subresource_endpoints = [
            f"/api/v1/projects/{project_id}/tests",
            f"/api/v1/projects/{project_id}/capture",
            f"/api/v1/projects/{project_id}/execute",
            f"/api/v1/projects/{project_id}/history",
        ]

        for endpoint in subresource_endpoints:
            subresource_response = client.get(endpoint)
            assert subresource_response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_project_response_headers(
        self,
        mock_project_data: dict[str, Any],
    ) -> None:
        """Test project deletion response headers.

        This test MUST FAIL until proper headers are implemented.
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

        # Delete project
        response = client.delete(f"/api/v1/projects/{project_id}")

        # Verify response status and headers
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert response.content == b""

        # Verify no content-type header for 204 responses
        assert "content-type" not in response.headers.keys()

    def test_delete_multiple_projects_independent(
        self,
        mock_project_data: dict[str, Any],
    ) -> None:
        """Test that deleting one project doesn't affect others.

        This test MUST FAIL until proper project isolation is implemented.
        """
        from test_helper.e2e.api.app import app

        client = TestClient(app)

        # Create two projects
        project1_data = mock_project_data.copy()
        project1_data["name"] = "Project 1"
        create_response1 = client.post(
            "/api/v1/projects",
            json=project1_data,
        )
        assert create_response1.status_code == status.HTTP_201_CREATED
        project1 = create_response1.json()
        project1_id = project1["id"]

        project2_data = mock_project_data.copy()
        project2_data["name"] = "Project 2"
        create_response2 = client.post(
            "/api/v1/projects",
            json=project2_data,
        )
        assert create_response2.status_code == status.HTTP_201_CREATED
        project2 = create_response2.json()
        project2_id = project2["id"]

        # Delete first project
        delete_response = client.delete(f"/api/v1/projects/{project1_id}")
        assert delete_response.status_code == status.HTTP_204_NO_CONTENT

        # Verify first project is deleted
        get_response1 = client.get(f"/api/v1/projects/{project1_id}")
        assert get_response1.status_code == status.HTTP_404_NOT_FOUND

        # Verify second project still exists
        get_response2 = client.get(f"/api/v1/projects/{project2_id}")
        assert get_response2.status_code == status.HTTP_200_OK
        project2_retrieved = get_response2.json()
        assert project2_retrieved["id"] == project2_id
        assert project2_retrieved["name"] == "Project 2"
