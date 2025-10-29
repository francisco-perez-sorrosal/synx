"""MCP Server for Synx - Synapse Executor."""

import asyncio
import os

from mcp.server.fastmcp import Context, FastMCP
from mcp.server.auth.settings import AuthSettings
from pydantic import AnyHttpUrl

from synx.auth.token_verifier import SimpleTokenVerifier
from synx.auth_config import AuthConfig
from synx.code_executor import PythonExecutor
from synx.config import MCPTransport
from synx.logger import get_logger

logger = get_logger()

# TODO: Remove this once the FastMCP class is fixed.
import uvicorn
from mcp.server.auth.handlers.metadata import ProtectedResourceMetadataHandler
from mcp.server.auth.routes import cors_middleware
from mcp.shared.auth import ProtectedResourceMetadata
from starlette.routing import Route

class FastMCPFixedOAuth(FastMCP):
    # TODO: This is a hack to fix the FastMCP class to work with OAuth 2.0 Protected Resource Metadata. Remove this once the FastMCP class is fixed.

    async def run_streamable_http_async(self) -> None:
        """Run the server using StreamableHTTP transport."""

        starlette_app = self.streamable_http_app()

        config = uvicorn.Config(
            starlette_app,
            host=self.settings.host,
            port=self.settings.port,
            log_level=self.settings.log_level.lower(),
            # This solves the issue of the server not shutting down gracefully when stopping the server with Ctrl+C. Commented out bc I suspect it's affecting the OAuth flow!!!!
            # timeout_keep_alive=5,  # Close idle connections after 5 seconds.
            # timeout_graceful_shutdown=10,  # Wait max 10 seconds for graceful shutdown            
        )
        
        if self.settings.auth is not None:                    
            # Remove existing Protected Resource Metadata endpoint (resource="http://localhost:8000/")
            logger.warning(f"Removing existing Protected Resource Metadata endpoint: {starlette_app.router.routes}")
            starlette_app.router.routes = list(filter(lambda r: r.path != "/.well-known/oauth-protected-resource", starlette_app.router.routes))

            # Add OAuth 2.0 Protected Resource Metadata endpoint as per RFC 9728 (resource="http://localhost:8000/mcp")
            protected_resource_metadata = ProtectedResourceMetadata(
                resource=AnyHttpUrl(str(self.settings.auth.resource_server_url)+"mcp"), # Real fix
                authorization_servers=[self.settings.auth.issuer_url],
                scopes_supported=self.settings.auth.required_scopes,
            )
            
            logger.warning(f"Adding new Protected Resource Metadata JSON endpoint: {protected_resource_metadata}")
            starlette_app.router.routes.append(Route("/.well-known/oauth-protected-resource", endpoint=cors_middleware(ProtectedResourceMetadataHandler(protected_resource_metadata).handle, ["GET", "OPTIONS"]), methods=["GET", "OPTIONS"]))

        # New server with fixed OAuth
        server = uvicorn.Server(config)
        await server.serve()
        

def create_mcp_server(host: str, port: int, auth_config: AuthConfig | None) -> FastMCP:
    # Load host/port from environment at module level
    mcp_host = os.getenv("HOST", host)
    mcp_port = int(os.getenv("PORT", port))
    
    # Auth configuration
    auth_settings = None
    token_verifier = None
    if auth_config is not None:
        this_mcp_server_url: AnyHttpUrl = AnyHttpUrl(f"{auth_config.resource_server_url}")
        auth_settings = AuthSettings(
            issuer_url=auth_config.auth_server_url,
            required_scopes=[auth_config.mcp_scope],
            resource_server_url=this_mcp_server_url,
        )
        logger.info(f"Using auth: {auth_settings}")
        
        # Create token verifier for introspection with RFC 8707 resource validation
        token_verifier = SimpleTokenVerifier(
            introspection_endpoint=auth_config.auth_server_introspection_endpoint,
            server_url=str(this_mcp_server_url),
            oauth_strict=auth_config.oauth_strict,  # Only validate when --oauth-strict is set
        )
    else:
        logger.warning("No auth used!")

    # Configure FastMCP with proper settings for streamable HTTP
    return FastMCPFixedOAuth(
        "synx",
        host=mcp_host,
        port=mcp_port,
        auth=auth_settings,
        token_verifier=token_verifier,
    )


async def run_server(mcp: FastMCP, transport: MCPTransport = MCPTransport.STDIO):
    executor = PythonExecutor()
    
    logger.info(f"Starting Synx MCP Server (transport={transport})")

    @mcp.tool(name="run", description="Execute Python code in an isolated environment")
    async def run_code(ctx: Context, code: str, session_id: str | None = None) -> str:
        """
        Execute Python code in an isolated environment.

        Args:
            code: Python code to execute
            session_id: Optional session ID for maintaining state

        Returns:
            JSON string with execution results
        """
        await ctx.log("info", f"Executing code: {code} for session: {session_id}")
        result = await executor.execute(ctx, code, session_id)
        await ctx.log("info", f"Execution result: {result}")
        res = result.model_dump_json(indent=2)
        await ctx.log("info", f"Result dumped to JSON: {res}")
        return res

    if transport == MCPTransport.STREAMABLE_HTTP:
        logger.info(f"Server listening on {mcp.settings.host}:{mcp.settings.port}")
        await mcp.run_streamable_http_async()
    else:
        logger.info("Server listening on stdio")
        await mcp.run_stdio_async()


if __name__ == "__main__":
    mcp_server = create_mcp_server(host="0.0.0.0", port=10000, auth_config=AuthConfig())
    asyncio.run(run_server(mcp_server, transport=MCPTransport.STREAMABLE_HTTP))
