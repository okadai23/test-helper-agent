from __future__ import annotations

import contextlib
import http.client
import os
import socket
import subprocess
import sys
import time
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pytest
from playwright.sync_api import Browser, Page, Playwright, sync_playwright

if TYPE_CHECKING:
    from collections.abc import Iterator

# Mark all tests in this directory as requiring agent_browser
pytestmark = pytest.mark.agent_browser  # Custom mark


def pytest_collection_modifyitems(
    config: Any,  # noqa: ARG001 - Pytest Config type not exported
    items: list[Any],  # Pytest Item type not exported
) -> None:
    """Skip agent_browser tests if OPENAI_API_KEY is not set."""
    skip_agent = pytest.mark.skip(
        reason="OPENAI_API_KEY not set - skipping agent browser tests",
    )

    if not os.environ.get("OPENAI_API_KEY"):
        for item in items:
            if item.get_closest_marker("agent_browser"):
                item.add_marker(skip_agent)


@pytest.fixture(scope="session", autouse=True)
def check_agent_requirements() -> None:
    """Check requirements for agent browser tests."""
    import sys

    if os.environ.get("OPENAI_API_KEY"):
        # Log that we're running with real API
        sys.stdout.write("\n✓ Running agent browser tests with OPENAI_API_KEY\n")
    else:
        sys.stdout.write("\n⚠ Skipping agent browser tests (OPENAI_API_KEY not set)\n")


@pytest.fixture(scope="session")
def agent_browser_client() -> Any | None:
    """Create Agent browser client for automated testing."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return None

    try:
        from agents import Agent

        from test_helper.services.browser_use_mcp_client import BrowserUseMCPClient

        # Initialize Agent with browser tools
        agent = Agent(
            name="BrowserTestAgent",
            instructions="You are a browser automation agent for testing web applications.",
            model=os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
        )

        # Initialize browser MCP client
        browser_client = BrowserUseMCPClient()
    except ImportError:
        import sys

        sys.stdout.write("⚠ Agent dependencies not installed\n")
        return None
    else:
        return {"agent": agent, "browser": browser_client}


def _find_free_port() -> int:
    with contextlib.closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(("127.0.0.1", 0))
        return int(s.getsockname()[1])


@pytest.fixture(scope="session")
def test_sites_root() -> Path:
    """Return the path to the test_sites directory."""
    return Path(__file__).resolve().parents[2] / "test_sites"


@pytest.fixture(scope="session")
def http_server(test_sites_root: Path) -> Iterator[str]:
    """Serve test_sites on a random free port; yield base_url."""
    port = _find_free_port()
    env = os.environ.copy()
    cmd = [sys.executable, "-m", "http.server", str(port), "--bind", "127.0.0.1"]
    proc = subprocess.Popen(cmd, cwd=str(test_sites_root), env=env)  # noqa: S603

    base_url = f"http://127.0.0.1:{port}"
    # Wait until server is ready
    deadline = time.time() + 10
    while time.time() < deadline:
        try:
            conn = http.client.HTTPConnection("127.0.0.1", port, timeout=0.5)
            conn.request("GET", "/")
            _ = conn.getresponse()
            conn.close()
            break
        except (
            OSError,
            TimeoutError,
            ConnectionRefusedError,
            http.client.HTTPException,
        ):
            time.sleep(0.1)

    try:
        yield base_url
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            proc.kill()


@pytest.fixture(scope="session")
def playwright_context() -> Iterator[tuple[Playwright, Browser]]:
    """Provide a Playwright instance and browser for the test session."""
    headful = os.getenv("E2E_HEADED", "0").lower() in {"1", "true", "yes"}
    slow_mo = 0
    try:
        slow_mo = int(os.getenv("E2E_SLOWMO", "0") or "0")
    except ValueError:
        slow_mo = 0

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=not headful, slow_mo=slow_mo)
        try:
            yield p, browser
        finally:
            browser.close()


@pytest.fixture
def page(
    playwright_context: tuple[Playwright, Browser],
    request: Any,  # Pytest FixtureRequest type not exported
) -> Iterator[Page]:
    """Create a new browser page for each test."""
    _, browser = playwright_context

    # Artifacts configuration via env
    artifacts_root = Path.cwd() / "artifacts" / "playwright"
    artifacts_root.mkdir(parents=True, exist_ok=True)
    record_video = os.getenv("E2E_VIDEO", "0").lower() in {"1", "true", "yes"}
    enable_trace = os.getenv("E2E_TRACE", "0").lower() in {"1", "true", "yes"}

    context_kwargs: dict[str, Any] = {}
    if record_video:
        videos_dir = artifacts_root / "videos"
        videos_dir.mkdir(parents=True, exist_ok=True)
        context_kwargs["record_video_dir"] = str(videos_dir)

    context = browser.new_context(**context_kwargs)
    if enable_trace:
        context.tracing.start(screenshots=True, snapshots=True, sources=True)

    page = context.new_page()
    try:
        yield page
    finally:
        if enable_trace:
            traces_dir = artifacts_root / "traces"
            traces_dir.mkdir(parents=True, exist_ok=True)
            out = traces_dir / f"{request.node.name}.zip"
            context.tracing.stop(path=str(out))
        context.close()
