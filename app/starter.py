from __future__ import annotations

import argparse
import asyncio
import os
from typing import Optional

from temporalio.client import Client

from app.workflow import AgentWorkflow, TASK_QUEUE


async def start(prompt: str, workflow_id: Optional[str] = None) -> str:
    target_host = os.environ.get("TEMPORAL_ADDRESS", "localhost:7233")
    client = await Client.connect(target_host)

    handle = await client.start_workflow(
        AgentWorkflow.run,
        prompt,
        id=workflow_id or f"agent-workflow-{os.getpid()}-{abs(hash(prompt))}",
        task_queue=TASK_QUEUE,
    )

    print(f"Started workflow: {handle.id}")
    result = await handle.result()
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Start AgentWorkflow with a user prompt")
    parser.add_argument("prompt", help="User prompt for the agent")
    parser.add_argument("--workflow-id", dest="workflow_id", help="Custom workflow ID", default=None)
    args = parser.parse_args()

    result = asyncio.run(start(args.prompt, args.workflow_id))
    print("\n=== Workflow Result ===")
    print(result)


if __name__ == "__main__":
    main()

