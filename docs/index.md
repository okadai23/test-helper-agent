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

## Quick Start

Refer to the [Installation](./installation.md) and [Quickstart](./quickstart.md) guides for details on how to set up and run the application.

## Development

For details on how to contribute, set up a development environment, and run tests, see the [Development](./development/contributing.md) section.