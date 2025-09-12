# Temporal + OpenAI Agents (Python) Demo

This project integrates Temporal Python SDK with the OpenAI Agents SDK. An AI Agent runs inside a Temporal workflow and calls durable tools implemented as Temporal Activities.

Reference: `temporalio/contrib/openai_agents/README.md` from Temporal Python SDK.

## Prerequisites

- Python 3.10+
- Temporal server running (e.g., `docker run --name temporal -p 7233:7233 temporalio/auto:1.25`)
- OpenAI-compatible Agents SDK installed (see requirements)

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Optional environment variables:

- `TEMPORAL_ADDRESS` (default `localhost:7233`)
- `OPENAI_API_KEY` required by the Agents SDK if it uses OpenAI models

## Run

Start the worker:

```bash
python -m app.worker
```

In a separate terminal, start a workflow with your prompt:

```bash
python -m app.starter "Build a 2-day travel plan for Tokyo; use fetch if helpful"
```

You should see the workflow start and the final agent output printed. Agent tools available:

- `add(a, b)` → sums numbers via Activity
- `fetch(url)` → HTTP GET with timeout via Activity
- `log(message)` → server-side log via Activity

## Project Structure

- `app/activities.py` — Activity implementations backing agent tools
- `app/workflow.py` — `AgentWorkflow` integrating the Agent and tools
- `app/worker.py` — Temporal worker registering workflow and activities
- `app/starter.py` — Simple CLI to start the workflow

## Notes

- Tools execute as Activities to ensure durability and visibility in Temporal. The agent core runs in the workflow so conversation state is fully replayable.
- For model/provider configuration, follow your Agents SDK documentation. This demo assumes defaults provided by `openai-agents` package.