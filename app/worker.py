from __future__ import annotations

import asyncio
import os
from typing import Sequence

from temporalio.client import Client
from temporalio.worker import Worker

from app.activities import add_numbers, fetch_url, log_message
from app.workflow import AgentWorkflow, TASK_QUEUE


async def run_worker(task_queue: str = TASK_QUEUE) -> None:
    target_host = os.environ.get("TEMPORAL_ADDRESS", "localhost:7233")
    client = await Client.connect(target_host)

    activities: Sequence[object] = [add_numbers, fetch_url, log_message]
    workflows: Sequence[type] = [AgentWorkflow]

    worker = Worker(
        client,
        task_queue=task_queue,
        activities=activities,
        workflows=workflows,
    )

    print(f"Worker connected to {target_host}, listening on task queue '{task_queue}'")
    await worker.run()


if __name__ == "__main__":
    asyncio.run(run_worker())

