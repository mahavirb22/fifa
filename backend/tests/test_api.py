"""Integration tests — full HTTP stack via TestClient.

Each test asserts status code, response shape, and meaningful content.
"""


def test_health_returns_status(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] in ("healthy", "degraded")
    assert "version" in data
    assert "gemini_available" in data
    assert "firestore_available" in data


def test_chat_returns_response(client):
    resp = client.post("/api/chat", json={
        "message": "Where can I eat?",
        "language": "en",
        "device_id": "test-device-123",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "reply" in data
    assert data["source"] in ("gemini", "rules", "cache")
    assert len(data["reply"]) > 0


def test_chat_rejects_empty_message(client):
    resp = client.post("/api/chat", json={
        "message": "",
        "language": "en",
        "device_id": "test-device-123",
    })
    assert resp.status_code == 422


def test_chat_rejects_invalid_device_id(client):
    resp = client.post("/api/chat", json={
        "message": "hello",
        "language": "en",
        "device_id": "invalid device id with spaces!",
    })
    assert resp.status_code == 422


def test_chat_spanish_query(client):
    resp = client.post("/api/chat", json={
        "message": "dónde puedo comer",
        "language": "es",
        "device_id": "test-device-456",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["source"] == "rules"


def test_crowd_density_returns_analysis(client):
    resp = client.get("/api/crowd/density")
    assert resp.status_code == 200
    data = resp.json()
    assert "densities" in data
    assert "hotspots" in data
    assert "total_occupancy" in data
    assert "total_capacity" in data
    assert "overall_density_pct" in data
    assert len(data["densities"]) > 0


def test_crowd_snapshot_accepts_valid_data(client):
    resp = client.post("/api/crowd/snapshot", json={
        "zones": [
            {
                "zone_id": "gate-a",
                "current_count": 1000,
                "capacity": 2500,
                "zone_type": "gate",
            },
            {
                "zone_id": "seating-lower-east",
                "current_count": 8000,
                "capacity": 12000,
                "zone_type": "seating",
            },
        ],
    })
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["densities"]) == 2


def test_crowd_snapshot_rejects_empty_zones(client):
    resp = client.post("/api/crowd/snapshot", json={"zones": []})
    assert resp.status_code == 422


def test_ops_recommendations_returns_list(client):
    resp = client.get("/api/ops/recommendations")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)


def test_ops_action_logging(client):
    resp = client.post("/api/ops/action", json={
        "action_type": "deploy_staff",
        "target_zone": "gate-a",
        "notes": "Deployed 3 additional stewards",
        "operator_id": "staff-001",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["action_type"] == "deploy_staff"
    assert data["target_zone"] == "gate-a"
    assert "id" in data
    assert "created_at" in data


def test_ops_actions_list(client):
    # Log an action first
    client.post("/api/ops/action", json={
        "action_type": "open_gate",
        "target_zone": "gate-c",
        "notes": "Opening for overflow",
        "operator_id": "staff-002",
    })
    resp = client.get("/api/ops/actions")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_security_headers_present(client):
    resp = client.get("/api/health")
    assert resp.headers.get("X-Content-Type-Options") == "nosniff"
    assert resp.headers.get("X-Frame-Options") == "DENY"
    assert "Content-Security-Policy" in resp.headers
