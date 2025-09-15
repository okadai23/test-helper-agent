# Agent Browser E2E Tests

This directory contains end-to-end tests that use OpenAI Agent API with browser automation tools to test web applications.

## Purpose

These tests demonstrate and validate:
- Agent-driven browser automation using real OpenAI API
- Playwright integration with Agent tools
- Real-world web application testing scenarios

## Test Coverage

- **Landing Page Tests** (`test_landing_*.py`): Navigation, forms, responsive design
- **Shop Tests** (`test_shop_*.py`): E-commerce workflows including login, cart, checkout
- **SPA Tests** (`test_spa_*.py`): Single-page application interactions
- **Responsive Tests** (`test_responsive_*.py`): Multi-device viewport testing

## Requirements

1. **OpenAI API Key**: Set the `OPENAI_API_KEY` environment variable
2. **Agent Dependencies**: Install with `uv add --dev openai-agents`
3. **Playwright**: Already included in project dependencies

## Running Tests

### Run all tests (including agent browser tests if API key is set):
```bash
pytest tests/e2e_web/
```

### Skip agent browser tests:
```bash
pytest -m "not agent_browser"
```

### Run only agent browser tests (requires API key):
```bash
export OPENAI_API_KEY="your-api-key"
pytest -m agent_browser
```

### Run specific test file:
```bash
export OPENAI_API_KEY="your-api-key"
pytest tests/e2e_web/test_shop_playwright.py
```

## Environment Variables

- `OPENAI_API_KEY`: Required for running agent browser tests
- `OPENAI_MODEL`: Optional, defaults to "gpt-4o-mini"
- `E2E_HEADED`: Set to "1" to run browser in headed mode
- `E2E_SLOWMO`: Milliseconds to slow down browser actions
- `E2E_VIDEO`: Set to "1" to record videos
- `E2E_TRACE`: Set to "1" to enable Playwright tracing

## Skip Behavior

Tests are automatically skipped when:
- `OPENAI_API_KEY` is not set
- Running with `pytest -m "not agent_browser"`

## Integration with CI/CD

For CI/CD pipelines, these tests are marked with `agent_browser` and will be skipped by default unless explicitly configured with API credentials.

```yaml
# Example GitHub Actions configuration
- name: Run tests without agent browser
  run: pytest -m "not agent_browser"

- name: Run agent browser tests
  if: secrets.OPENAI_API_KEY != ''
  env:
    OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
  run: pytest -m agent_browser
```

## Test Architecture

Each test uses:
1. **Playwright** for browser automation
2. **Agent API** for intelligent test scenario execution
3. **MCP Browser Tools** for advanced browser interactions
4. **Local HTTP server** serving test sites from `test_sites/` directory

## Debugging

Enable debug output:
```bash
export PYTEST_DEBUG=1
export E2E_HEADED=1
export E2E_SLOWMO=1000
pytest tests/e2e_web/ -v -s
```