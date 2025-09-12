Playwright E2E Template (Python)

This directory contains Playwright-based E2E smoke tests targeting the sample apps in `test_sites/`.

Install (with uv):

- uv add --dev playwright pytest pytest-asyncio
- uv run python -m playwright install chromium

Run:

- uv run pytest -q tests/e2e_web

Notes:

- Tests spin up a local `http.server` from `test_sites/` on a free port.
- Service Worker in `shop_multipage` requires localhost; the server binds to 127.0.0.1 which qualifies.
- If browsers are not installed, run the install command above.

