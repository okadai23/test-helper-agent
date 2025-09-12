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

| Command              | Description         |
| -------------------- | ------------------- |
| `nox -s lint`        | Run code linting    |
| `nox -s format_code` | Format code         |
| `nox -s typing`      | Run type checking   |
| `nox -s test`        | Run all tests       |
| `nox -s security`    | Run security checks |
| `nox -s docs`        | Build documentation |
| `nox -s ci`          | Run all CI checks   |

This project uses `nox` for task automation.

### Testing

```bash
# Run all tests
nox -s test

# Run specific test file
uv run pytest tests/unit/clean_interfaces/test_app.py

# Run with coverage
uv run pytest --cov=src --cov-report=html
```

### E2E Web (Playwright)

Sample web apps for E2E validation live under `test_sites/`. A ready-to-run Playwright template is provided.

Install and run:

```bash
uv add --dev playwright pytest pytest-asyncio
uv run python -m playwright install chromium
uv run pytest -q tests/e2e_web
```

Docs: see `docs/development/e2e-web.md` for detailed usage and tips.

Run via nox:

```bash
nox -s e2e_web
nox -s e2e_web_headed
nox -s e2e_web_shop_debug
nox -s e2e_web_trace
nox -s e2e_web_video
```

### Code Quality

The project maintains high code quality standards:

-   **Type Checking**: Strict Pyright type checking
-   **Linting**: Comprehensive Ruff rules
-   **Formatting**: Automated with Ruff formatter
-   **Testing**: 80% minimum coverage requirement
-   **Security**: Regular security scanning

## Interface Types

### CLI Interface

The default interface provides a command-line interface using Typer:

```bash
# Run CLI interface
INTERFACE_TYPE=cli uv run python -m clean_interfaces.main
```

Features:

-   Interactive command-line interface
-   Rich terminal output
-   Help documentation
-   Command completion

### REST API Interface

The REST API interface provides HTTP endpoints using FastAPI:

```bash
# Run REST API interface
INTERFACE_TYPE=restapi uv run python -m clean_interfaces.main
```




### Pre-commit Hooks

Pre-commit hooks are configured to automatically format and lint your code.

```bash
# Install pre-commit hooks
uv run pre-commit install
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.