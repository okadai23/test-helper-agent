from __future__ import annotations

from datetime import timedelta
from typing import Any

from temporalio import workflow


# We use the OpenAI Agents SDK. Tools below delegate to Temporal activities for durability.
try:
    # The Agents SDK public API
    from openai_agents import Agent, Runner, tool
except Exception as exc:  # pragma: no cover - keep import error clear at runtime
    raise RuntimeError(
        "openai-agents package is required. Install with `pip install openai-agents`."
    ) from exc


TASK_QUEUE = "openai-agent-task-queue"


@workflow.defn
class AgentWorkflow:
    @workflow.run
    async def run(self, prompt: str) -> str:
        # Define tools bound to workflow context that call Activities.
        @tool
        async def add(a: int, b: int) -> int:
            return await workflow.execute_activity(
                "add_numbers",
                a,
                b,
                start_to_close_timeout=timedelta(seconds=30),
            )

        @tool
        async def fetch(url: str) -> str:
            return await workflow.execute_activity(
                "fetch_url",
                url,
                30,
                start_to_close_timeout=timedelta(seconds=60),
            )

        @tool
        async def log(message: str) -> str:
            return await workflow.execute_activity(
                "log_message",
                message,
                None,
                start_to_close_timeout=timedelta(seconds=15),
            )

        agent = Agent(
            name="TemporalAgent",
            instructions=(
                "You are a helpful software agent running inside a Temporal workflow. "
                "Use the provided tools to complete the user's task. "
                "Prefer fetching real data with fetch(url) when relevant and show your work."
            ),
            tools=[add, fetch, log],
        )

        result = await Runner.run(agent, input=prompt)

        # Try common result attributes, fallback to str for flexibility across SDK versions
        final = getattr(result, "final_output", None)
        if final is None:
            final = getattr(result, "output", None)
        if final is None:
            final = str(result)
        return final

