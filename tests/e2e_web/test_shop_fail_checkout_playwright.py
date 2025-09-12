from __future__ import annotations

from playwright.sync_api import Page


def _wait_sw_ready(page: Page) -> None:
    page.wait_for_function(
        "async () => { try { const r = await fetch('/api/products'); return r.ok; } catch { return false } }",
        timeout=7000,
    )


def test_shop_checkout_fails_with_failcart(http_server: str, page: Page) -> None:
    # Login and add an item first (while failCart is disabled)
    page.goto(f"{http_server}/shop_multipage/login.html")
    page.get_by_test_id("login-email").fill("e2e@example.com")
    page.get_by_test_id("login-password").fill("password")
    page.get_by_test_id("login-submit").click()
    page.wait_for_url("**/index.html")
    _wait_sw_ready(page)
    page.locator("[data-testid^=add-]").first.click()

    # Enable failCart (also affects checkout)
    page.evaluate(
        "async () => { await fetch('/api/__debug', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ failCart: true }) }); }"
    )

    # Proceed to checkout and expect /api/checkout to return 500
    page.goto(f"{http_server}/shop_multipage/checkout.html")
    page.get_by_test_id("checkout-name").fill("田中 太郎")
    page.get_by_test_id("checkout-address").fill("東京都千代田区1-2-3")

    with page.expect_response(lambda r: "/api/checkout" in r.url and r.request.method == "POST") as resp_info:
        page.get_by_test_id("checkout-submit").click()
    resp = resp_info.value
    assert resp.status == 500

