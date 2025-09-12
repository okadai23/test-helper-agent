"""Temporal workflow integrating OpenAI Agents SDK with durable tools.

Follows repository architecture and settings patterns under `test_helper`.
"""

from __future__ import annotations

from datetime import timedelta
from typing import Any
from urllib.parse import urlparse

from temporalio import activity
from temporalio import workflow as _workflow

from test_helper.utils.settings import get_e2e_settings

try:
    from agents import Agent, Runner, tool
except ImportError as exc:  # pragma: no cover - optional extra
    msg = "openai-agents optional dependency missing; install with extras 'agents'"
    raise ImportError(msg) from exc


# -------------------- Activities (Agent Tools Backing) --------------------


@activity.defn
async def add_numbers(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b


def _validate_url_for_fetch(url: str) -> str:
    """Validate URLs to mitigate SSRF and enforce allowed schemes.

    Reads allowed domains and max size from E2E settings in future extensions.
    """
    if not url or not url.strip():
        msg = "URL cannot be empty"
        raise ValueError(msg)
    parsed = urlparse(url.strip())
    if parsed.scheme.lower() not in {"http", "https"}:
        msg = "Only http/https schemes are allowed"
        raise ValueError(msg)
    if not parsed.netloc:
        msg = "URL must include a host"
        raise ValueError(msg)
    # Basic private IP/netloc guardrails can be added here if required
    return url.strip()


@activity.defn
async def fetch_url(url: str, timeout_seconds: int | None = None) -> str:
    """Fetch content from a URL."""
    import httpx

    settings = get_e2e_settings()
    safe_url = _validate_url_for_fetch(url)
    timeout = httpx.Timeout(timeout_seconds or 20)  # type: ignore[no-untyped-call]
    async with httpx.AsyncClient(  # type: ignore[no-untyped-call]
        timeout=timeout,
        headers={"User-Agent": "temporal-openai-agent/1.0"},
        follow_redirects=True,
    ) as client:  # type: ignore[assignment]
        resp = await client.get(safe_url)  # type: ignore[no-untyped-call]
        resp.raise_for_status()
        max_chars = int(getattr(settings, "agent_fetch_max_chars", 20000))
        return str(resp.text[:max_chars])  # type: ignore[arg-type]


@activity.defn
async def log_message(message: str, metadata: dict[str, Any] | None = None) -> str:
    """Log a message to the console."""
    _ = metadata or {}
    import logging

    logger = logging.getLogger(__name__)
    logger.info("[AgentLog] %s", message)
    return "ok"


# -------------------------- Agent Workflow -------------------------------


TASK_QUEUE = "agent-tq"


@_workflow.defn
class AgentWorkflow:
    """Temporal workflow integrating OpenAI Agents SDK."""

    @_workflow.run
    async def run(self, prompt: str) -> str:
        """Execute agent workflow with OpenAI Agents SDK.

        Args:
            prompt: The user prompt to process.

        Returns:
            The agent's response.

        """
        settings = get_e2e_settings()

        # Unused workflow methods - preserved for future use
        _ = prompt  # mark as used
        _ = settings  # mark as used

        # Define agent tools bound to activities
        @tool  # type: ignore[misc]
        async def add(a: int, b: int) -> int:
            result = await _workflow.execute_activity(  # type: ignore[attr-defined]
                add_numbers,
                a,
                b,
                start_to_close_timeout=timedelta(seconds=30),
            )
            return int(result)  # type: ignore[arg-type]

        @tool  # type: ignore[misc]
        async def fetch(url: str) -> str:
            result = await _workflow.execute_activity(  # type: ignore[attr-defined]
                fetch_url,
                url,
                30,
                start_to_close_timeout=timedelta(seconds=60),
            )
            return str(result)  # type: ignore[arg-type]

        @tool  # type: ignore[misc]
        async def log(message: str) -> str:
            result = await _workflow.execute_activity(  # type: ignore[attr-defined]
                log_message,
                message,
                None,
                start_to_close_timeout=timedelta(seconds=15),
            )
            return str(result)  # type: ignore[arg-type]

        agent = Agent(
            name="TemporalAgent",
            instructions=(
                "You are a durable agent running in a Temporal workflow. "
                "Use the tools to accomplish tasks and cite sources when using fetch()."
            ),
            tools=[add, fetch, log],  # type: ignore[list-item]
        )

        result = await Runner.run(agent, input=prompt)
        final = getattr(result, "final_output", None) or getattr(result, "output", None)
        return str(final) if final is not None else str(result)


__all__ = [
    "TASK_QUEUE",
    "AgentWorkflow",
    "add_numbers",
    "fetch_url",
    "log_message",
]
