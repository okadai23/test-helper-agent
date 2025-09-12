from __future__ import annotations

import contextlib
import http.client
import os
import socket
import subprocess
import sys
import time
from collections.abc import Iterator
from pathlib import Path

import pytest
from playwright.sync_api import Browser, Page, Playwright, sync_playwright


def _find_free_port() -> int:
    with contextlib.closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(("127.0.0.1", 0))
        return int(s.getsockname()[1])


@pytest.fixture(scope="session")
def test_sites_root() -> Path:
    return Path(__file__).resolve().parents[2] / "test_sites"


@pytest.fixture(scope="session")
def http_server(test_sites_root: Path) -> Iterator[str]:
    """Serve test_sites on a random free port; yield base_url."""
    port = _find_free_port()
    env = os.environ.copy()
    cmd = [sys.executable, "-m", "http.server", str(port), "--bind", "127.0.0.1"]
    proc = subprocess.Popen(cmd, cwd=str(test_sites_root), env=env)

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
    request: pytest.FixtureRequest,
) -> Iterator[Page]:
    _, browser = playwright_context

    # Artifacts configuration via env
    artifacts_root = Path.cwd() / "artifacts" / "playwright"
    artifacts_root.mkdir(parents=True, exist_ok=True)
    record_video = os.getenv("E2E_VIDEO", "0").lower() in {"1", "true", "yes"}
    enable_trace = os.getenv("E2E_TRACE", "0").lower() in {"1", "true", "yes"}

    context_kwargs: dict[str, object] = {}
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
