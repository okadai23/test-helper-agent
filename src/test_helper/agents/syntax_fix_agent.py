"""Syntax Fix Agent for fixing TypeScript/Playwright test syntax errors."""

import json
import re
import subprocess
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from test_helper.agents.base import BaseAgent
from test_helper.utils.logger import get_logger

logger = get_logger(__name__)


class TestSyntaxError(BaseModel):
    """Model for syntax error information."""

    file: str
    line: int
    column: int
    message: str
    code: str | None = None
    severity: str = "error"


class SyntaxFixResult(BaseModel):
    """Result of syntax fixing operation."""

    success: bool
    original_file: str
    fixed_file: str | None = None
    errors_found: list[TestSyntaxError] = Field(
        default_factory=lambda: list[TestSyntaxError]()
    )
    errors_fixed: list[TestSyntaxError] = Field(
        default_factory=lambda: list[TestSyntaxError]()
    )
    iterations: int = 0
    final_errors: list[TestSyntaxError] = Field(
        default_factory=lambda: list[TestSyntaxError]()
    )


class SyntaxFixAgent(BaseAgent):
    """Agent for fixing TypeScript syntax errors in Playwright tests."""

    def __init__(
        self, openai_client: Any | None = None, max_iterations: int = 5
    ) -> None:
        """Initialize the syntax fix agent.

        Args:
            openai_client: OpenAI client for AI-powered fixes
            max_iterations: Maximum iterations for fixing errors

        """
        super().__init__(openai_client)
        self.max_iterations = max_iterations

    def _run_typescript_check(self, file_path: Path) -> list[TestSyntaxError]:
        """Run TypeScript compiler to detect syntax errors.

        Args:
            file_path: Path to the TypeScript file

        Returns:
            List of syntax errors found

        """
        try:
            result = subprocess.run(  # noqa: S603
                ["npx", "tsc", "--noEmit", "--pretty", "false", str(file_path)],
                check=False,
                capture_output=True,
                text=True,
                cwd=file_path.parent.parent
                if file_path.parent.name in ["generated_tests", "tests"]
                else file_path.parent,
            )

            errors: list[TestSyntaxError] = []
            for line in result.stdout.splitlines() + result.stderr.splitlines():
                # Parse TypeScript error format: file(line,col): error TS####: message
                match = re.match(
                    r"(.+?)\((\d+),(\d+)\):\s+error\s+(TS\d+):\s+(.+)", line
                )
                if match:
                    errors.append(
                        TestSyntaxError(
                            file=match.group(1),
                            line=int(match.group(2)),
                            column=int(match.group(3)),
                            code=match.group(4),
                            message=match.group(5),
                        )
                    )
        except Exception as e:
            logger.error("Error running TypeScript check", error=str(e))
            return []
        else:
            return errors

    def _run_eslint_check(self, file_path: Path) -> list[TestSyntaxError]:
        """Run ESLint to detect linting errors.

        Args:
            file_path: Path to the TypeScript file

        Returns:
            List of linting errors found

        """
        try:
            result = subprocess.run(  # noqa: S603
                ["npx", "eslint", str(file_path), "--format", "json"],
                check=False,
                capture_output=True,
                text=True,
                cwd=file_path.parent.parent
                if file_path.parent.name in ["generated_tests", "tests"]
                else file_path.parent,
            )

            if result.stdout:
                eslint_results = json.loads(result.stdout)
                errors = [
                    TestSyntaxError(
                        file=file_result["filePath"],
                        line=message.get("line", 0),
                        column=message.get("column", 0),
                        message=message.get("message", ""),
                        code=message.get("ruleId"),
                        severity=message.get("severity", "error"),
                    )
                    for file_result in eslint_results
                    for message in file_result.get("messages", [])
                ]
                return errors  # noqa: RET504
        except Exception as e:
            logger.error("Error running ESLint", error=str(e))
        return []

    def _fix_common_quote_errors(self, content: str) -> str:
        """Fix common quote nesting errors in TypeScript.

        Args:
            content: File content

        Returns:
            Fixed content

        """
        # Fix nested quotes in selectors
        patterns = [
            # Pattern to fix nested single quotes in href attributes
            (r"'(.*?)\[([^=]+)='([^']+)'\]'", r"'\1[\2=\"\3\"]'"),
            # Fix: 'button:has-text('text')' -> 'button:has-text("text")'
            (r"'(.*?):has-text\('([^']+)'\)'", r"'\1:has-text(\"\2\")'"),
            # Fix: 'input[name='field']' -> 'input[name="field"]'
            (r"'(input|button|select)\[([^=]+)='([^']+)'\]'", r"'\1[\2=\"\3\"]'"),
        ]

        fixed = content
        for pattern, replacement in patterns:
            fixed = re.sub(pattern, replacement, fixed)

        return fixed

    def _fix_missing_await(self, content: str) -> str:
        """Add missing await keywords for async operations.

        Args:
            content: File content

        Returns:
            Fixed content

        """
        # Add await for common Playwright async methods
        patterns = [
            (r"^(\s+)page\.(goto|click|fill|type|press|waitFor)", r"\1await page.\2"),
            (r"^(\s+)expect\(", r"\1await expect("),
            (
                r"^(\s+)page\.locator\(.*?\)\.(click|fill|type|press)",
                r"\1await page.locator\2",
            ),
        ]

        lines = content.split("\n")
        fixed_lines: list[str] = []
        for line in lines:
            fixed_line = line
            for pattern, replacement in patterns:
                if re.match(pattern, line) and "await" not in line:
                    fixed_line = re.sub(pattern, replacement, line)
                    break
            fixed_lines.append(fixed_line)

        return "\n".join(fixed_lines)

    def _apply_eslint_autofix(self, file_path: Path) -> bool:
        """Apply ESLint auto-fix to the file.

        Args:
            file_path: Path to the TypeScript file

        Returns:
            True if fixes were applied

        """
        try:
            result = subprocess.run(  # noqa: S603
                ["npx", "eslint", str(file_path), "--fix"],
                check=False,
                capture_output=True,
                text=True,
                cwd=file_path.parent.parent
                if file_path.parent.name in ["generated_tests", "tests"]
                else file_path.parent,
            )
        except Exception as e:
            logger.error("Error applying ESLint fixes", error=str(e))
            return False
        else:
            return result.returncode == 0

    def _ai_fix_errors(self, content: str, errors: list[TestSyntaxError]) -> str:
        """Use AI to fix syntax errors.

        Args:
            content: File content
            errors: List of errors to fix

        Returns:
            Fixed content

        """
        if not self.openai_client or not errors:
            return content

        try:
            error_descriptions = "\n".join(
                [
                    f"Line {e.line}: {e.message}" for e in errors[:5]
                ]  # Limit to first 5 errors
            )

            system = """You are a TypeScript/Playwright test syntax fixer.
Fix the syntax errors in the provided code.
Return ONLY the fixed code, no explanations."""

            user = f"""Fix these syntax errors in the Playwright test:

Errors:
{error_descriptions}

Code:
{content}"""

            response = self._run(
                self.openai_client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": system},
                        {"role": "user", "content": user},
                    ],
                    temperature=0.1,
                    max_completion_tokens=3000,
                ),
            )

            if response and response.choices:
                fixed = response.choices[0].message.content
                # Remove code block markers if present
                fixed = re.sub(r"^```(?:typescript|ts)?\n", "", fixed)
                return re.sub(r"\n```$", "", fixed)

        except Exception as e:
            logger.error("AI fix failed", error=str(e))

        return content

    def fix_syntax_errors(self, file_path: str | Path) -> SyntaxFixResult:
        """Fix syntax errors in a TypeScript file iteratively.

        Args:
            file_path: Path to the TypeScript file

        Returns:
            Result of the fixing operation

        """
        file_path = Path(file_path)
        if not file_path.exists():
            return SyntaxFixResult(
                success=False,
                original_file=str(file_path),
                errors_found=[],
            )

        original_content = file_path.read_text()
        current_content = original_content
        all_errors_found: list[TestSyntaxError] = []
        all_errors_fixed: list[TestSyntaxError] = []
        iteration = 0

        while iteration < self.max_iterations:
            iteration += 1
            logger.debug("Syntax fix iteration", iteration=iteration)

            # Check for TypeScript errors
            ts_errors = self._run_typescript_check(file_path)

            # Check for ESLint errors
            eslint_errors = self._run_eslint_check(file_path)

            # Combine errors
            current_errors = ts_errors + eslint_errors

            if not current_errors:
                # No errors found, we're done
                logger.info("No syntax errors found")
                break

            # Track found errors
            for error in current_errors:
                if error not in all_errors_found:
                    all_errors_found.append(error)

            # Apply fixes in order of preference

            # 1. Try common pattern fixes
            fixed_content = self._fix_common_quote_errors(current_content)
            fixed_content = self._fix_missing_await(fixed_content)

            # 2. Apply ESLint auto-fix
            if fixed_content != current_content:
                file_path.write_text(fixed_content)
                current_content = fixed_content

            self._apply_eslint_autofix(file_path)
            current_content = file_path.read_text()

            # 3. If errors persist and we have AI, try AI fix
            if self.openai_client and iteration < self.max_iterations - 1:
                remaining_errors = self._run_typescript_check(file_path)
                if remaining_errors:
                    fixed_content = self._ai_fix_errors(
                        current_content, remaining_errors
                    )
                    if fixed_content != current_content:
                        file_path.write_text(fixed_content)
                        current_content = fixed_content

            # Check if we made progress
            new_errors = self._run_typescript_check(file_path) + self._run_eslint_check(
                file_path
            )
            if len(new_errors) >= len(current_errors):
                # No progress made, stop
                logger.warning("No progress in fixing errors, stopping")
                break

            # Track fixed errors
            for error in current_errors:
                if error not in new_errors and error not in all_errors_fixed:
                    all_errors_fixed.append(error)

        # Final check
        final_errors = self._run_typescript_check(file_path) + self._run_eslint_check(
            file_path
        )

        return SyntaxFixResult(
            success=len(final_errors) == 0,
            original_file=str(file_path),
            fixed_file=str(file_path) if current_content != original_content else None,
            errors_found=all_errors_found,
            errors_fixed=all_errors_fixed,
            iterations=iteration,
            final_errors=final_errors,
        )
