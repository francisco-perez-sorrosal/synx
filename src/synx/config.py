"""Configuration management for Synx."""

import os
from enum import Enum

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


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


class AppConfig(BaseSettings):
    """Application configuration model."""

    debug: bool = Field(default=bool(os.getenv("DEBUG", False)), description="Enable debug mode")
    log_level: LogLevel = Field(default=LogLevel(os.getenv("LOG_LEVEL", "INFO")), description="Log level")
    mcp_transport: MCPTransport = Field(
        default=MCPTransport(os.getenv("TRANSPORT", "stdio")), description="MCP server transport type"
    )
    mcp_host: str = Field(default=os.getenv("HOST", "localhost"), description="Host for MCP transport")
    mcp_port: int = Field(default=int(os.getenv("PORT", 10000)), description="Port for MCP transport")
    
    # model_config = SettingsConfigDict(env_prefix="SYNX_")
