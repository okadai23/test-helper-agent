from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect


@pytest.mark.parametrize(
    "size",
    [
        (390, 844),   # mobile
        (1024, 768),  # tablet
        (1440, 900),  # desktop
    ],
)
def test_landing_responsive(http_server: str, page: Page, size: tuple[int, int]) -> None:
    page.set_viewport_size({"width": size[0], "height": size[1]})
    page.goto(f"{http_server}/landing_static/index.html")

    if size[0] <= 720:
        # Mobile: menu is hidden until toggled
        expect(page.locator("#nav-list")).to_be_hidden()
        page.get_by_test_id("nav-toggle").click()
        expect(page.locator("#nav-list")).to_be_visible()
    else:
        # Desktop: menu visible, toggle not visible
        expect(page.locator("#nav-list")).to_be_visible()


@pytest.mark.parametrize(
    "size",
    [
        (390, 844),
        (1024, 768),
        (1440, 900),
    ],
)
def test_spa_responsive(http_server: str, page: Page, size: tuple[int, int]) -> None:
    page.set_viewport_size({"width": size[0], "height": size[1]})
    page.goto(f"{http_server}/spa_tasks/index.html?fixture=few&route=%23/all")
    expect(page.get_by_test_id("task-form")).to_be_visible()
    expect(page.get_by_test_id("task-list")).to_be_visible()


@pytest.mark.parametrize(
    "size",
    [
        (390, 844),
        (1024, 768),
        (1440, 900),
    ],
)
def test_shop_responsive(http_server: str, page: Page, size: tuple[int, int]) -> None:
    page.set_viewport_size({"width": size[0], "height": size[1]})
    page.goto(f"{http_server}/shop_multipage/index.html")
    # Header and product list are visible
    expect(page.locator(".shop-header")).to_be_visible()
    expect(page.get_by_test_id("product-list")).to_be_visible()

