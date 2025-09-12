# CLI Interface Guide

The Command Line Interface (CLI) is the primary way to interact with the Test Helper Agent.

## Overview

The CLI is built using [Typer](https://typer.tiangolo.com/) and provides a structured set of commands to manage the entire E2E test lifecycle.

## Running Commands

All commands are run through the `test-helper` entrypoint using `uv`.

```bash
# Show the main help message
uv run test-helper --help
```

This will display the main command groups available:

-   `project`: Manage project workspaces.
-   `capture`: Capture user flows and generate interaction traces.
-   `generate`: Generate Playwright test code from captures.
-   `execute`: Run tests.
-   `fix`: Automatically fix broken tests.

## Command Examples

### `project`

Manage workspaces for different applications under test.

```bash
# Create a new project
uv run test-helper project create --project-name "my-e-commerce-app"

# List all projects
uv run test-helper project list
```

### `capture`

Start a browser session to record a user flow based on a natural language prompt.

```bash
# Capture a login sequence
uv run test-helper capture --project-name "my-e-commerce-app" \
  --url "https://my-app.com/login" \
  --prompt "Log in with username 'test' and password 'password'."
```

### `generate`

Generate a Playwright test file from a captured session.

```bash
# Generate a test from the latest capture
uv run test-helper generate --project-name "my-e-commerce-app"
```

### `execute`

Run the generated Playwright tests.

```bash
# Run all tests for a project
uv run test-helper execute --project-name "my-e-commerce-app"
```

### `fix`

Attempt to automatically repair tests that failed during the last execution.

```bash
# Automatically fix failing tests
uv run test-helper fix --project-name "my-e-commerce-app" --auto-apply
```

## Advanced Usage

### Overriding Environment Variables

You can override settings for a single command run:

```bash
# Use a different model for a specific capture task
AGENT_MODEL=gpt-5-nano uv run test-helper capture --project-name "my-app" --prompt "..."
```

### Shell Integration

For convenience, you can add a shell alias:

```bash
# Add to your .bashrc or .zshrc
alias tha='uv run test-helper'

# Now you can run commands like this:
tha project list
tha capture --project-name "my-app" --prompt "..."
```
