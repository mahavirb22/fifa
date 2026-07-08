"""In-memory repository — full-featured implementation for dev and testing.

Thread-safe via threading lock. This is NOT a stub — it provides complete
functionality identical to the Firestore implementation. Actions are stored
in memory and lost on process restart, which is acceptable for development
and testing scenarios.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from threading import Lock

from app.models import OpsActionRecord, OpsActionRequest


class MemoryOpsRepository:
    """In-memory implementation of the OpsRepository protocol."""

    def __init__(self) -> None:
        """Initialize empty storage with thread safety."""
        self._actions: list[OpsActionRecord] = []
        self._lock = Lock()

    def log_action(self, action: OpsActionRequest) -> OpsActionRecord:
        """Store an operational action in memory."""
        record = OpsActionRecord(
            id=str(uuid.uuid4()),
            action_type=action.action_type,
            target_zone=action.target_zone,
            notes=action.notes,
            operator_id=action.operator_id,
            created_at=datetime.now(tz=timezone.utc),
        )
        with self._lock:
            self._actions.append(record)
        return record

    def list_actions(self, limit: int = 50) -> list[OpsActionRecord]:
        """Return recent actions, newest first."""
        with self._lock:
            return sorted(
                self._actions,
                key=lambda a: a.created_at,
                reverse=True,
            )[:limit]

    async def async_log_action(self, action: OpsActionRequest) -> OpsActionRecord:
        """Async wrapper — in-memory is instant, no thread needed."""
        return self.log_action(action)

    async def async_list_actions(self, limit: int = 50) -> list[OpsActionRecord]:
        """Async wrapper — in-memory is instant, no thread needed."""
        return self.list_actions(limit)
