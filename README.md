# Test Helper Agent

An AI-powered E2E test automation agent that generates and maintains Playwright tests from natural language.

## Overview

This project provides an AI agent system designed to automate the creation and maintenance of end-to-end (E2E) tests for web applications. By leveraging natural language instructions, it can perform browser interactions, generate robust Playwright test code, and even automatically fix broken tests.

The system is built on a modern stack including:

-   **Playwright MCP**: For enabling Large Language Models (LLMs) to interact with and control a web browser.
-   **OpenAI Agents SDK**: For building and orchestrating the AI agents.
-   **Temporal**: For creating durable and reliable workflows that manage the entire test lifecycle (capture, generation, execution, and fixing).

## Features

-   **Natural Language to E2E Tests**: Generate comprehensive E2E tests simply by describing a user flow in natural language.
-   **Automated Test Generation**: Captures browser interactions and converts them into clean, deterministic Playwright test code (`*.spec.ts`).
-   **Auto-Healing Tests**: Automatically detects and fixes failing tests caused by UI changes (e.g., updated selectors).
-   **Black-box and White-box Modes**: Supports both crawling a live application (black-box) and analyzing source code for test generation (white-box).
-   **Accessibility & Usability Testing**: Integrates `@axe-core/playwright` to perform automated accessibility checks during test execution.
-   **Durable Workflows**: Uses Temporal to orchestrate the complex, long-running processes of test generation and maintenance, ensuring reliability and re-runnability.
-   **Multiple Interfaces**: Provides both a CLI (`test-helper`) and a REST API for interacting with the system.

## Project Structure

```
test-helper-agent/
├── src/test_helper/            # Main application code
│   ├── __init__.py
│   ├── app.py                  # Application factory and setup
│   ├── main.py                 # CLI entry point
│   ├── agents/                 # AI agent implementations
│   ├── services/               # Core business logic (generator, executor, etc.)
│   ├── lib/                    # Libraries for external services (Playwright MCP, Temporal)
│   ├── interfaces/             # CLI and REST API interface implementations
│   ├── models/                 # Pydantic data models
│   └── utils/                  # Utility modules
├── specs/                      # Feature specifications and research
├── tests/                      # Test suite (unit, integration, e2e)
├── docs/                       # Documentation
├── .env.example                # Example environment configuration
├── pyproject.toml              # Project configuration and dependencies
├── docker-compose.yml          # Docker services (Temporal, Playwright MCP, etc.)
└── README.md                   # This file
```

## Quick Start

### Prerequisites

-   Python 3.13 or higher
-   Docker and Docker Compose
-   `uv` (Python package manager)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd test-helper-agent
    ```

2.  **Set up the environment:**
    ```bash
    # Copy the example environment file
    cp .env.example .env

    # Add your OpenAI API key and other configurations to .env
    ```

3.  **Install dependencies:**
    ```bash
    # Create a virtual environment and install dependencies
    uv sync --extra dev
    ```

4.  **Start background services:**
    ```bash
    # This will start Temporal, Playwright MCP, and other required services
    docker-compose up -d
    ```

### Running the Application

The application provides a CLI for interacting with the agent.

```bash
# Show the main help message
uv run test-helper --help

# Example: Create a new test project (workspace)
uv run test-helper project create --project-name "my-test-project"

# Example: Capture a user flow from a URL
uv run test-helper capture --project-name "my-test-project" --url "http://example.com" --prompt "Log in and navigate to the dashboard."

# Example: Generate a Playwright test from the captured session
uv run test-helper generate --project-name "my-test-project"
```

## Development

### Development Commands

This project uses `nox` for task automation.

| Command              | Description                               |
| -------------------- | ----------------------------------------- |
| `nox -s lint`        | Run code linting with Ruff.               |
| `nox -s format_code` | Format code with Ruff.                    |
| `nox -s typing`      | Run static type checking with Pyright.    |
| `nox -s test`        | Run all tests with pytest.                |
| `nox -s security`    | Run security checks with `pip-audit`.     |
| `nox -s ci`          | Run all CI checks (lint, format, typing, test). |

### Pre-commit Hooks

Pre-commit hooks are configured to automatically format and lint your code.

```bash
# Install pre-commit hooks
uv run pre-commit install
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.