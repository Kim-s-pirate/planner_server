import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
from fastapi.testclient import TestClient
from Controller.main import app
from Service.user_service import user_service, UserNotFoundError
from Service import authorization_service
from Database.models import user
from unittest.mock import MagicMock
from unittest.mock import patch

client = TestClient(app)

# Mock data
mock_user = {
    "userid": "test_userid",
    "username": "Test User",
    "email": "test@example.com",
    "password": "testpassword"
}


@pytest.fixture
def mock_user_service(monkeypatch):
    # Mock user_service
    class MockUserService:
        @staticmethod
        def find_user_by_email(email):
            if email == "test@example.com":
                return MagicMock(**mock_user)  # Use MagicMock to simulate user model instance
            return None

    monkeypatch.setattr(user_service, "find_user_by_email", MockUserService.find_user_by_email)

@pytest.fixture
def mock_auth_service(monkeypatch):
    # Mock authentication service
    def mock_get_token(request):
        return "valid token"

    def mock_verify_token(token):
        return token == "valid token"

    monkeypatch.setattr("Service.authorization_service.get_token", mock_get_token)
    monkeypatch.setattr("Service.authorization_service.verify_token", mock_verify_token)


@pytest.fixture
def mock_except_service(monkeypatch):
    # Mock a service that raises an exception
    def mock_get_token(request):
        raise Exception("Test Exception")

    monkeypatch.setattr("Service.authorization_service.get_token", mock_get_token)


def test_login_success(mock_user_service, mock_auth_service):
    response = client.post("/login", json={"email": "test@example.com", "password": "testpassword"})
    assert response.status_code == 200
    assert "token" in response.json()
    assert response.json()["token"] == "valid token"
    assert response.json()["message"] == "User logged in successfully"


def test_login_user_not_found(mock_user_service):
    response = client.post("/login", json={"email": "nonexistent@example.com", "password": "testpassword"})
    assert response.status_code == 404
    assert response.json() == {"message": "User not found"}


def test_login_incorrect_password(mock_user_service):
    response = client.post("/login", json={"email": "test@example.com", "password": "wrongpassword"})
    assert response.status_code == 401
    assert response.json() == {"message": "User login failed"}

def test_login_token_already_exists(mock_auth_service):
    response = client.post("/login", json={"email": "test@example.com", "password": "testpassword"})
    assert response.status_code == 302
    assert response.json() == {"message": "Token already exists"}

def test_login_exception_handling(mock_auth_service, mock_except_service):
    response = client.post("/login", json={"email": "test@example.com", "password": "testpassword"})
    assert response.status_code == 409
    assert response.json() == {"message": "There was some error while logging in the user"}
