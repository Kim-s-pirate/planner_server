import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
from fastapi.testclient import TestClient
from Controller.main import app  # FastAPI 애플리케이션이 정의된 파일과 경로

client = TestClient(app)

def test_main_without_token():
    response = client.get("/")
    assert response.status_code == 400
    assert response.json() == {"message": "Token not found"}

def test_main_with_invalid_token(monkeypatch):
    def mock_verify_token(token):
        return False

    monkeypatch.setattr("Service.authorization_service.verify_token", mock_verify_token)

    response = client.get("/", headers={"Authorization": "Bearer invalid_token"})
    assert response.status_code == 400
    assert response.json() == {"message": "Token verification failed"}

def test_main_with_valid_token(monkeypatch):
    valid_token = "valid_token"

    def mock_verify_token(token):
        return {
            "userid": "userid_placeholder",
            "exp": (datetime.now(timezone.utc) + timedelta(hours=1000000)).timestamp()
        }

    monkeypatch.setattr("Service.authorization_service.verify_token", mock_verify_token)

    response = client.get("/", headers={"Authorization": f"Bearer {valid_token}"})
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert data["data"]["userid"] == "userid_placeholder"
    assert "exp" in data["data"]

def test_main_exception_handling(monkeypatch):
    def mock_get_token(request):
        raise Exception("Test Exception")

    monkeypatch.setattr("Service.authorization_service.get_token", mock_get_token)

    response = client.get("/")
    assert response.status_code == 409
    assert response.json() == {"message": "There was some error"}
