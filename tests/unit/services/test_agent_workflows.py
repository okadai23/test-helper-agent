from __future__ import annotations

import asyncio
from typing import Any

import pytest

from test_helper.utils.settings import E2ESettings, reset_e2e_settings
from test_helper.services.agent_workflows import _validate_url_for_fetch


def test_validate_url_for_fetch_allows_http_https() -> None:
    assert _validate_url_for_fetch("http://example.com") == "http://example.com"
    assert _validate_url_for_fetch("https://example.com") == "https://example.com"


@pytest.mark.parametrize(
    "url",
    ["", "   ", "ftp://example.com", "file:///etc/passwd", "http:///path"],
)
def test_validate_url_for_fetch_rejects_invalid(url: str) -> None:
    with pytest.raises(ValueError):
        _validate_url_for_fetch(url)


def test_agent_fetch_max_chars_setting_bounds() -> None:
    # Ensure settings field is present and bounded
    s = E2ESettings(agent_fetch_max_chars=5000)
    assert 1000 <= s.agent_fetch_max_chars <= 200000

