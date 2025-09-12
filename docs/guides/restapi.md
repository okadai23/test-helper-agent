# REST API Interface Guide

The REST API interface provides HTTP endpoints for interacting with the Test Helper Agent programmatically.

## Overview

The REST API is built using FastAPI and is designed for integration with other systems, such as CI/CD pipelines or custom dashboards.

## Running the REST API

To run the application with the REST API interface, you need to set the `INTERFACE_TYPE` environment variable.

```bash
# Set the interface type to use the REST API
export INTERFACE_TYPE=restapi

# Run the application using a web server like Uvicorn
uv run uvicorn test_helper.app:create_app --factory --reload
```

The API will be available at `http://localhost:8000` by default.

## API Documentation

FastAPI automatically generates interactive API documentation.

-   **Swagger UI**: `http://localhost:8000/docs`
-   **ReDoc**: `http://localhost:8000/redoc`

## Available Endpoints

Endpoints are organized by project.

### Health Check

-   **GET `/health`**: Returns the health status of the application.

    ```bash
    curl http://localhost:8000/health
    ```

### Projects

-   **POST `/api/v1/projects`**: Create a new project workspace.
-   **GET `/api/v1/projects`**: List all existing projects.

### Capture & Generation

-   **POST `/api/v1/projects/{project_name}/capture`**: Start a new capture session.
-   **POST `/api/v1/projects/{project_name}/generate`**: Generate a test from a capture.

## Authentication

Currently, the REST API does not implement authentication. It is expected to be run in a trusted environment. For production use, it should be placed behind a reverse proxy that can handle authentication and TLS termination.
