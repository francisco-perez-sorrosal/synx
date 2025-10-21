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


class MCPTransport(str, Enum):
    """MCP transport enumeration."""

    STDIO = "stdio"
    STREAMABLE_HTTP = "streamable-http"


class AppConfig(BaseModel):
    """Application configuration model."""

    debug: bool = Field(default=False, description="Enable debug mode")
    log_level: LogLevel = Field(default=LogLevel.INFO, description="Log level")
    mcp_transport: MCPTransport = Field(
        default=MCPTransport.STDIO, description="MCP server transport type"
    )
    mcp_host: str = Field(default="localhost", description="Host for MCP transport")
    mcp_port: int = Field(default=10000, description="Port for MCP transport")

    def __str__(self) -> str:
        """String representation of AppConfig."""
        return (
            f"AppConfig(debug={self.debug}, log_level={self.log_level}, "
            f"mcp_transport={self.mcp_transport}, mcp_host={self.mcp_host}, "
            f"mcp_port={self.mcp_port})"
        )


def load_config() -> AppConfig:
    """Load application configuration from environment variables.

    Returns:
        Configured AppConfig instance.
    """
    return AppConfig(
        debug=os.getenv("DEBUG", "false").lower() == "true",
        log_level=LogLevel(os.getenv("LOG_LEVEL", "INFO")),
        mcp_transport=MCPTransport(os.getenv("TRANSPORT", "stdio")),
        mcp_host=os.getenv("HOST", "localhost"),
        mcp_port=int(os.getenv("PORT", "10000")),
    )
