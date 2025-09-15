"""E2E tests for test-helper CLI commands using pexpect."""

import json
import os
import shutil
import tempfile
from collections.abc import Iterator
from pathlib import Path

import pytest

from tests.helpers.pexpect_debug import run_cli_with_debug

# Mark tests that require OpenAI API key
pytestmark = pytest.mark.skipif(
    not os.getenv("OPENAI_API_KEY"),
    reason="Requires OPENAI_API_KEY environment variable",
)


class TestCLIE2ECommands:
    """E2E tests for test-helper CLI E2E commands."""

    @pytest.fixture
    def clean_env(self) -> dict[str, str]:
        """Provide clean environment with API key."""
        env = os.environ.copy()
        # Ensure we have the API key
        if "OPENAI_API_KEY" not in env:
            pytest.skip("OPENAI_API_KEY not set")
        env["AGENT_BACKEND"] = "sdk"
        env["OPENAI_MODEL"] = "gpt-5"
        return env

    @pytest.fixture
    def temp_dir(self) -> Iterator[Path]:
        """Create temporary directory for test outputs."""
        temp_dir = tempfile.mkdtemp(prefix="test_cli_e2e_")
        yield Path(temp_dir)
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_cli_help_command(self, clean_env: dict[str, str]) -> None:
        """Test that help command works."""
        output, exitstatus = run_cli_with_debug(
            "uv run test-helper --help",
            env=clean_env,
            timeout=10,
        )

        assert exitstatus == 0
        assert "Test Helper CLI" in output
        assert "e2e" in output
        assert "Commands" in output

    def test_cli_e2e_help(self, clean_env: dict[str, str]) -> None:
        """Test E2E subcommand help."""
        output, exitstatus = run_cli_with_debug(
            "uv run test-helper e2e --help",
            env=clean_env,
            timeout=10,
        )

        assert exitstatus == 0
        assert "E2E test automation commands" in output
        assert "capture" in output
        assert "generate" in output
        assert "diagnose" in output
        assert "syntax-check" in output

    def test_cli_capture_command(
        self, clean_env: dict[str, str], temp_dir: Path
    ) -> None:
        """Test capture command functionality."""
        output_file = temp_dir / "capture.json"

        # Run capture command
        output, exitstatus = run_cli_with_debug(
            "uv run test-helper e2e capture "
            f"test-project-123 http://localhost:8000/test/ "
            f"--output {output_file}",
            env=clean_env,
            timeout=30,
        )

        assert exitstatus == 0
        assert "Creating capture plan" in output
        assert "Capture plan saved" in output
        assert output_file.exists()

        # Verify JSON content
        with output_file.open() as f:
            data = json.load(f)

        assert "project_id" in data
        assert data["project_id"] == "test-project-123"
        assert "steps" in data
        assert isinstance(data["steps"], list)
        assert len(data["steps"]) > 0

    def test_cli_generate_command(
        self, clean_env: dict[str, str], temp_dir: Path
    ) -> None:
        """Test generate command functionality."""
        # Create sample session file
        session_file = temp_dir / "session.json"
        session_data = {
            "project_id": "test-project",
            "base_url": "http://localhost:8000/",
            "test_name": "Test Generated",
            "steps": [
                {"action": "navigate", "url": "http://localhost:8000/"},
                {"action": "click", "selector": "button"},
                {"action": "wait", "selector": ".result"},
            ],
            "assertions": [
                {"type": "visible", "selector": ".result"},
            ],
        }
        session_file.write_text(json.dumps(session_data))

        output_file = temp_dir / "test.spec.ts"

        # Run generate command
        output, exitstatus = run_cli_with_debug(
            f"uv run test-helper e2e generate {session_file} --output {output_file}",
            env=clean_env,
            timeout=30,
        )

        assert exitstatus == 0
        assert "Generating test from session" in output
        assert "Test code saved" in output
        assert output_file.exists()

        # Verify TypeScript content
        content = output_file.read_text()
        assert "import { test, expect }" in content
        assert "page.goto" in content
        assert "async" in content

    def test_cli_diagnose_command(
        self, clean_env: dict[str, str], temp_dir: Path
    ) -> None:
        """Test diagnose command functionality."""
        # Create sample error log file
        log_file = temp_dir / "error.json"
        log_data = [
            {
                "timestamp": "2025-09-13T12:00:00Z",
                "level": "ERROR",
                "message": "Element not found: button.submit",
                "stack_trace": "at page.click() at test.spec.ts:15",
            },
            {
                "timestamp": "2025-09-13T12:00:01Z",
                "level": "ERROR",
                "message": "Timeout waiting for selector",
                "stack_trace": "at page.waitForSelector() at test.spec.ts:20",
            },
        ]
        log_file.write_text(json.dumps(log_data))

        # Run diagnose command
        output, exitstatus = run_cli_with_debug(
            "uv run test-helper e2e diagnose {log_file}",
            env=clean_env,
            timeout=30,
        )

        assert exitstatus == 0
        assert "Diagnosing failure" in output
        assert "Diagnosis:" in output
        assert "Category:" in output
        assert "Confidence:" in output

    def test_cli_syntax_check_command(
        self, clean_env: dict[str, str], temp_dir: Path
    ) -> None:
        """Test syntax-check command functionality."""
        # Create a TypeScript file with valid syntax
        test_file = temp_dir / "test.spec.ts"
        test_file.write_text("""
import { test, expect } from '@playwright/test';

test('Valid test', async ({ page }) => {
    await page.goto('http://localhost:8000/');
    await expect(page).toHaveTitle('Test');
});
""")

        # Run syntax-check command
        output, exitstatus = run_cli_with_debug(
            "uv run test-helper e2e syntax-check {test_file}",
            env=clean_env,
            timeout=30,
        )

        assert exitstatus == 0
        assert "Validating syntax" in output
        assert "No syntax errors found" in output or "syntax errors detected" in output

    def test_cli_syntax_check_with_fix(
        self, clean_env: dict[str, str], temp_dir: Path
    ) -> None:
        """Test syntax-check command with --fix option."""
        # Create a TypeScript file with potential issues
        test_file = temp_dir / "test_broken.spec.ts"
        test_file.write_text("""
import { test, expect } from '@playwright/test';

test('Test with issues', async ({ page }) => {
    await page.goto('http://localhost:8000/');
    await page.click('button[data-testid="submit"]');
    await page.click("a[href='#features']");  // Mixed quotes
    await expect(page).toHaveTitle('Test');
});
""")

        # Run syntax-check command with fix
        output, exitstatus = run_cli_with_debug(
            f"uv run test-helper e2e syntax-check {test_file} --fix",
            env=clean_env,
            timeout=30,
        )

        assert exitstatus == 0
        assert "Checking and fixing syntax" in output
        assert "Fixed" in output or "No syntax errors" in output

    def test_cli_complete_workflow(
        self, clean_env: dict[str, str], temp_dir: Path
    ) -> None:
        """Test complete workflow: capture -> generate -> syntax-check."""
        # Step 1: Capture
        capture_file = temp_dir / "capture.json"
        output, exitstatus = run_cli_with_debug(
            "uv run test-helper e2e capture "
            f"workflow-test http://localhost:8000/ "
            f"--output {capture_file}",
            env=clean_env,
            timeout=30,
        )

        assert exitstatus == 0
        assert capture_file.exists()

        # Modify capture to be a proper session
        with capture_file.open() as f:
            capture_data = json.load(f)

        session_data = {
            "project_id": capture_data.get("project_id", "workflow-test"),
            "base_url": "http://localhost:8000/",
            "test_name": "Workflow Test",
            "steps": capture_data.get(
                "steps",
                [
                    {"action": "navigate", "url": "http://localhost:8000/"},
                ],
            ),
            "assertions": capture_data.get(
                "assertions",
                [
                    {"type": "visible", "selector": "body"},
                ],
            ),
        }

        session_file = temp_dir / "session.json"
        session_file.write_text(json.dumps(session_data))

        # Step 2: Generate
        test_file = temp_dir / "workflow_test.spec.ts"
        output, exitstatus = run_cli_with_debug(
            f"uv run test-helper e2e generate {session_file} --output {test_file}",
            env=clean_env,
            timeout=30,
        )

        assert exitstatus == 0
        assert test_file.exists()

        # Step 3: Syntax check
        output, exitstatus = run_cli_with_debug(
            "uv run test-helper e2e syntax-check {test_file}",
            env=clean_env,
            timeout=30,
        )

        assert exitstatus == 0
        assert "syntax" in output.lower()

    def test_cli_interactive_session(
        self, clean_env: dict[str, str], temp_dir: Path
    ) -> None:
        """Test interactive CLI session with multiple commands."""
        # This tests that the CLI can handle multiple commands in sequence
        commands = [
            (
                f"e2e capture test-interactive http://localhost:8000/ --output {temp_dir}/cap.json",
                "Capture plan saved",
            ),
            (
                f"e2e syntax-check {temp_dir}/../README.md",
                "Error: Test file not found",
            ),  # Test error handling
            ("config --show", "Current configuration"),
            ("version", "version"),
        ]

        for cmd, expected in commands:
            output, exitstatus = run_cli_with_debug(
                f"uv run test-helper {cmd}",
                env=clean_env,
                timeout=30,
            )

            # Some commands may fail (like syntax-check on non-existent file)
            # But they should fail gracefully
            if "Error:" in expected:
                assert exitstatus != 0

            # Check expected output is present (case-insensitive for some outputs)
            assert expected.lower() in output.lower()
