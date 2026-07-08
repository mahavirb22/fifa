"""Firestore repository — production persistence for operational actions.

Lazy SDK import: the google.cloud.firestore SDK is imported inside __init__
so importing this module never triggers credential loading. Uses
asyncio.to_thread for async wrappers since the Firestore Python SDK is
synchronous.
"""

from __future__ import annotations

import asyncio
import uuid
from datetime import datetime, timezone

from app.models import OpsActionRecord, OpsActionRequest


class FirestoreOpsRepository:
    """Firestore-backed implementation of the OpsRepository protocol."""

    def __init__(self, project_id: str) -> None:
        """Initialize Firestore client with lazy SDK import."""
        from google.cloud import firestore  # Lazy import — no creds at import time

        self._db = firestore.Client(project=project_id)
        self._collection = "ops_actions"

    def log_action(self, action: OpsActionRequest) -> OpsActionRecord:
        """Persist an operational action to Firestore."""
        record_id = str(uuid.uuid4())
        now = datetime.now(tz=timezone.utc)

        doc_data = {
            "action_type": action.action_type.value,
            "target_zone": action.target_zone,
            "notes": action.notes,
            "operator_id": action.operator_id,
            "created_at": now.isoformat(),
        }

        self._db.collection(self._collection).document(record_id).set(doc_data)

        return OpsActionRecord(
            id=record_id,
            action_type=action.action_type,
            target_zone=action.target_zone,
            notes=action.notes,
            operator_id=action.operator_id,
            created_at=now,
        )

    def list_actions(self, limit: int = 50) -> list[OpsActionRecord]:
        """Return recent actions from Firestore, newest first."""
        from app.models import ActionType

        query = (
            self._db.collection(self._collection)
            .order_by("created_at", direction="DESCENDING")
            .limit(limit)
        )

        records: list[OpsActionRecord] = []
        for doc in query.stream():
            data = doc.to_dict()
            if data is None:
                continue
            records.append(OpsActionRecord(
                id=doc.id,
                action_type=ActionType(data["action_type"]),
                target_zone=data["target_zone"],
                notes=data.get("notes", ""),
                operator_id=data.get("operator_id", "unknown"),
                created_at=datetime.fromisoformat(data["created_at"]),
            ))
        return records

    async def async_log_action(self, action: OpsActionRequest) -> OpsActionRecord:
        """Async wrapper — runs sync Firestore call in thread pool."""
        return await asyncio.to_thread(self.log_action, action)

    async def async_list_actions(self, limit: int = 50) -> list[OpsActionRecord]:
        """Async wrapper — runs sync Firestore call in thread pool."""
        return await asyncio.to_thread(self.list_actions, limit)
