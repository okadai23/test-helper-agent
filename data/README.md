# E2E Test Automation Data Directory

This directory contains runtime data for the E2E Test Automation AI Agent system.

## Directory Structure

- `projects/`: Test project data and metadata
  - `{project_id}/`: Individual project directories
    - `metadata.json`: Project configuration and statistics
    - `tests/`: Generated test files
    - `cache/`: Cached selectors and patterns
    - `history/`: Test execution history
- `cache/`: Global cache for common patterns and configurations

## Data Retention

- Test history is retained for 30 days by default
- Maximum 100 test files per project
- Cache is automatically cleaned based on usage patterns

## File Formats

- All metadata files use JSON format with UTF-8 encoding
- Test files are saved as Playwright TypeScript/JavaScript
- Screenshots and videos are stored as binary files with relative paths