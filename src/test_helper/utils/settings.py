"""Application settings management using Pydantic Settings (test_helper)."""

from enum import Enum
from typing import Any, ClassVar, Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class OTelExportMode(str, Enum):
    """OpenTelemetry log export modes."""

    FILE = "file"
    OTLP = "otlp"
    BOTH = "both"


class LoggingSettings(BaseSettings):
    """Logging configuration settings.

    All settings can be configured via environment variables.
    """

    instance: ClassVar[Any] = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Basic logging settings
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        description="Logging level",
    )

    log_format: Literal["json", "console", "plain"] = Field(
        default="json",
        description="Log output format",
    )

    log_file_path: str | None = Field(
        default=None,
        description="Path to log file for local file logging",
    )

    # OpenTelemetry settings
    otel_logs_export_mode: OTelExportMode = Field(
        default=OTelExportMode.FILE,
        description="OpenTelemetry logs export mode: file, otlp, or both",
    )

    otel_endpoint: str = Field(
        default="http://localhost:4317",
        description="OpenTelemetry collector endpoint",
    )

    otel_service_name: str = Field(
        default="python-app",
        description="Service name for OpenTelemetry",
    )

    otel_export_timeout: int = Field(
        default=30000,
        description="OpenTelemetry export timeout in milliseconds",
        ge=1,
    )

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level value."""
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if v.upper() not in valid_levels:
            msg = f"Invalid log level: {v}. Must be one of {valid_levels}"
            raise ValueError(msg)
        return v.upper()

    @field_validator("log_format")
    @classmethod
    def validate_log_format(cls, v: str) -> str:
        """Validate log format value."""
        valid_formats = {"json", "console", "plain"}
        if v.lower() not in valid_formats:
            msg = f"Invalid log format: {v}. Must be one of {valid_formats}"
            raise ValueError(msg)
        return v.lower()

    @field_validator("otel_export_timeout")
    @classmethod
    def validate_timeout(cls, v: int) -> int:
        """Validate timeout is positive."""
        if v <= 0:
            msg = "Timeout must be a positive integer"
            raise ValueError(msg)
        return v

    @property
    def otel_export_enabled(self) -> bool:
        """Check if OpenTelemetry export is enabled."""
        return self.otel_logs_export_mode in (OTelExportMode.OTLP, OTelExportMode.BOTH)

    def model_dump(self, **kwargs: Any) -> dict[str, Any]:
        """Dump model including computed properties."""
        data = super().model_dump(**kwargs)
        data["otel_export_enabled"] = self.otel_export_enabled
        return data


class InterfaceSettings(BaseSettings):
    """Interface configuration settings."""

    instance: ClassVar[Any] = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    interface_type: str = Field(
        default="cli",
        description="Type of interface to use (cli, restapi)",
    )

    @field_validator("interface_type")
    @classmethod
    def validate_interface_type(cls, v: str) -> str:
        """Validate interface type value."""
        from test_helper.types import InterfaceType

        try:
            # Validate that it's a valid interface type
            InterfaceType(v.lower())
            return v.lower()
        except ValueError:
            valid_types = [t.value for t in InterfaceType]
            msg = f"Invalid interface type: {v}. Must be one of {valid_types}"
            raise ValueError(msg) from None

    @property
    def interface_type_enum(self) -> Any:
        """Get interface type as enum."""
        from test_helper.types import InterfaceType

        return InterfaceType(self.interface_type)


def get_settings() -> LoggingSettings:
    """Get the global settings instance.

    Returns:
        LoggingSettings: The settings instance

    """
    if LoggingSettings.instance is None:
        LoggingSettings.instance = LoggingSettings()
    return LoggingSettings.instance


def reset_settings() -> None:
    """Reset the global settings instance.

    This is mainly useful for testing.
    """
    LoggingSettings.instance = None


def get_interface_settings() -> InterfaceSettings:
    """Get the global interface settings instance.

    Returns:
        InterfaceSettings: The interface settings instance

    """
    if InterfaceSettings.instance is None:
        InterfaceSettings.instance = InterfaceSettings()
    return InterfaceSettings.instance


def reset_interface_settings() -> None:
    """Reset the global interface settings instance.

    This is mainly useful for testing.
    """
    InterfaceSettings.instance = None


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
    e2e_data_path: Any = Field(
        default="data",
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
        description="Default browser viewport width",
        ge=320,
        le=3840,
    )

    default_viewport_height: int = Field(
        default=720,
        description="Default browser viewport height",
        ge=240,
        le=2160,
    )

    # Test generation settings
    test_generation_timeout: int = Field(
        default=5000,
        description="Timeout for test generation in milliseconds",
        ge=1000,
        le=30000,
    )

    test_fix_timeout: int = Field(
        default=10000,
        description="Timeout for test fixing in milliseconds",
        ge=1000,
        le=60000,
    )

    # Storage settings
    retention_days: int = Field(
        default=30,
        description="Days to retain test history",
        ge=1,
        le=365,
    )

    max_test_files: int = Field(
        default=100,
        description="Maximum test files per project",
        ge=1,
        le=1000,
    )

    # Agent settings
    max_memory_mb: int = Field(
        default=2048,
        description="Maximum memory per agent in MB",
        ge=512,
        le=8192,
    )

    # Temporal settings
    temporal_namespace: str = Field(
        default="default",
        description="Temporal namespace for workflows",
    )

    temporal_host: str = Field(
        default="localhost:7233",
        description="Temporal server host and port",
    )

    # OpenAI settings
    openai_api_key: str | None = Field(
        default=None,
        description="OpenAI API key for AI agents",
    )

    openai_model: str = Field(
        default="gpt-4",
        description="OpenAI model to use for agents",
    )

    # Backend switching for mocks vs real SDKs
    agent_backend: Literal["mock", "sdk"] = Field(
        default="mock",
        description="OpenAI agent backend (mock or sdk)",
    )

    temporal_backend: Literal["mock", "sdk"] = Field(
        default="mock",
        description="Temporal backend (mock or sdk)",
    )

    @field_validator("default_browser")
    @classmethod
    def validate_browser(cls, v: str) -> str:
        """Validate browser value."""
        valid_browsers = {"chromium", "firefox", "webkit"}
        if v.lower() not in valid_browsers:
            msg = f"Invalid browser: {v}. Must be one of {valid_browsers}"
            raise ValueError(msg)
        return v.lower()

    def __init__(self, **kwargs: Any) -> None:
        """Initialize E2E settings."""
        super().__init__(**kwargs)
        # Import Path here to avoid issues
        from pathlib import Path

        if isinstance(self.e2e_data_path, str):
            self.e2e_data_path = Path(self.e2e_data_path)


def get_e2e_settings() -> E2ESettings:
    """Get the global E2E settings instance.

    Returns:
        E2ESettings: The E2E settings instance

    """
    if E2ESettings.instance is None:
        E2ESettings.instance = E2ESettings()
    return E2ESettings.instance


def reset_e2e_settings() -> None:
    """Reset the global E2E settings instance.

    This is mainly useful for testing.
    """
    E2ESettings.instance = None
