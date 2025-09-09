# Quick Start Guide: E2E Test Automation AI Agent

## Prerequisites

-   Python 3.13+
-   Docker and Docker Compose
-   Chrome or Chromium browser
-   4GB RAM minimum

## Installation

### 1. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/daisuke19891023/test-helper e2e-agent.git
cd test-helper e2e-agent

# Create virtual environment with uv
uv python install 3.13  # Install Python 3.13 if needed
uv sync --all-extras     # Install all dependencies including dev

# Activate virtual environment (optional, uv handles this automatically)
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 2. Start Required Services

```bash
# Start Temporal server and Playwright MCP
docker-compose up -d

# Verify services are running
docker-compose ps
# Should show:
# - temporal-server (port 7233)
# - temporal-ui (port 8080)
# - playwright-mcp (port 9000)
```

### 3. Initialize Configuration

```bash
# Run setup script
python scripts/setup.py

# This will:
# - Create data directories
# - Generate default config
# - Verify connectivity to services
# - Create your first project
```

## Basic Usage

### Create Your First Test Project

```bash
# Create a project for your web application
test-helper e2e project create \
  --name "My Web App" \
  --url "http://localhost:3000" \
  --browser chromium

# Output:
# ✓ Project created: 123e4567-e89b-12d3-a456-426614174000
# ✓ Storage initialized at: data/projects/123e4567-e89b-12d3-a456-426614174000
```

### Capture User Interactions

```bash
# Start capture session (opens browser)
test-helper e2e capture start \
  --project 123e4567-e89b-12d3-a456-426614174000 \
  --headed  # Shows browser window

# Perform your interactions in the browser:
# 1. Navigate to pages
# 2. Fill forms
# 3. Click buttons
# 4. Complete user flows

# Stop capture when done
test-helper e2e capture stop

# Output:
# ✓ Captured 15 interactions
# ✓ Session saved: 987f6543-a21b-34c5-d678-912345678900
```

### Generate Tests from Capture

```bash
# Generate Playwright tests
test-helper e2e generate \
  --project 123e4567-e89b-12d3-a456-426614174000 \
  --session 987f6543-a21b-34c5-d678-912345678900 \
  --name "User login flow"

# Output:
# ✓ Generated test: test_user_login_flow.spec.ts
# ✓ Location: data/projects/123e4567-e89b-12d3-a456-426614174000/tests/
# ✓ Steps: 8, Assertions: 3
```

### Execute Generated Tests

```bash
# Run tests
test-helper e2e execute \
  --project 123e4567-e89b-12d3-a456-426614174000 \
  --all  # Run all tests in project

# Output:
# Running tests...
# ✓ test_user_login_flow.spec.ts (3.2s)
#
# Results: 1 passed, 0 failed
# Reports saved to: data/projects/123e4567-e89b-12d3-a456-426614174000/reports/
```

### Fix Failing Tests (After App Changes)

```bash
# When tests fail after application changes
test-helper e2e execute --project 123e4567-e89b-12d3-a456-426614174000

# Output:
# ✗ test_user_login_flow.spec.ts
#   Error: Element not found: #login-button
#   Failed at step 3

# Analyze and fix automatically
test-helper e2e fix \
  --project 123e4567-e89b-12d3-a456-426614174000 \
  --auto-apply  # Automatically apply high-confidence fixes

# Output:
# Analyzing failure...
# ✓ Root cause: Selector changed from #login-button to button[data-testid="login"]
# ✓ Confidence: 0.92
# ✓ Fix applied automatically
# ✓ Re-running test... PASSED
```

## Complete Example Workflow

### Scenario: Testing an E-commerce Application

```bash
# 1. Create project
test-helper e2e project create \
  --name "E-commerce Store" \
  --url "https://shop.example.com" \
  --browser chromium

# 2. Start capture
test-helper e2e capture start --project $PROJECT_ID --headed

# 3. Record shopping workflow:
#    - Browse products
#    - Add to cart
#    - Checkout process
#    - Payment (test mode)

# 4. Stop capture
test-helper e2e capture stop

# 5. Generate comprehensive test suite
test-helper e2e generate \
  --project $PROJECT_ID \
  --session $SESSION_ID \
  --split-scenarios  # Creates separate test for each flow

# 6. Review generated tests
ls data/projects/$PROJECT_ID/tests/
# Output:
# - test_browse_products.spec.ts
# - test_add_to_cart.spec.ts
# - test_checkout_process.spec.ts
# - test_payment_flow.spec.ts

# 7. Execute all tests
test-helper e2e execute --project $PROJECT_ID --all --parallel

# 8. Schedule regular test runs
test-helper e2e schedule \
  --project $PROJECT_ID \
  --cron "0 */6 * * *"  # Every 6 hours
  --notify-on-failure email@example.com
```

## CLI Commands Reference

### Project Management

```bash
test-helper e2e project create --name NAME --url URL [--browser BROWSER]
test-helper e2e project list [--status active|archived|paused]
test-helper e2e project get PROJECT_ID
test-helper e2e project update PROJECT_ID [--name NAME] [--url URL]
test-helper e2e project delete PROJECT_ID
```

### Capture Sessions

```bash
test-helper e2e capture start --project PROJECT_ID [--headed] [--viewport WIDTHxHEIGHT]
test-helper e2e capture stop
test-helper e2e capture status
test-helper e2e capture list --project PROJECT_ID
```

### Test Generation

```bash
test-helper e2e generate --project PROJECT_ID --session SESSION_ID [--name NAME]
test-helper e2e generate --project PROJECT_ID --from-recording FILE
test-helper e2e generate --optimize PROJECT_ID TEST_ID  # Optimize existing test
```

### Test Execution

```bash
test-helper e2e execute --project PROJECT_ID [--test TEST_ID] [--all] [--parallel]
test-helper e2e execute --watch PROJECT_ID  # Run on file changes
test-helper e2e results PROJECT_ID EXECUTION_ID
```

### Test Fixes

```bash
test-helper e2e fix --project PROJECT_ID [--execution EXECUTION_ID] [--auto-apply]
test-helper e2e fix --review PROJECT_ID PROPOSAL_ID
test-helper e2e fix --apply PROJECT_ID PROPOSAL_ID
```

### Utilities

```bash
test-helper e2e config set KEY VALUE
test-helper e2e config get KEY
test-helper e2e doctor  # Check system health
test-helper e2e export --project PROJECT_ID --format playwright|cypress
```

## Configuration

### Project Configuration (metadata.json)

```json
{
    "project": {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "name": "My Web App",
        "url": "http://localhost:3000",
        "browser_config": {
            "browser": "chromium",
            "headless": true,
            "viewport": {
                "width": 1280,
                "height": 720
            }
        }
    },
    "settings": {
        "auto_fix_confidence_threshold": 0.8,
        "max_retries": 3,
        "timeout_ms": 30000,
        "parallel_execution": true
    }
}
```

### Global Configuration (~/.test-helper e2e/config.yaml)

```yaml
# API Configuration
api:
    host: localhost
    port: 8000

# Temporal Configuration
temporal:
    host: localhost
    port: 7233
    namespace: default

# Playwright MCP Configuration
playwright_mcp:
    host: localhost
    port: 9000

# Storage Configuration
storage:
    base_path: ./data
    retention_days: 30
    max_projects: 100

# AI Configuration
ai:
    model: gpt-4o-mini
    temperature: 0.3
    max_tokens: 2000
```

## Troubleshooting

### Common Issues

#### 1. Services Not Starting

```bash
# Check Docker status
docker-compose ps
docker-compose logs temporal-server
docker-compose logs playwright-mcp

# Restart services
docker-compose restart
```

#### 2. Test Generation Fails

```bash
# Check capture session has interactions
test-helper e2e capture list --project PROJECT_ID --detailed

# Verify AI service connectivity
test-helper e2e doctor --check-ai

# Increase verbosity for debugging
test-helper e2e generate --project PROJECT_ID --session SESSION_ID --verbose
```

#### 3. Tests Failing Unexpectedly

```bash
# Run with debugging enabled
test-helper e2e execute --project PROJECT_ID --debug --screenshot-on-failure

# Check for timing issues
test-helper e2e fix --project PROJECT_ID --analyze-timing

# Review execution logs
cat data/projects/PROJECT_ID/logs/execution_*.log
```

#### 4. High Memory Usage

```bash
# Clean up old data
test-helper e2e cleanup --older-than 30d

# Limit parallel execution
test-helper e2e config set max_parallel_tests 2

# Restart services
docker-compose restart
```

## Best Practices

1. **Use Stable Selectors**: Configure your app with `data-testid` attributes
2. **Start Simple**: Begin with basic flows before complex scenarios
3. **Regular Execution**: Schedule tests to run regularly to catch issues early
4. **Review Fix Proposals**: Always review auto-fixes before deploying
5. **Version Control Tests**: Commit generated tests to your repository
6. **Monitor Performance**: Track test execution times and optimize slow tests

## Next Steps

-   Read the full documentation: [docs/](../../docs/)
-   View example tests: [examples/](../../examples/)
-   Check the implementation plan: [plan.md](plan.md)
-   Report issues: [GitHub Issues](https://github.com/daisuke19891023/test-helper e2e-agent/issues)

## Support

-   Repository: https://github.com/daisuke19891023/test-helper e2e-agent
-   Documentation: [docs/](../../docs/)
-   Issues: https://github.com/daisuke19891023/test-helper e2e-agent/issues

---

_Version 1.0.0 - Last Updated: 2025-09-09_
