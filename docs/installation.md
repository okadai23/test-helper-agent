# Installation

This guide covers the installation of the Test Helper Agent.

## Requirements

-   Python 3.13 or higher
-   Docker and Docker Compose
-   `uv` (Python package manager)

## Installing `uv`

If you don't have `uv` installed, you can install it using:

=== "Linux/macOS"

    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

=== "Windows"

    ```powershell
    powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
    ```

## Installation Steps

1.  **Clone the repository**

    ```bash
    git clone <repository-url>
    cd test-helper-agent
    ```

2.  **Set up the environment**

    Copy the example environment file and add your OpenAI API key.

    ```bash
    cp .env.example .env
    # Now, edit .env to add your API key
    ```

3.  **Install dependencies**

    This command creates a virtual environment and installs all necessary packages.

    ```bash
    uv sync --extra dev
    ```

4.  **Start background services**

    The agent relies on several background services, including Temporal and Playwright MCP. Start them with Docker Compose.

    ```bash
    docker-compose up -d
    ```

## Verification

Verify the installation by running the CLI's help command:

```bash
# Show help for the main command
uv run test-helper --help
```

You should see the help output for the `test-helper` command-line interface.

## Next Steps

-   Read the [Quick Start](quickstart.md) guide to learn how to use the agent.
-   Explore the [Development Guide](development/contributing.md) for contribution guidelines.