from __future__ import annotations

from playwright.sync_api import Page, expect


def test_landing_anchor_navigation(http_server: str, page: Page) -> None:
    page.goto(f"{http_server}/landing_static/index.html")
    # Click CTA to contact section
    page.get_by_test_id("hero-cta").click()
    expect(page).to_have_url(lambda url: url.endswith("#contact"))

    # Navigate via header link to pricing
    page.get_by_test_id("nav-pricing").click()
    expect(page).to_have_url(lambda url: url.endswith("#pricing"))
