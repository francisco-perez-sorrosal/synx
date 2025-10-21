"""Configuration management for Synx."""

import os
from enum import Enum

from pydantic import BaseModel, Field


class LogLevel(str, Enum):
    """Log level enumeration."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class AppConfig(BaseModel):
    """Application configuration model."""

    debug: bool = Field(default=False, description="Enable debug mode")
    log_level: LogLevel = Field(default=LogLevel.INFO, description="Log level")

    def __str__(self) -> str:
        """String representation of AppConfig."""
        return f"AppConfig(debug={self.debug}, log_level={self.log_level})"


def load_config() -> AppConfig:
    """Load application configuration from environment variables.

    Returns:
        Configured AppConfig instance.
    """
    return AppConfig(
        debug=os.getenv("DEBUG", "false").lower() == "true",
        log_level=LogLevel(os.getenv("LOG_LEVEL", "INFO")),
    )
