from __future__ import annotations

from playwright.sync_api import Page, expect


def test_shop_login_add_cart_checkout(http_server: str, page: Page) -> None:
    # Login
    page.goto(f"{http_server}/shop_multipage/login.html")
    page.get_by_test_id("login-email").fill("e2e@example.com")
    page.get_by_test_id("login-password").fill("password")
    page.get_by_test_id("login-submit").click()

    # After login, index shown and SW should be active; add to cart
    page.wait_for_url("**/index.html", timeout=5000)
    # Ensure Service Worker is active (API becomes available)
    page.wait_for_function(
        "async () => { try { const r = await fetch('/api/products'); return r.ok; } catch { return false } }",
        timeout=7000,
    )
    # First card add button
    page.locator("[data-testid^=add-]").first.click()

    # Cart count updates
    expect(page.locator("#cart-count")).not_to_have_text("0")

    # Go to cart
    page.get_by_test_id("nav-cart").click()
    page.wait_for_url("**/cart.html")
    expect(page.get_by_test_id("cart")).to_contain_text("合計:")

    # Remove first item
    page.locator("[data-testid^=remove-]").first.click()

    # Go checkout
    page.get_by_test_id("go-checkout").click()
    page.wait_for_url("**/checkout.html")
    page.get_by_test_id("checkout-name").fill("田中 太郎")
    page.get_by_test_id("checkout-address").fill("東京都千代田区1-2-3")
    page.get_by_test_id("checkout-submit").click()
    expect(page.locator("#checkout-result")).to_contain_text("注文が確定")


def test_shop_unauthorized_redirect(http_server: str, page: Page) -> None:
    # Ensure no token
    page.context.add_init_script("localStorage.removeItem('shop_token')")
    # Access cart directly -> should redirect to login due to 401 from SW
    page.goto(f"{http_server}/shop_multipage/cart.html")
    # Depending on timing, first call may render then redirect; await login load
    page.wait_for_url("**/login.html")
