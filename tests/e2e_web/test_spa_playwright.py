from __future__ import annotations

from playwright.sync_api import Page, expect


def test_spa_tasks_smoke(http_server: str, page: Page) -> None:
    base = f"{http_server}/spa_tasks/index.html?fixture=empty&route=%23/all"
    page.goto(base)

    # Add
    page.get_by_test_id("task-title").fill("E2E最初のタスク")
    page.get_by_test_id("task-add").click()
    expect(page.get_by_test_id("task-list")).to_contain_text("E2E最初のタスク")

    # Toggle done
    page.locator(".task-list input[type=checkbox]").first.click()

    # Switch to completed
    page.get_by_test_id("tab-completed").click()
    expect(page.get_by_test_id("task-list")).to_contain_text("E2E最初のタスク")

    # Persist after reload
    page.reload()
    expect(page.get_by_test_id("task-list")).to_contain_text("E2E最初のタスク")

    # Search and delete via dialog
    page.get_by_test_id("task-search").fill("E2E")
    page.locator(".actions [data-testid^=task-delete-]").first.click()
    # Confirm dialog
    # In the app, dialog is native <dialog>; emulate confirmation by pressing Enter
    page.keyboard.press("Enter")
    expect(page.get_by_test_id("task-list")).not_to_contain_text("E2E最初のタスク")

