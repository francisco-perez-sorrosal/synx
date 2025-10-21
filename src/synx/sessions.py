import asyncio
import threading
import uuid
from datetime import datetime
from typing import Any

from mcp.server.fastmcp import Context
from pydantic import BaseModel, Field


class Session(BaseModel):
    """Represents a code execution session with persistent state."""

    model_config = {"arbitrary_types_allowed": True}

    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=datetime.now)
    lock: asyncio.Lock = Field(default_factory=asyncio.Lock, exclude=True)
    globals: dict[str, Any] = Field(default_factory=dict, exclude=True)
    locals: dict[str, Any] = Field(default_factory=dict, exclude=True)
    execution_count: int = Field(default=0)

    def __str__(self) -> str:
        """String representation of Session."""
        return f"Session(id={self.session_id}, execution_count={self.execution_count})"


class SessionManager:
    """Manages code execution sessions."""

    exec_globals = {
        "__builtins__": __builtins__,
        "__name__": "__main__",
        "__doc__": None,
    }

    def __init__(self):
        """Initialize the session manager."""
        self._sessions_lock = threading.Lock()
        self._sessions: dict[str, Session] = {}

    async def get_or_create_session(
        self, ctx: Context, session_id: str | None = None
    ) -> Session:
        """Get existing session or create a new one.

        Args:
            session_id: Optional session identifier

        Returns:
            Session object
        """
        with self._sessions_lock:
            if session_id is None:
                session = Session()
                await ctx.log("info", f"Creating new session: {session.session_id}")
                self._sessions[session.session_id] = session
                return session
            else:
                found_session = self._sessions.get(session_id)
                if found_session is None:
                    await ctx.log("error", f"Session {session_id} not found")
                    raise KeyError(f"Session {session_id} not found")
                await ctx.log("info", f"Session {session_id} found")
                return found_session

    def get_session(self, session_id: str) -> Session:
        """Get session by ID.

        Args:
            session_id: Session identifier

        Returns:
            Session object
        """
        with self._sessions_lock:
            return self._sessions[session_id]

    def update_session(
        self, session_id: str, exec_globals: dict[str, Any], exec_locals: dict[str, Any]
    ) -> None:
        with self._sessions_lock:
            session = self._sessions[session_id]
            session.globals.update(exec_globals)
            session.locals.update(exec_locals)
            session.execution_count += 1

    def list_sessions(self) -> list[str]:
        with self._sessions_lock:
            return list(self._sessions.keys())
