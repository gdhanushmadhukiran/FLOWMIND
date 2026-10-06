from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "flowmind", "mode": "simulation"}

def test_state():
    response = client.get("/api/state")
    assert response.status_code == 200
    data = response.json()
    assert "timestamp" in data
    assert "summary" in data
    assert "junctions" in data
    assert len(data["junctions"]) > 0
    
def test_websocket():
    with client.websocket_connect("/ws") as websocket:
        data = websocket.receive_json()
        assert "mode" in data
        assert data["mode"] == "simulation"