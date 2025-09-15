Test Sites for E2E Automation

This directory contains three sample web applications intended as targets for E2E test automation.
They are self-contained and require no backend services. The multi-page sample uses a Service Worker
to simulate an API and token-based session state.

Structure

- landing_static/ — A static corporate-style landing page (HTML/CSS/JS)
- spa_tasks/ — A simple SPA task manager using vanilla JS + localStorage
- shop_multipage/ — A multi-page shopping site with mock API and token session via Service Worker

How to Serve Locally

- Option A: Serve all samples from the repo root of `test_sites/`:
  - cd test_sites
  - python -m http.server 8000
  - Access:
    - http://localhost:8000/landing_static/
    - http://localhost:8000/spa_tasks/
    - http://localhost:8000/shop_multipage/

- Option B: Use the helper script:
  - bash scripts/serve-test-sites.sh

Notes for E2E Tests

- Prefer stable selectors: elements include data-testid attributes where appropriate.
- The SPA uses hash routes (#/all, #/active, #/completed) and persists tasks in localStorage.
- The multi-page shop registers a Service Worker on first load. Use http://localhost to satisfy
  secure context requirements for SW. The mock API exposes endpoints:
  - POST /api/login { email, password } -> { token }
  - GET /api/products -> [{ id, name, price }]
  - GET /api/cart -> { items: [...], total }
  - POST /api/cart { productId, qty } -> cart state
  - DELETE /api/cart/{productId} -> cart state
  - POST /api/checkout -> { ok: true, orderId }
  Include Authorization: Bearer <token> after login.

Test Case Harness Pages

- Landing: http://localhost:8000/landing_static/test_cases.html
  - Controls: nav toggle, anchor jumps, carousel prev/next, contact form valid/invalid submit
- SPA Tasks: http://localhost:8000/spa_tasks/test_cases.html
  - Fixtures via query: `fixture=empty|few|many`, `corrupt=1`, `route=#/all|#/active|#/completed`
  - Controls: add/toggle/delete/search/sort
- Shop (multi-page): http://localhost:8000/shop_multipage/test_cases.html
  - Controls: page jumps, login/logout, seed cart, clear cart
  - Debug API: POST /api/__debug { force401, failCart, delay }
    - force401: all protected endpoints return 401
    - failCart: cart-related endpoints return 500
    - delay: extra latency (ms) added to all API calls

Intended Scenarios

- Landing: navigate sections, open/close mobile menu, submit contact form (JS-only validation),
  run simple testimonials carousel.
- SPA Tasks: add/edit/delete/complete tasks, filter by status, persist across reloads.
- Shop: login, browse products, view product detail, add/remove cart items, checkout flow,
  validate token enforcement and cart count across pages.
