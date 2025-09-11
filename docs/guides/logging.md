# Logging Guide

The Test Helper Agent provides comprehensive logging capabilities with structured logging and multiple output formats.

## Overview

The logging system is built on **structlog** to ensure all log messages are structured and enriched with context.

## Basic Configuration

Configure logging using environment variables in your `.env` file:

```ini
# Set log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL=INFO

# Set log format (json or console)
LOG_FORMAT=json

# Optional: Log to a file
LOG_FILE_PATH=/path/to/agent.log
```

## Structured Logging

All components use structured logging, which automatically includes context about the component generating the log.

```python
from test_helper.base import BaseComponent

class MyService(BaseComponent):
    def process(self, item_id: str) -> None:
        # This log will automatically include component context
        self.logger.info("processing_item", item_id=item_id)
```

## Log Formats

### JSON Format (Default)

Best for production environments and log aggregation tools (e.g., ELK Stack, Datadog).

```json
{
    "timestamp": "2025-09-12T12:00:00.123Z",
    "level": "info",
    "logger": "test_helper.services.generator",
    "message": "Generating test file",
    "project_name": "my-app",
    "source_capture_id": "capture-123"
}
```

### Console Format

Human-readable format, ideal for local development.

```
2025-09-12 12:00:00 [info     ] Generating test file               project_name=my-app source_capture_id=capture-123
```

## Best Practices

1.  **Use Structured Arguments**: Pass data as keyword arguments to the logger, not as part of the message string.
    ```python
    # Good
    logger.info("File generated", path=file_path)

    # Bad
    logger.info(f"File generated at {file_path}")
    ```

2.  **Log at Appropriate Levels**: Use `DEBUG` for detailed diagnostics, `INFO` for general workflow events, `WARNING` for recoverable issues, and `ERROR` for failures.

3.  **Avoid Logging Sensitive Data**: Never log secrets like API keys. The application configuration is designed to prevent this, but be mindful in custom code.