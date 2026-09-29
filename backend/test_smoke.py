
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

def test_demo():
    r = client.post("/api/demo/run")
    assert r.status_code == 200
    data = r.json()
    assert data["revised_belief"] is not None
    assert data["hindsight"]["retain"] == 8
