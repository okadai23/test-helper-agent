"""Unit tests for SyntaxFixAgent."""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from test_helper.agents.syntax_fix_agent import (
    SyntaxFixAgent,
    SyntaxFixResult,
    TestSyntaxError,
)


class TestSyntaxFixAgent:
    """Test SyntaxFixAgent functionality."""

    @pytest.fixture
    def agent(self) -> SyntaxFixAgent:
        """Create a SyntaxFixAgent instance."""
        return SyntaxFixAgent(openai_client=None)

    @pytest.fixture
    def agent_with_ai(self) -> SyntaxFixAgent:
        """Create a SyntaxFixAgent with mock OpenAI client."""
        mock_client = Mock()
        return SyntaxFixAgent(openai_client=mock_client)

    @pytest.fixture
    def test_file(self, tmp_path: Path) -> Path:
        """Create a test TypeScript file with syntax errors."""
        test_file = tmp_path / "test.spec.ts"
        test_file.write_text("""import { test, expect } from '@playwright/test';

test('Test with syntax errors', async ({ page }) => {
  await page.goto('http://localhost:8000');
  await page.click('a[href='#features']');  // Nested quotes error
  page.fill('input[name='email']', 'test@example.com');  // Missing await
  await expect(page.locator('button:has-text('Submit')')).toBeVisible();  // Nested quotes
});
""")
        return test_file

    def test_fix_common_quote_errors(self, agent: SyntaxFixAgent) -> None:
        """Test fixing common quote nesting errors."""
        content = "await page.click('a[href='#features']');"
        fixed = agent._fix_common_quote_errors(content)
        assert fixed == "await page.click('a[href=\"#features\"]');"

        content = "await page.click('button:has-text('Submit')');"
        fixed = agent._fix_common_quote_errors(content)
        assert fixed == "await page.click('button:has-text(\"Submit\")');"

    def test_fix_missing_await(self, agent: SyntaxFixAgent) -> None:
        """Test adding missing await keywords."""
        content = """  page.goto('http://localhost:8000');
  page.click('button');
  expect(page.locator('div')).toBeVisible();"""

        fixed = agent._fix_missing_await(content)
        assert "await page.goto" in fixed
        assert "await page.click" in fixed
        assert "await expect" in fixed

    def test_syntax_error_model(self) -> None:
        """Test SyntaxError model."""
        error = TestSyntaxError(
            file="test.ts",
            line=10,
            column=5,
            message="Unterminated string literal",
            code="TS1002",
        )
        assert error.file == "test.ts"
        assert error.line == 10
        assert error.column == 5
        assert error.severity == "error"

    def test_syntax_fix_result_model(self) -> None:
        """Test SyntaxFixResult model."""
        result = SyntaxFixResult(
            success=True,
            original_file="test.ts",
            fixed_file="test.ts",
            iterations=2,
        )
        assert result.success is True
        assert result.iterations == 2
        assert result.errors_found == []
        assert result.errors_fixed == []

    @patch("subprocess.run")
    def test_run_typescript_check(
        self, mock_run: Mock, agent: SyntaxFixAgent, tmp_path: Path
    ) -> None:
        """Test running TypeScript syntax check."""
        test_file = tmp_path / "test.ts"
        test_file.write_text("const x = 1;")

        # Mock TypeScript compiler output
        mock_run.return_value = Mock(
            stdout="test.ts(1,13): error TS1002: Unterminated string literal",
            stderr="",
            returncode=1,
        )

        errors = agent._run_typescript_check(test_file)
        assert len(errors) == 1
        assert errors[0].line == 1
        assert errors[0].column == 13
        assert errors[0].code == "TS1002"
        assert "Unterminated string literal" in errors[0].message

    @patch("subprocess.run")
    def test_run_eslint_check(
        self, mock_run: Mock, agent: SyntaxFixAgent, tmp_path: Path
    ) -> None:
        """Test running ESLint check."""
        test_file = tmp_path / "test.ts"
        test_file.write_text("const x = 1")

        # Mock ESLint JSON output
        mock_run.return_value = Mock(
            stdout='[{"filePath":"test.ts","messages":[{"line":1,"column":12,"message":"Missing semicolon","ruleId":"semi"}]}]',
            stderr="",
            returncode=1,
        )

        errors = agent._run_eslint_check(test_file)
        assert len(errors) == 1
        assert errors[0].line == 1
        assert errors[0].column == 12
        assert errors[0].code == "semi"
        assert "Missing semicolon" in errors[0].message

    def test_fix_syntax_errors_no_file(self, agent: SyntaxFixAgent) -> None:
        """Test fix_syntax_errors with non-existent file."""
        result = agent.fix_syntax_errors("/non/existent/file.ts")
        assert result.success is False
        assert result.original_file == "/non/existent/file.ts"
        assert result.fixed_file is None
        assert result.errors_found == []

    @patch("subprocess.run")
    def test_fix_syntax_errors_success(
        self, mock_run: Mock, agent: SyntaxFixAgent, test_file: Path
    ) -> None:
        """Test successful syntax error fixing."""
        # First call returns errors, second call returns no errors
        mock_run.side_effect = [
            # First TypeScript check - has errors
            Mock(
                stdout="test.spec.ts(5,3): error TS1002: Unterminated string",
                stderr="",
                returncode=1,
            ),
            # First ESLint check - has errors
            Mock(
                stdout='[{"filePath":"test.spec.ts","messages":[{"line":5,"column":3,"message":"Missing semicolon","ruleId":"semi"}]}]',
                stderr="",
                returncode=1,
            ),
            # ESLint fix
            Mock(stdout="", stderr="", returncode=0),
            # Second TypeScript check - no errors
            Mock(stdout="", stderr="", returncode=0),
            # Second ESLint check - no errors
            Mock(
                stdout='[{"filePath":"test.spec.ts","messages":[]}]',
                stderr="",
                returncode=0,
            ),
        ]

        result = agent.fix_syntax_errors(test_file)
        assert result.success is True
        assert result.iterations == 1
        assert len(result.errors_found) > 0

    def test_ai_fix_errors(self, agent_with_ai: SyntaxFixAgent) -> None:
        """Test AI-powered error fixing."""
        content = "await page.click('button:has-text('Submit')');"
        errors = [
            TestSyntaxError(
                file="test.ts",
                line=1,
                column=35,
                message="Unterminated string literal",
                code="TS1002",
            )
        ]

        # Mock AI response
        mock_response = Mock()
        mock_response.choices = [
            Mock(
                message=Mock(content="await page.click('button:has-text(\"Submit\")');")
            )
        ]
        assert agent_with_ai.openai_client is not None
        agent_with_ai.openai_client.chat.completions.create.return_value = mock_response

        fixed = agent_with_ai._ai_fix_errors(content, errors)
        assert fixed == "await page.click('button:has-text(\"Submit\")');"

    @patch("subprocess.run")
    def test_apply_eslint_autofix(
        self, mock_run: Mock, agent: SyntaxFixAgent, tmp_path: Path
    ) -> None:
        """Test applying ESLint auto-fix."""
        test_file = tmp_path / "test.ts"
        test_file.write_text("const x = 1")

        mock_run.return_value = Mock(returncode=0)
        result = agent._apply_eslint_autofix(test_file)
        assert result is True

        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        assert "eslint" in call_args
        assert "--fix" in call_args
