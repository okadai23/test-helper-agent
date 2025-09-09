"""E2E tests for Swagger UI functionality."""

import pytest
from fastapi.testclient import TestClient


class TestSwaggerUIE2E:
    """E2E tests for Swagger UI with dynamic content generation."""

    @pytest.fixture
    def client(self, monkeypatch: pytest.MonkeyPatch) -> TestClient:
        """Create test client with RestAPI interface."""
        # Set environment variable to use RestAPI interface
        monkeypatch.setenv("INTERFACE_TYPE", "restapi")

        # Import here to ensure environment variable is set
        from test_helper.interfaces.factory import InterfaceFactory
        from test_helper.interfaces.restapi import RestAPIInterface
        from test_helper.types import InterfaceType

        factory = InterfaceFactory()
        interface = factory.create(InterfaceType.RESTAPI)

        # Type narrow to RestAPIInterface to access app attribute
        assert isinstance(interface, RestAPIInterface)

        # Get the FastAPI app from the interface
        return TestClient(interface.app)

    def test_swagger_ui_endpoint(self, client: TestClient) -> None:
        """Test Swagger UI endpoint returns HTML with dynamic content."""
        response = client.get("/api/v1/swagger-ui")
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/html")

        # Verify content includes dynamic documentation
        content = response.text.lower()
        assert "swagger-ui" in content
        assert "test helper api" in content

        # Verify dynamic content elements are present
        assert "enhanced documentation" in content

    def test_swagger_ui_json_schema(self, client: TestClient) -> None:
        """Test Swagger UI JSON schema endpoint with dynamic content."""
        response = client.get("/api/v1/swagger-ui/schema")
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"

        schema = response.json()
        assert "info" in schema
        assert "paths" in schema
        assert "components" in schema

        # Verify metadata from dynamic content generation
        assert schema["info"]["title"] == "Test Helper API"
        assert "dynamic_content" in schema["info"]
        assert schema["info"]["dynamic_content"]["source_files_analyzed"] > 0
        assert schema["info"]["dynamic_content"]["documentation_files_found"] > 0

    def test_swagger_ui_with_source_analysis(self, client: TestClient) -> None:
        """Test that Swagger UI includes analysis from source code."""
        response = client.get("/api/v1/swagger-ui/analysis")
        assert response.status_code == 200

        analysis = response.json()
        assert "interfaces" in analysis
        assert "models" in analysis
        assert "endpoints" in analysis
        assert "documentation_files" in analysis

        # Verify analysis includes current interfaces
        interfaces = analysis["interfaces"]
        assert len(interfaces) > 0
        assert any("restapi" in interface.lower() for interface in interfaces)

        # Verify models analysis
        models = analysis["models"]
        assert len(models) > 0
        assert any("health" in model.lower() for model in models)

    def test_complete_swagger_ui_workflow(self, client: TestClient) -> None:
        """Test complete workflow from analysis to UI generation."""
        # 1. Get source code analysis
        analysis_response = client.get("/api/v1/swagger-ui/analysis")
        assert analysis_response.status_code == 200
        analysis = analysis_response.json()

        # 2. Get schema based on analysis
        schema_response = client.get("/api/v1/swagger-ui/schema")
        assert schema_response.status_code == 200
        schema = schema_response.json()

        # 3. Get UI that uses the schema
        ui_response = client.get("/api/v1/swagger-ui")
        assert ui_response.status_code == 200

        # Verify workflow coherence
        assert len(analysis["interfaces"]) > 0
        assert schema["info"]["dynamic_content"]["source_files_analyzed"] > 0
        assert "swagger-ui" in ui_response.text.lower()

        # Verify that the UI includes key elements
        ui_content = ui_response.text.lower()
        # Check for documentation elements rather than specific interface names
        assert "enhanced documentation" in ui_content
        assert "dynamically generated" in ui_content
