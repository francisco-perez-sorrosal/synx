import os
from pydantic_core.core_schema import to_string_ser_schema
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AnyHttpUrl
from typing import Any


class AuthConfig(BaseSettings):
    """Settings for the MCP Resource Server."""

    # Authorization Server settings
    auth_server_url: str = f"{os.getenv('AUTH_SERVER_URL', 'http://localhost:9000')}/login"
    auth_server_introspection_endpoint: str = f"{os.getenv('AUTH_SERVER_URL', 'http://localhost:9000')}/introspect"
    # No user endpoint needed - we get user data from token introspection

    resource_server_url: str = f"{os.getenv('RESOURCE_SERVER_URL', 'http://localhost:10000')}/mcp"
    
    # MCP settings
    mcp_scope: str = "user"

    # RFC 8707 resource validation
    oauth_strict: bool = False
