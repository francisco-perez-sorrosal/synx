"""Main CLI application for Synx - Synapse Executor."""


import asyncio
import os
import typer
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel

from synx import __version__
from synx.auth_config import AuthConfig
from synx.config import AppConfig, LogLevel, MCPTransport
from synx.logger import LogConfig, get_logger, setup_logger
from synx.mcp_server import create_mcp_server, run_server

# Load environment variables
load_dotenv()

# Initialize rich console and logger
console = Console()
logger = get_logger()

app = typer.Typer(
    name="synx",
    help="Synx - Synapse Executor: Isolated environment to run Python code",
    add_completion=False,
)


@app.command()
def start(
    debug: bool = typer.Option(False, "--debug", "-d", help="Enable debug mode"),
    log_level: str = typer.Option("INFO", "--log-level", "-l", help="Set log level"),
    use_auth: bool = typer.Option(bool(os.getenv("USE_AUTH", False)), "--use-auth", "-a", help="Use authentication"),
) -> None:
    """Main command demonstrating Synx capabilities.

    Args:
        debug: Enable debug mode for verbose output.
        log_level: Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        use_auth: Use authentication.
    """
    # Load configuration
    config = AppConfig()
    logger.info(f"App config: {config}")

    # Override config with CLI arguments
    if debug:
        config.debug = True
        
    if log_level.upper() in [level.value for level in LogLevel]:
        config.log_level = LogLevel(log_level.upper())

    if use_auth:
        auth_config = AuthConfig()
    else:
        auth_config = None
    logger.info(f"Auth config: {auth_config}")

    transport_info = (
        f"{config.mcp_host}:{config.mcp_port}"
        if config.mcp_transport.value == MCPTransport.STREAMABLE_HTTP.value
        else "stdio"
    )
    console.print(
        Panel(
            f"[bold green]Starting Synx MCP Server[/bold green]\n"
            f"[dim]Transport: {config.mcp_transport.value}[/dim]\n"
            f"[dim]Listening on: {transport_info}[/dim]\n"
            f"[dim]Using auth: {use_auth}[/dim]",
            border_style="green",
        )
    )
    mcp_server = create_mcp_server(host=config.mcp_host, port=config.mcp_port, auth_config=auth_config)
    asyncio.run(run_server(mcp_server, transport=config.mcp_transport))


@app.command()
def version() -> None:
    """Show version information."""
    console.print(f"Synx v{__version__}")
    console.print("Author: Francisco Perez-Sorrosal")
    console.print("Email: fperezsorrosal@gmail.com")


@app.command()
def main() -> None:
    # Trick to get the default values of the start command. Do not remove this!
    arg_defaults = start.__defaults__
    if arg_defaults:
        console.print(f"Running start with default values. arg_defaults: {arg_defaults[0].default} {arg_defaults[1].default} ")
        first_arg = arg_defaults[0].default
        second_arg = arg_defaults[1].default
        third_arg = arg_defaults[2].default
        start(first_arg, second_arg, third_arg)
    else:
        console.print("No arg defaults found, running start with default values")
        start()

if __name__ == "__main__":
    main()
