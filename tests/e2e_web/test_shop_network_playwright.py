from __future__ import annotations

import time

from playwright.sync_api import Page, expect


def _wait_sw_ready(page: Page) -> None:
    page.wait_for_function(
        "async () => { try { const r = await fetch('/api/products'); return r.ok; } catch { return false } }",
        timeout=7000,
    )


def test_shop_failcart_returns_500(http_server: str, page: Page) -> None:
    # Ensure SW registered and set failCart
    page.goto(f"{http_server}/shop_multipage/index.html")
    _wait_sw_ready(page)
    page.evaluate(
        "async () => { await fetch('/api/__debug', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ failCart: true, force401: false }) }); }"
    )

    # Login to obtain token (cart endpoints require auth)
    page.goto(f"{http_server}/shop_multipage/login.html")
    page.get_by_test_id("login-email").fill("e2e@example.com")
    page.get_by_test_id("login-password").fill("password")
    page.get_by_test_id("login-submit").click()
    page.wait_for_url("**/index.html")

    # Go cart and expect /api/cart to return 500
    page.goto(f"{http_server}/shop_multipage/cart.html")
    resp = page.wait_for_response(lambda r: "/api/cart" in r.url and r.request.method == "GET")
    assert resp.status == 500


def test_shop_api_delay_increases_latency(http_server: str, page: Page) -> None:
    # Register SW then configure extra delay
    page.goto(f"{http_server}/shop_multipage/index.html")
    _wait_sw_ready(page)
    page.evaluate(
        "async () => { await fetch('/api/__debug', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ delay: 1000 }) }); }"
    )

    # Reload and measure time for /api/products
    start = time.monotonic()
    page.reload()
    resp = page.wait_for_response(lambda r: "/api/products" in r.url and r.request.method == "GET")
    elapsed_ms = (time.monotonic() - start) * 1000
    # Expect at least ~900ms considering processing variance
    assert resp.ok
    assert elapsed_ms >= 900


def test_shop_product_not_found(http_server: str, page: Page) -> None:
    page.goto(f"{http_server}/shop_multipage/product.html?id=9999")
    expect(page.get_by_test_id("product-detail")).to_contain_text("商品が見つかりません")

