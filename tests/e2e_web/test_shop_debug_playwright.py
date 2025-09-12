from __future__ import annotations

from playwright.sync_api import Page, expect


def _wait_sw_ready(page: Page) -> None:
    page.wait_for_function(
        "async () => { try { const r = await fetch('/api/products'); return r.ok; } catch { return false } }",
        timeout=7000,
    )


def test_shop_debug_force401_toggle(http_server: str, page: Page) -> None:
    # Open index to ensure SW registration
    page.goto(f"{http_server}/shop_multipage/index.html")
    _wait_sw_ready(page)

    # Enable force401 via SW debug API
    page.evaluate(
        "async () => { await fetch('/api/__debug', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ force401: true }) }); }"
    )

    # Access cart -> should redirect to login
    page.goto(f"{http_server}/shop_multipage/cart.html")
    page.wait_for_url("**/login.html")
    expect(page.get_by_test_id("login-form")).to_be_visible()

    # Disable force401 and access cart again -> should succeed
    page.goto(f"{http_server}/shop_multipage/index.html")
    _wait_sw_ready(page)
    page.evaluate(
        "async () => { await fetch('/api/__debug', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ force401: false }) }); }"
    )

    # Need to login to get a token
    page.goto(f"{http_server}/shop_multipage/login.html")
    page.get_by_test_id("login-email").fill("e2e@example.com")
    page.get_by_test_id("login-password").fill("password")
    page.get_by_test_id("login-submit").click()
    page.wait_for_url("**/index.html")

    # Now go to cart; page should load and show '合計:' text
    page.goto(f"{http_server}/shop_multipage/cart.html")
    expect(page.get_by_test_id("cart")).to_contain_text("合計:")

