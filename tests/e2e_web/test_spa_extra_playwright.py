from __future__ import annotations

from playwright.sync_api import Page, expect


def test_spa_corrupt_storage_recovery(http_server: str, page: Page) -> None:
    # Load with corrupt localStorage; app should recover to empty list
    page.goto(f"{http_server}/spa_tasks/index.html?corrupt=1&route=%23/all")
    # List should be empty initially
    expect(page.get_by_test_id("task-list")).not_to_contain_text("タスク")
    # App should be usable after recovery
    page.get_by_test_id("task-title").fill("修復後タスク")
    page.get_by_test_id("task-add").click()
    expect(page.get_by_test_id("task-list")).to_contain_text("修復後タスク")


def test_spa_deeplink_completed_filter(http_server: str, page: Page) -> None:
    # Open directly on completed filter with a pre-seeded fixture
    page.goto(f"{http_server}/spa_tasks/index.html?fixture=few&route=%23/completed")
    # In fixtures, "レビュー" is done, "資料ドラフト作成" is not done
    expect(page.get_by_test_id("task-list")).to_contain_text("レビュー")
    expect(page.get_by_test_id("task-list")).not_to_contain_text("資料ドラフト作成")

