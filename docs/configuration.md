# Configuration Guide

The Test Helper Agent uses environment variables for configuration, with support for `.env` files.

## Configuration Methods

### 1. Environment Variables

Set environment variables directly in your shell before running a command:

```bash
export OPENAI_API_KEY="your-key-here"
uv run test-helper project list
```

### 2. `.env` File

Create a `.env` file in the project root. This is the recommended approach for managing keys and settings.

```ini
# .env
OPENAI_API_KEY="your-key-here"

# Optional: Specify a different model
AGENT_MODEL="gpt-4o"

# Optional: Set the backend for agents and workflows
AGENT_BACKEND="sdk" # "sdk" or "mock"
TEMPORAL_BACKEND="sdk" # "sdk" or "mock"
```

## Core Configuration Options

| Variable           | Description                                       | Default        | Options          |
| ------------------ | ------------------------------------------------- | -------------- | ---------------- |
| `OPENAI_API_KEY`   | **Required.** Your API key for OpenAI services.       | `None`         | Any valid key    |
| `AGENT_MODEL`      | The OpenAI model to use for the agent.            | `gpt-4o-mini`  | `gpt-5-nano`, etc. |
| `AGENT_BACKEND`    | The backend for the agent service.                | `mock`         | `sdk`, `mock`    |
| `TEMPORAL_BACKEND` | The backend for the Temporal workflow service.    | `mock`         | `sdk`, `mock`    |
| `TEMPORAL_HOST`    | The host for the Temporal frontend service.       | `localhost`    | Hostname or IP   |
| `TEMPORAL_PORT`    | The port for the Temporal frontend service.       | `7233`         | Port number      |

### Logging Configuration

| Variable        | Description       | Default | Options                                         |
| --------------- | ----------------- | ------- | ----------------------------------------------- |
| `LOG_LEVEL`     | Logging verbosity | `INFO`  | `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` |
| `LOG_FORMAT`    | Output format     | `json`  | `json`, `console`                               |
| `LOG_FILE_PATH` | Log file location | `None`  | Any valid file path                             |

## Best Practices

-   **Use `.env` for Secrets**: Always use a `.env` file for your `OPENAI_API_KEY` and add `.env` to your `.gitignore` to avoid committing secrets.
-   **Start with Mocks**: When developing or testing, use the `mock` backends (`AGENT_BACKEND=mock`, `TEMPORAL_BACKEND=mock`) to avoid making real API calls.
-   **Verify Configuration**: Ensure your Docker services (Temporal, etc.) are running before switching to the `sdk` backend.