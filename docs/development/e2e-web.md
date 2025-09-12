## E2E Web Tests (Playwright)

This document explains how to run the Playwright-based E2E smoke tests that validate the sample web apps under `test_sites/`.

### Overview

- Targets three self-contained apps:
  - `landing_static/` — static corporate landing page
  - `spa_tasks/` — simple SPA task manager (localStorage)
  - `shop_multipage/` — multi-page shop with token session and a mock API via Service Worker
- Tests automatically start a local HTTP server on a random port and run against it.

### Prerequisites

- Python 3.13+
- Dependencies managed via `uv`

Install dev dependencies and browser binaries:

```bash
uv add --dev playwright pytest pytest-asyncio
uv run python -m playwright install chromium
```

### Running Tests

Run the full E2E suite:

```bash
uv run pytest -q tests/e2e_web
```

Or via nox:

```bash
nox -s e2e_web
nox -s e2e_web_headed      # Headed mode + slow motion
nox -s e2e_web_shop_debug  # ShopのSWデバッグAPIを使った異常系テスト
nox -s e2e_web_trace       # Playwright tracing (artifacts/playwright/traces)
nox -s e2e_web_video       # Video recording (artifacts/playwright/videos)
```

Run a specific test file/case:

```bash
uv run pytest -q tests/e2e_web/test_shop_playwright.py::test_shop_login_add_cart_checkout
```

Run headed mode (for debugging):

```bash
PWDEBUG=1 uv run pytest tests/e2e_web/test_spa_playwright.py
```

### What the Tests Do

- Landing: toggles mobile navigation, cycles the testimonial carousel, and validates contact form behavior for invalid/valid input.
- SPA Tasks: adds/edits/completes/deletes tasks, checks filtering via hash routes, and verifies persistence across reloads.
- Shop: logs in, adds products to cart, verifies cart count, removes items, and completes checkout. Also verifies 401 redirect when unauthenticated.

### Test Server Behavior

- The test fixture serves `test_sites/` using Python's built-in `http.server` bound to `127.0.0.1`.
- Service Worker (Shop) requires a secure context; localhost qualifies.
- The server is started before tests and torn down afterward.

### Using Built-in Test Harness Pages

For manual verification or to assist custom E2E scripts:

- Landing harness: `/landing_static/test_cases.html`
- SPA harness: `/spa_tasks/test_cases.html`
  - Fixture query params: `fixture=empty|few|many`, `corrupt=1`, `route=#/all|#/active|#/completed`
- Shop harness: `/shop_multipage/test_cases.html`
  - Debug API: `POST /api/__debug { force401, failCart, delay }`

### Tips for Stability

- Prefer `get_by_test_id` selectors; the apps expose stable `data-testid` attributes.
- Avoid fixed sleeps; rely on `expect(...).to_*` or `wait_for_*` utilities.
- When testing the shop, wait for the Service Worker/API to become available after login (see example in tests).

### Tracing and Video Artifacts

- Enable tracing via nox session `e2e_web_trace` or set env `E2E_TRACE=1`.
  - Artifacts are exported per test under `artifacts/playwright/traces/*.zip`.
- Enable video via nox session `e2e_web_video` or set env `E2E_VIDEO=1`.
  - Videos are stored under `artifacts/playwright/videos/`.

### CI Integration (GitHub Actions)

- Workflow: `.github/workflows/e2e-web.yml`
  - Steps:
    - Install uv and project dependencies
    - Install Playwright Chromium
    - Run `nox -s e2e_web_trace`
    - Upload `artifacts/playwright/traces` as `playwright-traces`
    - If tests failed, run `nox -s e2e_web_video_shop` to capture videos for Shop tests
    - Upload `artifacts/playwright/videos` as `playwright-videos`
  - You can narrow test targets via `nox -s e2e_web_trace -- tests/e2e_web/test_spa_playwright.py::test_spa_tasks_smoke` in local runs.

### Cleaning State

- SPA state persists in `localStorage` under key `mini_tasks_v1`.
- Shop token persists as `localStorage['shop_token']`; cart state is held in-memory in the Service Worker session per token.
- Each test creates a new browser context to avoid cross-test contamination; additional clearing is not usually required.

### Troubleshooting

- If browsers are missing: rerun `uv run python -m playwright install chromium`.
- If SW does not intercept: ensure you are hitting `127.0.0.1` and not `localhost` with a different port; the fixture binds to `127.0.0.1` and tests use that base URL.
- Port conflicts are avoided by using a random free port; if you need a fixed port for tooling, run `scripts/serve-test-sites.sh` and point your runner to that.
