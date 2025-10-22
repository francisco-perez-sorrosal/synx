"""Main CLI application for Synx - Synapse Executor."""

import os

import typer
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel

from synx import __version__
from synx.config import LogLevel, MCPTransport, load_config
from synx.logger import LogConfig, get_logger

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
) -> None:
    """Main command demonstrating Synx capabilities.

    Args:
        debug: Enable debug mode for verbose output.
        log_level: Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
    """
    # Load configuration
    config = load_config()

    # Override config with CLI arguments
    if debug:
        config.debug = True
    if log_level.upper() in [level.value for level in LogLevel]:
        config.log_level = LogLevel(log_level.upper())

    # Configure logger with new settings
    from synx.logger import setup_logger

    setup_logger(LogConfig(level=config.log_level))

    # Import mcp_server after environment is configured
    from synx.mcp_server import run_server

    transport_info = (
        f"{config.mcp_host}:{config.mcp_port}"
        if config.mcp_transport.value == MCPTransport.STREAMABLE_HTTP.value
        else "stdio"
    )
    console.print(
        Panel(
            f"[bold green]Starting Synx MCP Server[/bold green]\n"
            f"[dim]Transport: {config.mcp_transport.value}[/dim]\n"
            f"[dim]Listening on: {transport_info}[/dim]",
            border_style="green",
        )
    )
    run_server(transport=config.mcp_transport)


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
    first_arg = arg_defaults[0].default
    second_arg = arg_defaults[1].default
    print(first_arg, second_arg)
    start(first_arg, second_arg)

if __name__ == "__main__":
    main()
