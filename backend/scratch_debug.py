from fastapi.testclient import TestClient
from app.main import create_app

app = create_app()
client = TestClient(app)

resp = client.post("/api/chat", json={
    "message": "Where can I eat?",
    "language": "en",
    "device_id": "test-device-123",
})
print("STATUS CODE:", resp.status_code)
print("BODY:", resp.json())
