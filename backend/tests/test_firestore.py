from unittest.mock import MagicMock, patch
import pytest
from app.models import OpsActionRequest, ActionType
from app.repository.firestore_repo import FirestoreOpsRepository


@pytest.fixture()
def mock_firestore():
    with patch("google.cloud.firestore.Client") as mock_client:
        client_instance = mock_client.return_value
        yield client_instance


def test_firestore_log_action(mock_firestore):
    # Setup mock
    mock_coll = mock_firestore.collection.return_value
    mock_doc = mock_coll.document.return_value

    repo = FirestoreOpsRepository(project_id="test-proj")
    action = OpsActionRequest(
        action_type=ActionType.DEPLOY_STAFF,
        target_zone="gate-a",
        notes="Testing firestore repo",
        operator_id="operator-123",
    )

    record = repo.log_action(action)

    assert record.action_type == ActionType.DEPLOY_STAFF
    assert record.target_zone == "gate-a"
    assert record.notes == "Testing firestore repo"
    assert record.operator_id == "operator-123"
    assert record.id is not None

    mock_firestore.collection.assert_called_with("ops_actions")
    mock_coll.document.assert_called_once()
    mock_doc.set.assert_called_once()


def test_firestore_list_actions(mock_firestore):
    # Setup mock stream
    mock_coll = mock_firestore.collection.return_value
    mock_order = mock_coll.order_by.return_value
    mock_limit = mock_order.limit.return_value

    doc1 = MagicMock()
    doc1.id = "id-1"
    doc1.to_dict.return_value = {
        "action_type": "deploy_staff",
        "target_zone": "gate-a",
        "notes": "note 1",
        "operator_id": "operator-1",
        "created_at": "2026-07-08T12:00:00Z",
    }

    mock_limit.stream.return_value = [doc1]

    repo = FirestoreOpsRepository(project_id="test-proj")
    records = repo.list_actions(limit=10)

    assert len(records) == 1
    assert records[0].id == "id-1"
    assert records[0].action_type == ActionType.DEPLOY_STAFF
    assert records[0].notes == "note 1"

    mock_firestore.collection.assert_called_with("ops_actions")
    mock_coll.order_by.assert_called_with("created_at", direction="DESCENDING")
    mock_order.limit.assert_called_with(10)


@pytest.mark.anyio()
async def test_async_wrappers(mock_firestore):
    mock_coll = mock_firestore.collection.return_value
    mock_doc = mock_coll.document.return_value
    mock_order = mock_coll.order_by.return_value
    mock_limit = mock_order.limit.return_value
    mock_limit.stream.return_value = []

    repo = FirestoreOpsRepository(project_id="test-proj")
    action = OpsActionRequest(
        action_type=ActionType.OPEN_GATE,
        target_zone="gate-c",
        notes="Opening gate",
        operator_id="operator-2",
    )

    record = await repo.async_log_action(action)
    assert record.action_type == ActionType.OPEN_GATE

    actions = await repo.async_list_actions(limit=5)
    assert len(actions) == 0
