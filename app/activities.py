from __future__ import annotations

import json
from datetime import timedelta
from typing import Any, Dict

import httpx
from temporalio import activity


@activity.defn
async def add_numbers(a: int, b: int) -> int:
    return a + b


@activity.defn
async def fetch_url(url: str, timeout_seconds: int | None = 20) -> str:
    timeout = httpx.Timeout(timeout_seconds or 20)
    async with httpx.AsyncClient(timeout=timeout, headers={"User-Agent": "temporal-openai-agent-demo/1.0"}) as client:
        resp = await client.get(url)
        resp.raise_for_status()
        # Only return text content to keep payloads light
        return resp.text[:20000]


@activity.defn
async def log_message(message: str, metadata: Dict[str, Any] | None = None) -> str:
    payload = {"message": message, "metadata": metadata or {}}
    print(f"[AgentLog] {json.dumps(payload, ensure_ascii=False)}")
    return "ok"

