"""Diagnostic agent using OpenAI SDK for intelligent failure analysis."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from test_helper.agents.openai_adapter import OpenAIAgentAdapter
from test_helper.models.diagnostic import (
    DiagnosisResult,
    FailureCategory,
    FlakinessAnalysis,
    TestLogEntry,
)
from test_helper.utils.settings import get_e2e_settings

# Constants for diagnostic thresholds
CONFIDENCE_THRESHOLD = 0.5
FLAKINESS_LOWER_BOUND = 0.2
FLAKINESS_UPPER_BOUND = 0.8


@dataclass
class DiagnosticAgent:
    """Analyzes failing test logs and categorizes root cause using AI."""

    openai_client: Any

    @property
    def name(self) -> str:
        """Return agent name."""
        return "diagnostic"

    @property
    def adapter(self) -> OpenAIAgentAdapter:
        """Get OpenAI adapter for diagnostic operations."""
        settings = get_e2e_settings()
        return OpenAIAgentAdapter(
            client=self.openai_client,
            model=settings.openai_model,  # Use model from environment variable
        )

    def diagnose_failure(
        self, logs: list[TestLogEntry] | list[dict[str, Any]]
    ) -> DiagnosisResult:
        """Intelligently categorize failure based on log messages using AI.

        Args:
            logs: List of log entries with messages and metadata

        Returns:
            Diagnosis with category, confidence, and recommendations

        """
        # Prepare log text for analysis
        log_entries: list[str] = []
        for entry in logs:
            if isinstance(entry, TestLogEntry):
                timestamp = entry.timestamp
                level = entry.level
                message = entry.message
                stack_trace = entry.stack_trace
            else:
                timestamp = entry.get("timestamp", "")
                level = entry.get("level", "INFO")
                message = entry.get("message", "")
                stack_trace = entry.get("stack_trace", "")

            log_entry = f"[{timestamp}] {level}: {message}"
            if stack_trace:
                log_entry += f"\nStack trace: {stack_trace}"
            log_entries.append(log_entry)

        log_text = "\n".join(log_entries) if log_entries else "No logs available"

        # Use OpenAI to analyze the failure
        system_prompt = """You are an expert E2E test diagnostician specializing in Playwright test failures.
        Analyze test failure logs and provide accurate diagnosis.

        Categories of failures:
        - selector: Element selector issues (not found, invalid, changed)
        - timing: Timeout issues, race conditions, slow loading
        - assertion: Failed assertions, unexpected values
        - network: Network errors, API failures, resource loading issues
        - authentication: Login failures, session issues, permission errors
        - data: Test data issues, state management problems
        - environment: Configuration issues, browser problems
        - flaky: Intermittent failures, non-deterministic behavior
        - unknown: Cannot determine root cause

        Return your analysis as a JSON object with this structure:
        {
            "category": "<main_category>",
            "confidence": <0.0-1.0>,
            "root_cause": "<detailed explanation>",
            "affected_elements": ["<selectors or components>"],
            "recommendations": [
                "<specific fix recommendation 1>",
                "<specific fix recommendation 2>"
            ],
            "is_flaky": <true/false>,
            "severity": "<low/medium/high/critical>"
        }
        """

        user_prompt = f"""Analyze these test failure logs and diagnose the issue:

        {log_text}

        Provide a detailed diagnosis with specific recommendations for fixing the issue.
        """

        try:
            response = self.adapter.diagnose_with_prompts(
                system=system_prompt,
                user=user_prompt,
            )

            if response:
                # Parse JSON response
                result_dict = json.loads(response)
                # Convert to DiagnosisResult model
                result_dict["category"] = FailureCategory(
                    result_dict.get("category", "unknown")
                )
                return DiagnosisResult(**result_dict)

        except (json.JSONDecodeError, Exception):
            pass  # Log error silently - fallback will be used

        # Fallback to rule-based diagnosis if AI fails
        return self._fallback_diagnosis(logs)

    def _fallback_diagnosis(
        self, logs: list[TestLogEntry] | list[dict[str, Any]] | dict[str, Any]
    ) -> DiagnosisResult:
        """Provide basic rule-based diagnosis as fallback.

        Args:
            logs: List of log entries or dict containing logs

        Returns:
            Basic diagnosis

        """
        # Handle both direct logs list and logs within a dict
        if isinstance(logs, dict):
            logs_list: list[Any] = logs.get("logs", [])
        else:
            logs_list: list[Any] = logs
        text = " ".join([str(entry.get("message", "")) for entry in logs_list]).lower()

        # Rule-based categorization
        category = "unknown"
        confidence = 0.3
        root_cause = "Unable to determine root cause from logs"
        recommendations = ["Review test logs manually", "Check test environment"]

        if "element not found" in text or "no such element" in text:
            category = "selector"
            confidence = 0.8
            root_cause = "Element selector is not finding the target element"
            recommendations = [
                "Verify the selector is correct and unique",
                "Check if element is rendered when expected",
                "Add proper wait conditions before interacting",
            ]
        elif "timeout" in text or "timed out" in text:
            category = "timing"
            confidence = 0.7
            root_cause = "Operation exceeded timeout waiting for condition"
            recommendations = [
                "Increase timeout values",
                "Add explicit waits for elements",
                "Check if application is slow to load",
            ]
        elif "assert" in text or "expected" in text:
            category = "assertion"
            confidence = 0.7
            root_cause = "Assertion failed - actual value doesn't match expected"
            recommendations = [
                "Verify expected values are correct",
                "Check if application behavior has changed",
                "Add debugging to see actual values",
            ]
        elif "network" in text or "fetch" in text or "xhr" in text:
            category = "network"
            confidence = 0.6
            root_cause = "Network request failed or returned unexpected response"
            recommendations = [
                "Check API endpoints are accessible",
                "Verify network conditions",
                "Add retry logic for network operations",
            ]
        elif "login" in text or "auth" in text or "permission" in text:
            category = "authentication"
            confidence = 0.6
            root_cause = "Authentication or authorization issue"
            recommendations = [
                "Verify test credentials are valid",
                "Check authentication flow",
                "Ensure proper session handling",
            ]

        return DiagnosisResult(
            category=FailureCategory(category),
            confidence=confidence,
            root_cause=root_cause,
            affected_elements=[],
            recommendations=recommendations,
            is_flaky=confidence < CONFIDENCE_THRESHOLD,
            severity="medium" if confidence > CONFIDENCE_THRESHOLD else "low",
        )

    def analyze_flakiness(
        self, failure_history: list[dict[str, Any]]
    ) -> FlakinessAnalysis:
        """Analyze pattern of failures to detect flaky tests.

        Args:
            failure_history: History of test failures with timestamps

        Returns:
            Flakiness analysis with patterns and recommendations

        """
        if not failure_history:
            return FlakinessAnalysis(
                total_runs=0,
                failure_count=0,
                failure_rate=0.0,
                patterns=["No failure history available"],
                time_based_correlation=False,
                environment_correlation={},
                recommended_retry_count=1,
                confidence=0.0,
            )

        # Analyze failure patterns
        total_runs = len(failure_history)
        failures = [f for f in failure_history if f.get("failed", False)]
        failure_rate = len(failures) / total_runs if total_runs > 0 else 0

        # Check for intermittent failures
        is_flaky = FLAKINESS_LOWER_BOUND < failure_rate < FLAKINESS_UPPER_BOUND

        system_prompt = """You are an expert at detecting flaky tests.
        Analyze test failure patterns and identify if a test is flaky.
        Return analysis as JSON:
        {
            "is_flaky": <true/false>,
            "confidence": <0.0-1.0>,
            "pattern": "<description of failure pattern>",
            "likely_causes": ["<cause1>", "<cause2>"],
            "stabilization_recommendations": ["<recommendation1>", "<recommendation2>"]
        }
        """

        user_prompt = f"""Analyze this test failure history:
        Total runs: {total_runs}
        Failures: {len(failures)}
        Failure rate: {failure_rate:.2%}

        Recent failures:
        {json.dumps(failures[:10], indent=2)}
        """

        try:
            response = self.adapter.diagnose_with_prompts(
                system=system_prompt,
                user=user_prompt,
            )

            if response:
                # Parse JSON response
                result = json.loads(response)
                # Convert to FlakinessAnalysis model
                return FlakinessAnalysis(
                    total_runs=total_runs,
                    failure_count=len(failures),
                    failure_rate=failure_rate,
                    patterns=[result.get("pattern", "")],
                    time_based_correlation=result.get("is_flaky", False),
                    environment_correlation={},
                    recommended_retry_count=3 if result.get("is_flaky", False) else 1,
                    confidence=result.get("confidence", 0.5),
                )

        except (json.JSONDecodeError, Exception):
            pass  # Log error silently - fallback will be used

        # Fallback analysis
        patterns = [
            f"Test fails {failure_rate:.0%} of the time",
        ]
        if is_flaky:
            patterns.extend(
                [
                    "Race conditions detected",
                    "Timing issues present",
                    "External dependencies unstable",
                ]
            )
        else:
            patterns.append("Consistent failure pattern")

        return FlakinessAnalysis(
            total_runs=total_runs,
            failure_count=len(failures),
            failure_rate=failure_rate,
            patterns=patterns,
            time_based_correlation=is_flaky,
            environment_correlation={},
            recommended_retry_count=3 if is_flaky else 1,
            confidence=0.6 if is_flaky else 0.8,
        )
