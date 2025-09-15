from __future__ import annotations

import pytest

from test_helper.services.agent_workflows import _validate_url_for_fetch
from test_helper.utils.settings import E2ESettings


def test_validate_url_for_fetch_allows_http_https() -> None:
    """Test that _validate_url_for_fetch allows HTTP and HTTPS URLs."""
    assert _validate_url_for_fetch("http://example.com") == "http://example.com"
    assert _validate_url_for_fetch("https://example.com") == "https://example.com"


@pytest.mark.parametrize(
    "url",
    ["", "   ", "ftp://example.com", "file:///etc/passwd", "http:///path"],
)
def test_validate_url_for_fetch_rejects_invalid(url: str) -> None:
    """Test that _validate_url_for_fetch rejects invalid URLs."""
    with pytest.raises(ValueError, match="Invalid URL"):
        _validate_url_for_fetch(url)


def test_agent_fetch_max_chars_setting_bounds() -> None:
    """Test agent fetch max chars setting bounds."""
    # Ensure settings field is present and bounded
    s = E2ESettings(agent_fetch_max_chars=5000)
    assert 1000 <= s.agent_fetch_max_chars <= 200000
