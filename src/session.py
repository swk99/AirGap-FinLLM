"""
session.py — Volatile In-RAM Session Manager

Sessions live only in RAM. No disk writes, no swap.
Context is overwritten (memset-style) on destroy or TTL expiry.
"""

import uuid
import time
import logging
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger("lmcu.session")

SESSION_TTL_SECONDS = 1800  # 30 min


@dataclass
class Session:
    session_id: str
    role: str
    created_at: float = field(default_factory=time.time)
    context: list = field(default_factory=list)

    def is_expired(self) -> bool:
        return (time.time() - self.created_at) > SESSION_TTL_SECONDS

    def add_turn(self, role: str, content: str) -> None:
        self.context.append({"role": role, "content": content})

    def purge(self) -> None:
        """Overwrite context before GC."""
        for item in self.context:
            item["content"] = "\x00" * len(item["content"])
        self.context.clear()


class SessionManager:
    def __init__(self):
        self._sessions: dict = {}

    def create(self, role: str) -> Session:
        sid = str(uuid.uuid4())
        session = Session(session_id=sid, role=role)
        self._sessions[sid] = session
        logger.info("SESSION CREATE | id=%s role=%s", sid[:8], role)
        return session

    def get(self, session_id: str) -> Optional[Session]:
        session = self._sessions.get(session_id)
        if session is None:
            return None
        if session.is_expired():
            self.destroy(session_id)
            return None
        return session

    def destroy(self, session_id: str) -> None:
        session = self._sessions.pop(session_id, None)
        if session:
            session.purge()
            logger.info("SESSION DESTROY | id=%s (purged)", session_id[:8])
