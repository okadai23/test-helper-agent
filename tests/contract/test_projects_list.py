"""Contract tests for GET /api/v1/projects endpoint."""

from __future__ import annotations

from typing import Any

from fastapi import status
from fastapi.testclient import TestClient


class TestListProjectsContract:
    """Contract tests for projects list endpoint."""

    def test_list_projects_empty_success(self) -> None:
        """Test successful project list retrieval when no projects exist.

        This test MUST FAIL until the API endpoint is implemented.
        It verifies the contract for GET /api/v1/projects.
        """
        # This will fail because the API endpoint doesn't exist yet
        from test_helper.e2e.api.app import app

        client = TestClient(app)

        # List projects when none exist
        response = client.get("/api/v1/projects")

        # Verify response status
        assert response.status_code == status.HTTP_200_OK

        # Verify response structure
        projects_list = response.json()
        assert "items" in projects_list
        assert "total" in projects_list
        assert "page" in projects_list
        assert "limit" in projects_list

        # Verify empty list
        assert projects_list["items"] == []
        assert projects_list["total"] == 0
        assert projects_list["page"] == 1
        assert projects_list["limit"] == 20  # Default limit

    def test_list_projects_with_data_success(
        self,
        mock_project_data: dict[str, Any],
    ) -> None:
        """Test successful project list retrieval with existing projects.

        This test MUST FAIL until project listing is implemented.
        """
        from test_helper.e2e.api.app import app

        client = TestClient(app)

        # Create multiple projects
        project1_data = mock_project_data.copy()
        project1_data["name"] = "First Project"
        create_response1 = client.post(
            "/api/v1/projects",
            json=project1_data,
        )
        assert create_response1.status_code == status.HTTP_201_CREATED
        project1 = create_response1.json()

        project2_data = mock_project_data.copy()
        project2_data["name"] = "Second Project"
        create_response2 = client.post(
            "/api/v1/projects",
            json=project2_data,
        )
        assert create_response2.status_code == status.HTTP_201_CREATED
        project2 = create_response2.json()

        # List projects
        response = client.get("/api/v1/projects")

        assert response.status_code == status.HTTP_200_OK
        projects_list = response.json()

        # Verify structure
        assert "items" in projects_list
        assert "total" in projects_list
        assert projects_list["total"] == 2
        assert len(projects_list["items"]) == 2

        # Verify project data
        project_ids = {p["id"] for p in projects_list["items"]}
        assert project1["id"] in project_ids
        assert project2["id"] in project_ids

    def test_list_projects_pagination_default(
        self,
        mock_project_data: dict[str, Any],
    ) -> None:
        """Test project list pagination with default parameters.

        This test MUST FAIL until pagination is implemented.
        """
        from test_helper.e2e.api.app import app

        client = TestClient(app)

        # Create a project
        create_response = client.post(
            "/api/v1/projects",
            json=mock_project_data,
        )
        assert create_response.status_code == status.HTTP_201_CREATED

        # List projects with default pagination
        response = client.get("/api/v1/projects")

        assert response.status_code == status.HTTP_200_OK
        projects_list = response.json()

        # Verify pagination fields
        assert projects_list["page"] == 1
        assert projects_list["limit"] == 20
        assert projects_list["total"] == 1

    def test_list_projects_pagination_custom(
        self,
        mock_project_data: dict[str, Any],
    ) -> None:
        """Test project list pagination with custom parameters.

        This test MUST FAIL until custom pagination is implemented.
        """
        from test_helper.e2e.api.app import app

        client = TestClient(app)

        # Create multiple projects
        for i in range(5):
            project_data = mock_project_data.copy()
            project_data["name"] = f"Project {i + 1}"
            create_response = client.post(
                "/api/v1/projects",
                json=project_data,
            )
            assert create_response.status_code == status.HTTP_201_CREATED

        # List projects with custom pagination
        response = client.get("/api/v1/projects?page=2&limit=2")

        assert response.status_code == status.HTTP_200_OK
        projects_list = response.json()

        # Verify pagination
        assert projects_list["page"] == 2
        assert projects_list["limit"] == 2
        assert projects_list["total"] == 5
        assert len(projects_list["items"]) == 2

    def test_list_projects_filter_by_status(
        self,
        mock_project_data: dict[str, Any],
    ) -> None:
        """Test project list filtering by status.

        This test MUST FAIL until status filtering is implemented.
        """
        from test_helper.e2e.api.app import app

        client = TestClient(app)

        # Create active project
        active_project_data = mock_project_data.copy()
        active_project_data["name"] = "Active Project"
        create_response1 = client.post(
            "/api/v1/projects",
            json=active_project_data,
        )
        assert create_response1.status_code == status.HTTP_201_CREATED
        active_project = create_response1.json()

        # Create paused project
        paused_project_data = mock_project_data.copy()
        paused_project_data["name"] = "Paused Project"
        create_response2 = client.post(
            "/api/v1/projects",
            json=paused_project_data,
        )
        assert create_response2.status_code == status.HTTP_201_CREATED
        paused_project = create_response2.json()

        # Update second project to paused status
        patch_response = client.patch(
            f"/api/v1/projects/{paused_project['id']}",
            json={"status": "paused"},
        )
        assert patch_response.status_code == status.HTTP_200_OK

        # Filter by active status
        response = client.get("/api/v1/projects?status=active")

        assert response.status_code == status.HTTP_200_OK
        projects_list = response.json()

        # Should only return active projects
        assert projects_list["total"] == 1
        assert len(projects_list["items"]) == 1
        assert projects_list["items"][0]["status"] == "active"
        assert projects_list["items"][0]["id"] == active_project["id"]

    def test_list_projects_pagination_limits(self) -> None:
        """Test project list pagination limit validation.

        This test MUST FAIL until limit validation is implemented.
        """
        from test_helper.e2e.api.app import app

        client = TestClient(app)

        # Test maximum limit
        response = client.get("/api/v1/projects?limit=100")
        assert response.status_code == status.HTTP_200_OK
        projects_list = response.json()
        assert projects_list["limit"] == 100

        # Test limit too high
        response = client.get("/api/v1/projects?limit=101")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        error = response.json()
        assert "error" in error
        assert "limit" in error["message"].lower()

        # Test minimum limit
        response = client.get("/api/v1/projects?limit=1")
        assert response.status_code == status.HTTP_200_OK
        projects_list = response.json()
        assert projects_list["limit"] == 1

        # Test limit too low
        response = client.get("/api/v1/projects?limit=0")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        error = response.json()
        assert "error" in error

    def test_list_projects_pagination_page_validation(self) -> None:
        """Test project list page number validation.

        This test MUST FAIL until page validation is implemented.
        """
        from test_helper.e2e.api.app import app

        client = TestClient(app)

        # Test minimum page
        response = client.get("/api/v1/projects?page=1")
        assert response.status_code == status.HTTP_200_OK

        # Test page too low
        response = client.get("/api/v1/projects?page=0")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        error = response.json()
        assert "error" in error
        assert "page" in error["message"].lower()

        # Test negative page
        response = client.get("/api/v1/projects?page=-1")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_list_projects_invalid_status_filter(self) -> None:
        """Test project list with invalid status filter.

        This test MUST FAIL until status validation is implemented.
        """
        from test_helper.e2e.api.app import app

        client = TestClient(app)

        response = client.get("/api/v1/projects?status=invalid_status")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        error = response.json()
        assert "error" in error
        assert "status" in error["message"].lower()

    def test_list_projects_sorting_by_created_date(
        self,
        mock_project_data: dict[str, Any],
    ) -> None:
        """Test project list sorting by creation date.

        This test MUST FAIL until sorting is implemented.
        """
        from test_helper.e2e.api.app import app

        client = TestClient(app)

        # Create projects with slight delay to ensure different timestamps
        import time

        project1_data = mock_project_data.copy()
        project1_data["name"] = "First Created"
        create_response1 = client.post(
            "/api/v1/projects",
            json=project1_data,
        )
        assert create_response1.status_code == status.HTTP_201_CREATED
        project1 = create_response1.json()

        time.sleep(0.1)  # Small delay

        project2_data = mock_project_data.copy()
        project2_data["name"] = "Second Created"
        create_response2 = client.post(
            "/api/v1/projects",
            json=project2_data,
        )
        assert create_response2.status_code == status.HTTP_201_CREATED
        project2 = create_response2.json()

        # List projects (should be sorted by creation date, newest first by default)
        response = client.get("/api/v1/projects")

        assert response.status_code == status.HTTP_200_OK
        projects_list = response.json()

        # Verify sorting (newest first)
        assert len(projects_list["items"]) == 2
        assert projects_list["items"][0]["id"] == project2["id"]  # Newer
        assert projects_list["items"][1]["id"] == project1["id"]  # Older

    def test_list_projects_response_format(
        self,
        mock_project_data: dict[str, Any],
    ) -> None:
        """Test project list response format compliance.

        This test MUST FAIL until proper response formatting is implemented.
        """
        from test_helper.e2e.api.app import app

        client = TestClient(app)

        # Create a project
        create_response = client.post(
            "/api/v1/projects",
            json=mock_project_data,
        )
        assert create_response.status_code == status.HTTP_201_CREATED

        # List projects
        response = client.get("/api/v1/projects")

        assert response.status_code == status.HTTP_200_OK

        # Verify content type
        assert response.headers["content-type"] == "application/json"

        # Verify JSON structure
        projects_list = response.json()
        assert isinstance(projects_list, dict)

        # Verify required fields
        required_fields = ["items", "total", "page", "limit"]
        for field in required_fields:
            assert field in projects_list

        # Verify field types
        assert isinstance(projects_list["items"], list)
        assert isinstance(projects_list["total"], int)
        assert isinstance(projects_list["page"], int)
        assert isinstance(projects_list["limit"], int)

        # Verify project structure in items
        if projects_list["items"]:
            project = projects_list["items"][0]
            required_project_fields = {
                "id": str,
                "name": str,
                "url": str,
                "created_at": str,
                "updated_at": str,
                "status": str,
                "test_count": int,
            }

            for field, expected_type in required_project_fields.items():
                assert field in project
                assert isinstance(project[field], expected_type)

    def test_list_projects_empty_page(
        self,
        mock_project_data: dict[str, Any],
    ) -> None:
        """Test project list behavior when requesting page beyond available data.

        This test MUST FAIL until proper pagination bounds checking is implemented.
        """
        from test_helper.e2e.api.app import app

        client = TestClient(app)

        # Create only one project
        create_response = client.post(
            "/api/v1/projects",
            json=mock_project_data,
        )
        assert create_response.status_code == status.HTTP_201_CREATED

        # Request page 2 when only 1 project exists
        response = client.get("/api/v1/projects?page=2&limit=10")

        assert response.status_code == status.HTTP_200_OK
        projects_list = response.json()

        # Should return empty items but correct total
        assert projects_list["items"] == []
        assert projects_list["total"] == 1
        assert projects_list["page"] == 2
        assert projects_list["limit"] == 10
