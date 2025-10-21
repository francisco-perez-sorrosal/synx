"""Code execution functionality for Synx."""

import io
import json
from contextlib import redirect_stderr, redirect_stdout
from typing import Any

import numpy as np
from mcp.server.fastmcp import Context
from pydantic import BaseModel, Field

from synx.logger import get_logger
from synx.sessions import Session, SessionManager

logger = get_logger()


class ExecutionState(BaseModel):
    """State of the execution of a code block."""

    model_config = {"arbitrary_types_allowed": True}

    stdout: str = Field(description="Standard output of the execution")
    stderr: str = Field(description="Standard error of the execution")
    variables: dict[str, Any] = Field(
        description="Variables created/modified during the execution"
    )
    session: Session = Field(description="Session object")


class PythonExecutor:
    """Executes Python code in isolated environments with session management."""

    def __init__(self):
        """Initialize the Python executor."""
        self.session_manager = SessionManager()

    async def execute(
        self, ctx: Context, code: str, session_id: str | None = None
    ) -> ExecutionState:
        """
        Execute Python code in an isolated environment.

        Args:
            code: Python code to execute
            session_id: Optional session ID for maintaining state

        Returns:
            ExecutionState object
        """
        await ctx.log("info", f"Executing code for session: {session_id or 'default'}")
        session = await self.session_manager.get_or_create_session(ctx, session_id)

        async with session.lock:
            # Prepare execution environment
            exec_globals = {
                "__builtins__": __builtins__,
                "__name__": "__main__",
                "__doc__": None,
                "np": np,
                "numpy": np,
            }
            exec_globals.update(session.globals)
            exec_locals = session.locals.copy()

            # Capture stdout/stderr
            stdout_capture = io.StringIO()
            stderr_capture = io.StringIO()

            try:
                # Execute the code
                with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                    exec(code, exec_globals, exec_locals)
                await ctx.log("info", "Code executed successfully")
                # Update session state
                self.session_manager.update_session(
                    str(session.session_id), exec_globals, exec_locals
                )

                # Capture any variables that were created/modified
                new_variables = {}
                for key, value in exec_locals.items():
                    if not key.startswith("__"):
                        try:
                            # Try to serialize the variable
                            json.dumps(value)
                            new_variables[key] = value
                        except (TypeError, ValueError):
                            # If not serializable, convert to string representation
                            new_variables[key] = str(value)
                return ExecutionState(
                    stdout=stdout_capture.getvalue(),
                    stderr=stderr_capture.getvalue(),
                    variables=new_variables,
                    session=session,
                )
            except Exception as e:
                error_output = stderr_capture.getvalue()
                if error_output:
                    await ctx.log(
                        "error",
                        f"Error executing code (stderr): {error_output.strip()}",
                    )
                    raise Exception(
                        f"Error executing code: {error_output.strip()}"
                    ) from e
                await ctx.log("error", f"Error executing code (exception): {e}")
                raise Exception(f"Error executing code: {e}") from e
