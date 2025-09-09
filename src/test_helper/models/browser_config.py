"""Browser configuration models."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class ViewportSize(BaseModel):
    """Browser viewport dimensions."""

    width: int = Field(default=1280, ge=320, le=3840)
    height: int = Field(default=720, ge=240, le=2160)


class BrowserConfig(BaseModel):
    """Browser configuration settings."""

    browser: Literal["chromium", "firefox", "webkit"] = "chromium"
    headless: bool = True
    viewport: ViewportSize = Field(default_factory=ViewportSize)
    locale: str = "en-US"
    timezone: str = "UTC"
    user_agent: str | None = None
    device_scale_factor: float = Field(default=1.0, gt=0, le=3)
    is_mobile: bool = False
    has_touch: bool = False
    color_scheme: Literal["light", "dark", "no-preference"] = "light"
