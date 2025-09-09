"""Pytest configuration for test_project tests."""

import json
import tempfile
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest
import yaml


@pytest.fixture
def temp_dir():  # type: ignore[no-untyped-def]  # noqa: ANN201
    """Create a temporary directory for file operations testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_json_data() -> dict[str, Any]:
    """Sample JSON data for testing."""
    return {
        "name": "Test Project",
        "version": "1.0.0",
        "features": ["file_handling", "logging", "testing"],
        "config": {
            "debug": True,
            "max_retries": 3,
            "encoding": "utf-8",
        },
        "unicode_test": "テスト文字列",  # Japanese text for encoding tests
    }


@pytest.fixture
def sample_yaml_data() -> dict[str, Any]:
    """Sample YAML data for testing."""
    return {
        "application": {
            "name": "TestApp",
            "environment": "development",
            "settings": {
                "port": 8080,
                "host": "localhost",
                "ssl_enabled": False,
            },
        },
        "database": {
            "driver": "postgresql",
            "host": "localhost",
            "port": 5432,
            "name": "testdb",
        },
        "unicode_content": "テストYAML",  # Japanese text for encoding tests
    }


@pytest.fixture
def sample_text_utf8() -> str:
    """Sample UTF-8 text for testing."""
    return """This is a test file with UTF-8 encoding.
It contains multiple lines and special characters: €, ñ, ü
日本語のテキストも含まれています。
End of file."""


@pytest.fixture
def sample_text_cp932() -> str:
    """Sample text that can be encoded in CP932."""
    return """This is a test file for CP932 encoding.
日本語の文字列テスト
シフトJISエンコーディング
End of file."""


@pytest.fixture
def sample_files(
    temp_dir: Path,
    sample_json_data: dict[str, Any],
    sample_yaml_data: dict[str, Any],
    sample_text_utf8: str,
    sample_text_cp932: str,
) -> dict[str, Path]:
    """Create sample files for testing and return their paths."""
    files: dict[str, Path] = {}

    # Create JSON file
    json_path = temp_dir / "test_data.json"
    json_path.write_text(
        json.dumps(sample_json_data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    files["json"] = json_path

    # Create YAML file
    yaml_path = temp_dir / "test_config.yaml"
    yaml_path.write_text(
        yaml.dump(sample_yaml_data, default_flow_style=False, allow_unicode=True),
        encoding="utf-8",
    )
    files["yaml"] = yaml_path

    # Create UTF-8 text file
    utf8_path = temp_dir / "test_utf8.txt"
    utf8_path.write_text(sample_text_utf8, encoding="utf-8")
    files["utf8_text"] = utf8_path

    # Create CP932 text file
    cp932_path = temp_dir / "test_cp932.txt"
    cp932_path.write_text(sample_text_cp932, encoding="cp932")
    files["cp932_text"] = cp932_path

    # Create nested directory structure for testing parent creation
    nested_dir = temp_dir / "nested" / "deep" / "structure"
    files["nested_dir"] = nested_dir

    return files


@pytest.fixture
def invalid_json_file(temp_dir: Path) -> Path:
    """Create an invalid JSON file for error testing."""
    invalid_path = temp_dir / "invalid.json"
    # Invalid JSON with undefined value
    invalid_path.write_text(
        '{"name": "test", "value": undefined}',
        encoding="utf-8",
    )
    return invalid_path


@pytest.fixture
def invalid_yaml_file(temp_dir: Path) -> Path:
    """Create an invalid YAML file for error testing."""
    invalid_path = temp_dir / "invalid.yaml"
    # Invalid YAML with bad indentation
    invalid_path.write_text(
        "key: value\n  invalid: indentation without parent",
        encoding="utf-8",
    )
    return invalid_path


@pytest.fixture
def non_existent_file(temp_dir: Path) -> Path:
    """Return path to a non-existent file for error testing."""
    return temp_dir / "does_not_exist.txt"


# E2E Test Automation fixtures


@pytest.fixture
def mock_project_data() -> dict[str, Any]:
    """Sample project data for E2E testing."""
    return {
        "name": "Test E2E Project",
        "url": "https://example.com",
        "browser_config": {
            "browser": "chromium",
            "headless": True,
            "viewport": {"width": 1280, "height": 720},
        },
        "metadata": {"test_suite": "e2e", "environment": "development"},
    }


@pytest.fixture
def mock_scenario_data() -> dict[str, Any]:
    """Sample scenario data for E2E testing."""
    project_id = str(uuid4())
    return {
        "project_id": project_id,
        "name": "Login Test Scenario",
        "description": "Test user login functionality",
        "tags": ["login", "authentication"],
        "steps": [
            {
                "type": "navigate",
                "url": "https://example.com/login",
                "description": "Navigate to login page",
            },
            {
                "type": "input",
                "selector": "#username",
                "value": "testuser",
                "description": "Enter username",
            },
            {
                "type": "input",
                "selector": "#password",
                "value": "password123",
                "description": "Enter password",
            },
            {
                "type": "click",
                "selector": "#login-button",
                "description": "Click login button",
            },
            {
                "type": "assert",
                "assertion": {
                    "type": "url",
                    "expected": "https://example.com/dashboard",
                    "operator": "equals",
                },
                "description": "Verify redirect to dashboard",
            },
        ],
    }


@pytest.fixture
def mock_execution_data() -> dict[str, Any]:
    """Sample execution data for E2E testing."""
    scenario_id = str(uuid4())
    project_id = str(uuid4())
    return {
        "scenario_id": scenario_id,
        "project_id": project_id,
        "status": "passed",
        "duration_ms": 5000,
        "screenshots": ["screenshot1.png", "screenshot2.png"],
        "logs": [
            {
                "level": "info",
                "message": "Test started",
                "context": {"step": "navigate"},
            },
            {
                "level": "info",
                "message": "Test completed successfully",
                "context": {"step": "assert"},
            },
        ],
    }


@pytest.fixture
def mock_capture_session_data() -> dict[str, Any]:
    """Sample capture session data for E2E testing."""
    project_id = str(uuid4())
    return {
        "project_id": project_id,
        "status": "active",
        "browser_session_id": "browser-123",
        "captured_interactions": [
            {
                "type": "click",
                "target_selector": "#submit-button",
                "alternative_selectors": [
                    "button[type='submit']",
                    ".btn-primary",
                ],
                "metadata": {"x": 100, "y": 200},
            },
            {
                "type": "input",
                "target_selector": "#email",
                "value": "test@example.com",
                "alternative_selectors": ["input[name='email']"],
                "metadata": {"field_type": "email"},
            },
        ],
    }


@pytest.fixture
def mock_fix_proposal_data() -> dict[str, Any]:
    """Sample fix proposal data for E2E testing."""
    execution_id = str(uuid4())
    scenario_id = str(uuid4())
    step_id = str(uuid4())
    return {
        "execution_id": execution_id,
        "scenario_id": scenario_id,
        "confidence": 0.85,
        "fix_type": "selector",
        "description": "Update selector to more stable alternative",
        "rationale": (
            "Original selector #button was not found, but .submit-btn is available"
        ),
        "changes": [
            {
                "step_id": step_id,
                "change_type": "modify",
                "field": "selector",
                "old_value": "#button",
                "new_value": ".submit-btn",
            },
        ],
        "estimated_impact": "low",
        "auto_applicable": True,
    }


@pytest.fixture
def mock_temporal_client() -> Mock:
    """Mock Temporal client for testing."""
    client = Mock()
    client.start_workflow = AsyncMock()
    client.get_workflow_handle = Mock()
    client.list_workflows = AsyncMock()
    return client


@pytest.fixture
def mock_playwright_mcp_client() -> Mock:
    """Mock Playwright MCP client for testing."""
    client = Mock()
    client.create_browser_context = AsyncMock()
    client.navigate = AsyncMock()
    client.click = AsyncMock()
    client.fill = AsyncMock()
    client.wait_for_selector = AsyncMock()
    client.take_screenshot = AsyncMock()
    client.close_context = AsyncMock()
    return client


@pytest.fixture
def mock_openai_client() -> Mock:
    """Mock OpenAI client for testing."""
    client = Mock()
    client.chat.completions.create = AsyncMock()
    return client


@pytest.fixture
def e2e_test_data_dir(temp_dir: Path) -> Path:
    """Create E2E test data directory structure."""
    e2e_dir = temp_dir / "e2e_test_data"
    e2e_dir.mkdir(parents=True, exist_ok=True)

    # Create project directories
    projects_dir = e2e_dir / "projects"
    projects_dir.mkdir(exist_ok=True)

    # Create cache directory
    cache_dir = e2e_dir / "cache"
    cache_dir.mkdir(exist_ok=True)

    return e2e_dir


@pytest.fixture
def isolated_storage_manager(e2e_test_data_dir: Path) -> Any:
    """Create an isolated storage manager for testing."""
    from test_helper.lib.storage_manager import StorageManager

    return StorageManager(base_path=e2e_test_data_dir)


@pytest.fixture
def e2e_project_dir(e2e_test_data_dir: Path) -> Path:
    """Create a sample E2E project directory."""
    project_id = str(uuid4())
    project_dir = e2e_test_data_dir / "projects" / project_id
    project_dir.mkdir(parents=True, exist_ok=True)

    # Create subdirectories
    (project_dir / "tests").mkdir(exist_ok=True)
    (project_dir / "cache").mkdir(exist_ok=True)
    (project_dir / "history").mkdir(exist_ok=True)

    # Create metadata file
    metadata = {
        "project": {
            "id": project_id,
            "name": "Test Project",
            "url": "https://example.com",
            "status": "active",
            "browser_config": {
                "browser": "chromium",
                "headless": True,
                "viewport": {"width": 1280, "height": 720},
            },
        },
        "statistics": {
            "total_scenarios": 0,
            "total_executions": 0,
            "success_rate": 0.0,
            "average_duration_ms": 0,
            "last_7_days_executions": 0,
            "storage_size_mb": 0.0,
        },
    }

    metadata_file = project_dir / "metadata.json"
    metadata_file.write_text(
        json.dumps(metadata, indent=2, default=str),
        encoding="utf-8",
    )

    return project_dir
