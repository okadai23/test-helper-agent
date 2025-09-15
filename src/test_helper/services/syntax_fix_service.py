"""Service for fixing TypeScript/Playwright test syntax errors."""

from pathlib import Path
from typing import Any

from test_helper.agents.base import BaseService
from test_helper.agents.syntax_fix_agent import SyntaxFixAgent, SyntaxFixResult
from test_helper.utils.logger import get_logger

logger = get_logger(__name__)


class SyntaxFixService(BaseService):
    """Service for fixing syntax errors in generated tests."""

    def __init__(self, openai_client: Any | None = None) -> None:
        """Initialize the syntax fix service.

        Args:
            openai_client: Optional OpenAI client for AI-powered fixes

        """
        super().__init__()
        self.agent = SyntaxFixAgent(openai_client=openai_client)

    def fix_test_file(self, file_path: str | Path) -> SyntaxFixResult:
        """Fix syntax errors in a test file.

        Args:
            file_path: Path to the test file

        Returns:
            Result of the syntax fixing operation

        """
        logger.info("Fixing syntax errors in file", file_path=str(file_path))
        result = self.agent.fix_syntax_errors(file_path)

        if result.success:
            logger.info(
                "Successfully fixed errors",
                errors_fixed=len(result.errors_fixed),
                iterations=result.iterations,
            )
        else:
            logger.warning(
                "Could not fix all errors",
                errors_remaining=len(result.final_errors),
            )

        return result

    def fix_generated_test(
        self, test_content: str, output_path: str | Path
    ) -> tuple[str, SyntaxFixResult]:
        """Fix syntax errors in generated test content and save to file.

        Args:
            test_content: Generated test content
            output_path: Path to save the fixed test

        Returns:
            Tuple of (fixed_content, fix_result)

        """
        output_path = Path(output_path)

        # Ensure directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Write initial content
        output_path.write_text(test_content)
        logger.debug("Wrote initial test to file", output_path=str(output_path))

        # Fix syntax errors
        result = self.fix_test_file(output_path)

        # Read fixed content
        fixed_content = output_path.read_text()

        return fixed_content, result

    def validate_test_file(self, file_path: str | Path) -> bool:
        """Validate that a test file has no syntax errors.

        Args:
            file_path: Path to the test file

        Returns:
            True if file has no syntax errors

        """
        file_path = Path(file_path)
        if not file_path.exists():
            logger.error("File not found", file_path=str(file_path))
            return False

        # Run checks without fixing
        agent = SyntaxFixAgent(openai_client=None, max_iterations=0)
        ts_errors = agent._run_typescript_check(file_path)  # noqa: SLF001
        eslint_errors = agent._run_eslint_check(file_path)  # noqa: SLF001

        total_errors = len(ts_errors) + len(eslint_errors)

        if total_errors == 0:
            logger.info("No syntax errors found in file", file_path=str(file_path))
            return True
        logger.warning(
            "Found syntax errors in file",
            error_count=total_errors,
            file_path=str(file_path),
        )
        return False
