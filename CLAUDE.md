# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Synx** (Synapse Executor) is an MCP (Model Context Protocol) server that provides isolated Python code execution with session management. It allows executing Python code in sandboxed environments while maintaining state across multiple executions within the same session.

## Environment & Tooling

This project uses **Pixi** for dependency management and environment handling (NOT pip/venv). All commands must be prefixed with `pixi run`.

### Essential Commands

```bash
# Start the MCP server
pixi run start

# Run tests
pixi run test

# Code quality
pixi run format      # Format with black
pixi run lint        # Lint with ruff
pixi run type-check  # Type check with mypy
```

### Running Single Tests

```bash
pixi run pytest tests/test_mcp_server.py::test_name -v
```

## Architecture

### Core Components

1. **MCP Server** (`mcp_server.py`)
   - Built on FastMCP framework
   - Exposes `run` tool for code execution
   - Entry point: `run_server()`

2. **Code Executor** (`code_executor.py`)
   - `PythonExecutor`: Executes Python code in isolated environments
   - Captures stdout/stderr using context managers
   - Returns `ExecutionState` with output, variables, and session info
   - Serializes variables to JSON when possible, falls back to string representation

3. **Session Management** (`sessions.py`)
   - `Session`: Represents execution state with persistent namespace
   - `SessionManager`: Thread-safe session management with locks
   - Sessions maintain separate `globals` and `locals` dictionaries
   - Each session tracks execution count and creation time

4. **Configuration** (`config.py`)
   - Pydantic-based configuration from environment variables
   - Debug mode and log level settings

### Key Flows

**Code Execution Flow:**
1. MCP tool `run_code()` receives code and optional session_id
2. `PythonExecutor.execute()` gets or creates session via SessionManager
3. Code executes with session's globals/locals in isolated namespace
4. Stdout/stderr captured, variables serialized
5. Session state updated with new globals/locals
6. ExecutionState returned as JSON

**Session Lifecycle:**
- New session created if session_id is None
- Session state persists across executions within same session_id
- Thread-safe access via `threading.Lock` and `asyncio.Lock`

## Dependencies

- **MCP**: `mcp[cli]>=1.18.0,<2` - Model Context Protocol framework
- **Typer**: CLI framework
- **Rich**: Terminal formatting
- **Loguru**: Logging
- **Pydantic**: Configuration and data validation
- **python-dotenv**: Environment variable management

## Configuration

Environment variables (see `.env.example`):
- `DEBUG`: Enable debug mode (default: false)
- `LOG_LEVEL`: Logging level (default: INFO)

Command-line overrides available via `--debug` and `--log-level` flags.

## Code Quality Standards

- **Line length**: 88 characters (Black default)
- **Python version**: 3.11+
- **Type hints**: Recommended but not strictly enforced (mypy configured with relaxed settings for POC)
- **Import sorting**: Handled by ruff (isort rules)

## Entry Points

- Module execution: `python -m synx start` (via pixi)
- Direct: `src/synx/__main__.py`
- Server aliases: `pixi run mcp`, `pixi run mcps`, `pixi run server` (all equivalent to `pixi run start`)
