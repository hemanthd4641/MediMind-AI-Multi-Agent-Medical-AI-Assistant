from fastapi.testclient import TestClient
from backend.app import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    json = response.json()
    assert json["status"] == "healthy"
    assert json["version"] == "1.0.0"

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    json = response.json()
    assert json["application"] == "MediMind AI"
    assert json["status"] == "running"
