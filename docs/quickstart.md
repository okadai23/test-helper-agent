# Quick Start

This guide shows you how to get the Test Helper Agent running and generate your first E2E test.

## Prerequisites

Before you begin, ensure you have completed the [Installation](./installation.md) steps, including:

-   ✅ Cloning the repository.
-   ✅ Installing dependencies with `uv sync --extra dev`.
-   ✅ Configuring your `.env` file.
-   ✅ Starting the background services with `docker-compose up -d`.

## Basic Usage

The primary way to interact with the agent is through the `test-helper` CLI.

### 1. Create a Project Workspace

First, create a new project workspace. This will be a directory where the agent stores all tests, history, and reports for a specific application.

```bash
# Create a new project named "my-app"
uv run test-helper project create --project-name "my-app"
```

### 2. Capture a User Flow

Next, instruct the agent to capture a user flow from a live URL. Provide a natural language prompt describing the actions to perform.

```bash
# Tell the agent to go to a URL and perform a login
uv run test-helper capture --project-name "my-app" \
  --url "http://example.com/login" \
  --prompt "Enter 'user@example.com' into the email field, 'password123' into the password field, and click the 'Log In' button."
```

The agent will use Playwright MCP to execute these steps in a browser.

### 3. Generate the Test Code

Once the capture is complete, generate the Playwright test code from the recorded session.

```bash
# Generate a test file from the last capture session
uv run test-helper generate --project-name "my-app"
```

This will create a new `*.spec.ts` file inside the `data/projects/my-app/tests/` directory.

### 4. Execute the Test

Run the newly generated test to verify it works as expected.

```bash
# Execute the tests for the "my-app" project
uv run test-helper execute --project-name "my-app"
```

The agent will run the Playwright tests and output the results.

## What's Next?

-   **Fix Broken Tests**: Learn how to use the `fix` command to automatically repair failing tests.
-   **Explore the Guides**: Dive deeper into the [CLI Guide](./guides/cli.md) and other documentation.
-   **Contribute**: Check out the [Development Guide](./development/contributing.md) to learn how you can contribute to the project.