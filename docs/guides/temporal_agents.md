# Temporal + OpenAI Agents Integration

This guide explains how the OpenAI Agents SDK is integrated into our Temporal workflows using the existing `test_helper` architecture.

## Overview

- Workflow: `test_helper.services.agent_workflows.AgentWorkflow`
- Tools as Activities: `add_numbers`, `fetch_url`, `log_message`
- Task queue: `agent-tq`
- Settings: `E2ESettings` controls Temporal host/namespace, model, and `agent_fetch_max_chars`

## Running

- Ensure Temporal is running and `openai-agents` extra is installed.
- Use the CLI:

```bash
uv run test-helper workflows agent "Plan a 2-day trip to Tokyo; use fetch where helpful"
```

## Security & Reliability

- `fetch_url` validates URLs (http/https only, host required) to mitigate SSRF.
- Response size is truncated by `agent_fetch_max_chars` from settings.
- Activities encapsulate side effects for durability and observability.