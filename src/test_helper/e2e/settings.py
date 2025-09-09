"""E2E Test Automation settings management."""

from pathlib import Path
from typing import Any, ClassVar

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class E2ESettings(BaseSettings):
    """E2E Test Automation configuration settings."""

    instance: ClassVar[Any] = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # E2E Test Data Storage settings
    e2e_data_path: Path = Field(
        default=Path("data"),
        description="Base directory for E2E test data storage",
    )

    # Browser automation settings
    default_browser: str = Field(
        default="chromium",
        description="Default browser for testing (chromium, firefox, webkit)",
    )

    default_headless: bool = Field(
        default=True,
        description="Run browser in headless mode by default",
    )

    default_viewport_width: int = Field(
        default=1280,
        description="Default viewport width",
        ge=320,
        le=3840,
    )

    default_viewport_height: int = Field(
        default=720,
        description="Default viewport height",
        ge=240,
        le=2160,
    )

    # Test execution settings
    default_timeout_ms: int = Field(
        default=30000,
        description="Default test execution timeout in milliseconds",
        ge=1000,
        le=300000,
    )

    default_retry_count: int = Field(
        default=3,
        description="Default retry count for failed tests",
        ge=0,
        le=10,
    )

    # OpenAI settings for test generation
    openai_api_key: str | None = Field(
        default=None,
        description="OpenAI API key for test generation",
    )

    openai_model: str = Field(
        default="gpt-4",
        description="OpenAI model to use for test generation",
    )

    # Temporal settings for workflow orchestration
    temporal_host: str = Field(
        default="localhost:7233",
        description="Temporal server host",
    )

    temporal_namespace: str = Field(
        default="default",
        description="Temporal namespace",
    )

    temporal_task_queue: str = Field(
        default="e2e-test-automation",
        description="Temporal task queue name",
    )


def get_e2e_settings() -> E2ESettings:
    """Get the global E2E settings instance.

    Returns:
        E2ESettings: The settings instance

    """
    if E2ESettings.instance is None:
        E2ESettings.instance = E2ESettings()
    return E2ESettings.instance


def reset_e2e_settings() -> None:
    """Reset the global E2E settings instance.

    This is mainly useful for testing.
    """
    E2ESettings.instance = None
