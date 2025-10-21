"""MCP Server for Synx - Synapse Executor."""

from mcp.server.fastmcp import Context, FastMCP

from synx.code_executor import PythonExecutor
from synx.logger import get_logger

logger = get_logger()

mcp = FastMCP("synx")

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


def run_server():
    logger.info("Starting Synx MCP Server")
    mcp.run()


if __name__ == "__main__":
    run_server()
