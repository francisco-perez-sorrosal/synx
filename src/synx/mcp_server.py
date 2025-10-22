"""MCP Server for Synx - Synapse Executor."""

import os

from mcp.server.fastmcp import Context, FastMCP

from synx.code_executor import PythonExecutor
from synx.config import MCPTransport
from synx.logger import get_logger

logger = get_logger()

# Load host/port from environment at module level
_mcp_host = os.getenv("HOST", "0.0.0.0")
_mcp_port = int(os.getenv("PORT", "10000"))

logger.info(f"MCP host: {_mcp_host}, MCP port: {_mcp_port}")
# Configure FastMCP with proper settings for streamable HTTP
mcp = FastMCP(
    "synx",
    host=_mcp_host,
    port=_mcp_port
)

executor = PythonExecutor()


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


def run_server(transport: MCPTransport = MCPTransport.STDIO):
    """Start the MCP server with specified transport configuration.

    Args:
        transport: Transport type ("stdio" or "streamable_http")
        host: Host address for streamable_http transport (for logging only)
        port: Port number for streamable_http transport (for logging only)
    """
    logger.info(f"Starting Synx MCP Server (transport={transport})")

    if transport == MCPTransport.STREAMABLE_HTTP:
        logger.info(f"Server listening on {_mcp_host}:{_mcp_port}")
    else:
        logger.info("Server listening on stdio")
    mcp.run(transport=transport.value)


if __name__ == "__main__":
    run_server()
