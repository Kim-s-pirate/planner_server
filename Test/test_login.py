import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
from fastapi.testclient import TestClient
from Controller.main import app
from Service.user_service import user_service, UserNotFoundError
import Router.login as lg
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
"""
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
"""

def temp_get_token_valid(request):
    return "valid token"

def temp_get_token_invalid(request):
    return "invalid token"

def temp_get_token_failed(request):
    return False

def temp_get_token_raise_exception(request):
    raise Exception("Test Exception")

def temp_verify_token(token):
    return token == "valid token"

def temp_generate_token(email):
    return "valid token"

# Need to simplify code
# Need to unify the patcher method and fixture method
def test_login_success(mock_user_service):
    get_token_patcher = patch("Router.login.get_token", temp_get_token_failed)
    generate_token_patcher = patch("Router.login.generate_token", temp_generate_token)
    get_token_patcher.start()
    generate_token_patcher.start()

    try:
        response = client.post("/login", json={"email": "test@example.com", "password": "testpassword"})
        assert response.status_code == 200
        assert response.json()["token"] == "valid token"
        assert response.json()["message"] == "User logged in successfully"
    finally:
        get_token_patcher.stop()
        generate_token_patcher.stop()

def test_login_user_not_found(mock_user_service):
    response = client.post("/login", json={"email": "nonexistent@example.com", "password": "testpassword"})
    assert response.status_code == 404
    assert response.json() == {"message": "User not found"}

def test_login_incorrect_password(mock_user_service):
    response = client.post("/login", json={"email": "test@example.com", "password": "wrongpassword"})
    assert response.status_code == 401
    assert response.json() == {"message": "User login failed"}

def test_login_token_already_exists():
    get_token_patcher = patch("Router.login.get_token", temp_get_token_valid)
    verify_token_patcher = patch("Router.login.verify_token", temp_verify_token)
    get_token_patcher.start()
    verify_token_patcher.start()

    try:
        response = client.post("/login", json={"email": "test@example.com", "password": "testpassword"})
        assert response.status_code == 302
        assert response.json() == {"message": "Token already exists"}
    finally:
        get_token_patcher.stop()
        verify_token_patcher.stop()

def test_login_exception_handling():
    get_token_patcher = patch("Router.login.get_token", temp_get_token_raise_exception)
    get_token_patcher.start()

    try:
        response = client.post("/login", json={"email": "test@example.com", "password": "testpassword"})
        assert response.status_code == 409
        assert response.json() == {"message": "There was some error while logging in the user"}
    finally:
        get_token_patcher.stop()
