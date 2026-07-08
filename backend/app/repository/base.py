"""Repository protocol — abstract persistence contract.

Routes depend on this Protocol, never on a concrete implementation.
Swapping from Firestore to any other backend requires only a new
implementation file — no route changes.
"""

from __future__ import annotations

from typing import Protocol

from app.models import OpsActionRecord, OpsActionRequest


class OpsRepository(Protocol):
    """Persistence contract for operational action records.

    Two implementations exist:
    - FirestoreOpsRepository (production)
    - MemoryOpsRepository (dev/testing)

    The DI module selects the implementation based on USE_FIRESTORE.
    """

    def log_action(self, action: OpsActionRequest) -> OpsActionRecord:
        """Persist an operational action and return the stored record."""
        ...

    def list_actions(self, limit: int = 50) -> list[OpsActionRecord]:
        """Return recent actions, newest first."""
        ...

    async def async_log_action(self, action: OpsActionRequest) -> OpsActionRecord:
        """Async wrapper for log_action."""
        ...

    async def async_list_actions(self, limit: int = 50) -> list[OpsActionRecord]:
        """Async wrapper for list_actions."""
        ...
