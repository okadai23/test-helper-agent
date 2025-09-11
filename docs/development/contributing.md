# Contributing Guide

Thank you for considering contributing to the Test Helper Agent! This guide will help you get started.

## Development Setup

### Prerequisites

-   Python 3.13 or higher
-   Docker and Docker Compose
-   [uv](https://github.com/astral-sh/uv) for dependency management
-   Git for version control

### Setup Steps

1.  **Fork and clone the repository**

    ```bash
    git clone <your-fork-url>
    cd test-helper-agent
    ```

2.  **Install dependencies**

    ```bash
    # This creates a .venv and installs all required packages
    uv sync --extra dev
    ```

3.  **Set up pre-commit hooks**

    ```bash
    uv run pre-commit install
    ```

4.  **Configure your environment**

    ```bash
    cp .env.example .env
    # Add your OPENAI_API_KEY to the .env file
    ```

5.  **Start background services**

    ```bash
    docker-compose up -d
    ```

6.  **Activate the virtual environment**

    ```bash
    source .venv/bin/activate
    ```

## Development Workflow

1.  **Create a feature branch**:
    ```bash
    git checkout -b feature/your-amazing-feature
    ```

2.  **Make your changes**: Write code and add tests.

3.  **Run quality checks**: Use `nox` to run all checks.
    ```bash
    # Run all CI checks (lint, format, typing, test)
    nox -s ci
    ```

4.  **Commit your changes**: Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification.
    ```bash
    git commit -m "feat: add new agent capability"
    ```

5.  **Create a Pull Request**: Push your branch and open a PR against the `main` branch.

## Code Style

-   **Formatting**: We use [Ruff Formatter](https://docs.astral.sh/ruff/formatter/). The pre-commit hook will handle this automatically.
-   **Linting**: We use [Ruff Linter](https://docs.astral.sh/ruff/linter/) with a comprehensive set of rules defined in `pyproject.toml`.
-   **Type Hints**: All code must be fully type-hinted and pass `pyright --strict`.

## Testing

-   All new features or fixes must be accompanied by tests.
-   Run all tests with `nox -s test`.
-   The project includes unit, integration, and E2E tests.

## Documentation

-   Update documentation in the `docs/` directory for any user-facing changes.
-   Build and serve the documentation locally:
    ```bash
    uv run mkdocs serve
    ```