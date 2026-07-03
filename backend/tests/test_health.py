from fastapi.testclient import TestClient
from unittest.mock import patch
from backend.main import app

client = TestClient(app)

@patch("backend.api.health.embedding_service.health_check")
def test_health_endpoint(mock_health_check):
    mock_health_check.return_value = {
        "status": "healthy",
        "provider": "mock",
        "model_name": "mock",
        "device": "cpu",
        "api_reachability": "N/A"
    }
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
