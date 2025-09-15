"""Fix agent using OpenAI SDK to propose intelligent test fixes."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from test_helper.agents.openai_adapter import OpenAIAgentAdapter
from test_helper.utils.settings import get_e2e_settings


@dataclass
class FixAgent:
    """Suggests intelligent changes to fix failing tests using AI."""

    openai_client: Any
    storage: Any

    @property
    def name(self) -> str:
        """Return agent name."""
        return "fix"

    @property
    def adapter(self) -> OpenAIAgentAdapter:
        """Get OpenAI adapter for fix operations."""
        settings = get_e2e_settings()
        return OpenAIAgentAdapter(
            client=self.openai_client,
            model=settings.openai_model,  # Use model from environment variable
        )

    def propose_fix(self, failure: dict[str, Any]) -> dict[str, Any]:
        """Propose intelligent fix plan for a test failure using AI.

        Args:
            failure: Failure details including category, logs, and context

        Returns:
            Fix proposal with specific changes and confidence level

        """
        category = failure.get("category", "unknown")
        details = failure.get("details", {})
        test_code = failure.get("test_code", "")
        error_message = failure.get("error_message", "")
        stack_trace = failure.get("stack_trace", "")
        logs = failure.get("logs", [])

        # Prepare context for AI
        system_prompt = """You are an expert Playwright test engineer specializing in fixing test failures.
        Analyze test failures and propose specific, actionable fixes.

        Common fix types:
        - modify_selector: Change element selector (provide alternatives)
        - add_wait: Add wait conditions for elements or network
        - update_assertion: Fix assertion expected values
        - increase_timeout: Adjust timeout values
        - handle_dynamic_content: Add logic for dynamic content
        - fix_test_data: Update test data or fixtures
        - add_error_handling: Add try-catch or error recovery
        - refactor_flow: Restructure test flow for reliability

        Return your fix proposal as JSON:
        {
            "changes": [
                {
                    "type": "<fix_type>",
                    "description": "<what to change>",
                    "from": "<current_code_or_value>",
                    "to": "<proposed_code_or_value>",
                    "reason": "<why this fixes the issue>",
                    "line_number": <line_number_if_applicable>
                }
            ],
            "category": "<failure_category>",
            "confidence": <0.0-1.0>,
            "explanation": "<detailed explanation of the fix>",
            "alternative_fixes": [
                {
                    "description": "<alternative approach>",
                    "pros": "<advantages>",
                    "cons": "<disadvantages>"
                }
            ],
            "prevention": "<how to prevent similar issues>"
        }
        """

        # Build context from failure details
        log_text = "\n".join([str(log.get("message", "")) for log in logs[:20]])

        user_prompt = f"""Fix this test failure:

        Failure Category: {category}
        Error Message: {error_message}

        Stack Trace:
        {stack_trace}

        Test Code:
        ```typescript
        {test_code}
        ```

        Recent Logs:
        {log_text}

        Additional Details:
        {json.dumps(details, indent=2)}
        Provide specific code changes to fix this test.
        """

        try:
            response = self.adapter.fix_test(
                system=system_prompt,
                user=user_prompt,
            )

            if response:
                # Parse JSON response
                fix_proposal = json.loads(response)
                # Ensure category matches if we have one
                if category != "unknown":
                    fix_proposal["category"] = category
                return fix_proposal

        except (json.JSONDecodeError, Exception):
            pass  # Log error silently - fallback will be used

        # Fallback to intelligent rule-based fixes
        return self._generate_fallback_fix(failure)

    def _generate_fallback_fix(self, failure: dict[str, Any]) -> dict[str, Any]:
        """Generate rule-based fix proposal as fallback.

        Args:
            failure: Failure details

        Returns:
            Basic fix proposal

        """
        category = failure.get("category", "unknown")
        details = failure.get("details", {})
        error_message = failure.get("error_message", "").lower()

        changes: list[dict[str, Any]] = []
        confidence = 0.3

        if category == "selector" or "element not found" in error_message:
            # Selector-related fixes
            selector = details.get("selector", "#unknown")
            alternatives = details.get("alternatives", [])

            changes.append(
                {
                    "type": "modify_selector",
                    "description": "Update selector to use more reliable locator",
                    "from": selector,
                    "to": alternatives[0]
                    if alternatives
                    else "[data-testid='element']",
                    "reason": "Current selector is not finding the element",
                }
            )
            changes.append(
                {
                    "type": "add_wait",
                    "description": "Add explicit wait for element",
                    "from": f"await page.click('{selector}')",
                    "to": f"await page.waitForSelector('{selector}', {{ state: 'visible' }});\nawait page.click('{selector}')",
                    "reason": "Element might not be ready when test tries to interact",
                }
            )
            confidence = 0.7

        elif category == "timing" or "timeout" in error_message:
            # Timing-related fixes
            changes.append(
                {
                    "type": "increase_timeout",
                    "description": "Increase timeout for slow operations",
                    "from": "{ timeout: 30000 }",
                    "to": "{ timeout: 60000 }",
                    "reason": "Operation is taking longer than expected",
                }
            )
            changes.append(
                {
                    "type": "add_wait",
                    "description": "Add network idle wait",
                    "from": "await page.goto(url)",
                    "to": "await page.goto(url, { waitUntil: 'networkidle' })",
                    "reason": "Page might have lazy-loaded content",
                }
            )
            confidence = 0.6

        elif category == "assertion" or "expected" in error_message:
            # Assertion-related fixes
            changes.append(
                {
                    "type": "update_assertion",
                    "description": "Update expected value to match actual",
                    "from": "await expect(element).toHaveText('old')",
                    "to": "await expect(element).toHaveText('new')",
                    "reason": "Expected value doesn't match actual application state",
                }
            )
            changes.append(
                {
                    "type": "add_wait",
                    "description": "Wait for value to update",
                    "from": "await expect(element).toHaveText('text')",
                    "to": "await page.waitForTimeout(1000);\nawait expect(element).toHaveText('text')",
                    "reason": "Value might update asynchronously",
                }
            )
            confidence = 0.5

        elif category == "network" or "fetch" in error_message:
            # Network-related fixes
            changes.append(
                {
                    "type": "add_error_handling",
                    "description": "Add network error handling",
                    "from": "await page.goto(url)",
                    "to": "try {\n  await page.goto(url);\n} catch (e) {\n  await page.reload();\n  await page.goto(url);\n}",
                    "reason": "Network requests might fail intermittently",
                }
            )
            confidence = 0.5

        else:
            # Generic fixes for unknown issues
            changes.append(
                {
                    "type": "add_wait",
                    "description": "Add general wait for stability",
                    "from": "",
                    "to": "await page.waitForLoadState('networkidle');",
                    "reason": "Ensure page is fully loaded",
                }
            )
            confidence = 0.3

        return {
            "changes": changes,
            "category": category,
            "confidence": confidence,
            "explanation": f"Proposed fixes for {category} failure based on common patterns",
            "alternative_fixes": [],
            "prevention": "Add proper waits, use stable selectors, and handle errors gracefully",
        }

    def apply_fix(
        self, test_code: str, fix_proposal: dict[str, Any]
    ) -> tuple[str, list[str]]:
        """Apply proposed fixes to test code.

        Args:
            test_code: Original test code
            fix_proposal: Fix proposal with changes

        Returns:
            Tuple of (fixed_code, list_of_applied_changes)

        """
        fixed_code = test_code
        applied_changes: list[str] = []

        for change in fix_proposal.get("changes", []):
            change_type = change.get("type")
            from_code = change.get("from", "")
            to_code = change.get("to", "")

            if from_code and to_code and from_code in fixed_code:
                # Apply simple replacement
                fixed_code = fixed_code.replace(from_code, to_code, 1)
                applied_changes.append(
                    f"Applied {change_type}: {change.get('description', '')}"
                )
            elif change_type == "add_wait" and to_code:
                # Find appropriate place to add wait
                # This is simplified - real implementation would use AST
                lines = fixed_code.split("\n")
                for i, line in enumerate(lines):
                    if "page.goto" in line or "page.click" in line:
                        # Add wait before the action
                        indent = len(line) - len(line.lstrip())
                        wait_line = " " * indent + to_code
                        lines.insert(i, wait_line)
                        applied_changes.append(f"Added wait at line {i + 1}")
                        break
                fixed_code = "\n".join(lines)

        return fixed_code, applied_changes

    def validate_fix(self, original_code: str, fixed_code: str) -> dict[str, Any]:
        """Validate that proposed fix is safe and non-destructive.

        Args:
            original_code: Original test code
            fixed_code: Fixed test code

        Returns:
            Validation result with safety checks

        """
        # Basic validation checks
        validation: dict[str, Any] = {
            "is_valid": True,
            "warnings": [],
            "errors": [],
        }

        # Check that we haven't removed too much
        original_lines = original_code.count("\n")
        fixed_lines = fixed_code.count("\n")

        if fixed_lines < original_lines * 0.8:
            validation["warnings"].append(
                "Significant code reduction detected - verify all test steps are preserved"
            )

        # Check for common issues
        if "page.goto" not in fixed_code and "page.goto" in original_code:
            validation["errors"].append("Navigation step was removed")
            validation["is_valid"] = False

        if "expect" not in fixed_code and "expect" in original_code:
            validation["warnings"].append("Assertions may have been removed")

        # Check for syntax issues (simplified)
        if fixed_code.count("(") != fixed_code.count(")"):
            validation["errors"].append("Unbalanced parentheses")
            validation["is_valid"] = False

        if fixed_code.count("{") != fixed_code.count("}"):
            validation["errors"].append("Unbalanced braces")
            validation["is_valid"] = False

        return validation
