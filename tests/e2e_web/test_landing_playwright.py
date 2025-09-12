from __future__ import annotations

from playwright.sync_api import Page, expect


def test_landing_basic_flow(http_server: str, page: Page) -> None:
    base = f"{http_server}/landing_static/index.html"
    page.goto(base)

    # Mobile menu toggle aria-expanded change
    toggle = page.get_by_test_id("nav-toggle")
    toggle.click()
    expect(toggle).to_have_attribute("aria-expanded", "true")
    toggle.click()
    expect(toggle).to_have_attribute("aria-expanded", "false")

    # Carousel next/prev
    page.get_by_test_id("carousel-next").click()
    page.get_by_test_id("carousel-prev").click()

    # Invalid contact submit
    page.get_by_test_id("contact-name").fill("")
    page.get_by_test_id("contact-email").fill("not-an-email")
    page.get_by_test_id("contact-message").fill("")
    page.get_by_test_id("contact-submit").click()
    expect(page.locator("#contact-result")).to_contain_text("ご確認")

    # Valid contact submit
    page.get_by_test_id("contact-name").fill("田中 太郎")
    page.get_by_test_id("contact-email").fill("taro@example.com")
    page.get_by_test_id("contact-message").fill("資料のご相談です")
    page.get_by_test_id("contact-submit").click()
    expect(page.locator("#contact-result")).to_contain_text("送信が完了")

