import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from Database.database import Base, get_db
from Controller.main import app  # Assuming the FastAPI app is defined in Controller/main.py
from Data.book import book_register, book_edit
from Service.book_service import book_service
from unittest.mock import patch

# Create a test client
client = TestClient(app)

# Configure the test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override the get_db function to use the test database
@pytest.fixture(scope="module")
def test_db():
    Base.metadata.create_all(bind=engine)  # Create the tables in the test database
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)  # Drop the tables after the test is done

# Dependency override for FastAPI
@pytest.fixture(scope="module")
def client_with_test_db(test_db):
    def override_get_db():
        yield test_db

    app.dependency_overrides[get_db] = override_get_db
    yield client
    app.dependency_overrides.clear()

# Mock authentication service
@pytest.fixture(autouse=True)
def mock_auth_service():
    with patch("Service.authorization_service.authenticate_user") as mock_auth:
        mock_auth.return_value = {"userid": "test_user"}
        yield mock_auth

# Test cases
def test_book_register_success(client_with_test_db):
    response = client_with_test_db.post("/book_register", json={
        "title": "Test Book",
        "author": "Author Name",
        "description": "Description",
        "status": True
    }, headers={"Authorization": "Bearer validtoken"})
    assert response.status_code == 201
    assert response.json() == {"message": "Book registered successfully"}

def test_book_register_token_not_found(client_with_test_db, mock_auth_service):
    mock_auth_service.side_effect = TokenNotFoundError()
    response = client_with_test_db.post("/book_register", json={
        "title": "Test Book",
        "author": "Author Name",
        "description": "Description",
        "status": True
    })
    assert response.status_code == 400
    assert response.json() == {"message": "Token not found"}

def test_book_info_success(client_with_test_db):
    response = client_with_test_db.get("/book/1", headers={"Authorization": "Bearer validtoken"})
    assert response.status_code == 200
    assert "book" in response.json()

def test_book_info_token_not_found(client_with_test_db, mock_auth_service):
    mock_auth_service.side_effect = TokenNotFoundError()
    response = client_with_test_db.get("/book/1")
    assert response.status_code == 400
    assert response.json() == {"message": "Token not found"}

def test_book_list_success(client_with_test_db):
    response = client_with_test_db.get("/book_list", headers={"Authorization": "Bearer validtoken"})
    assert response.status_code == 200
    assert "books" in response.json()

def test_book_list_token_not_found(client_with_test_db, mock_auth_service):
    mock_auth_service.side_effect = TokenNotFoundError()
    response = client_with_test_db.get("/book_list")
    assert response.status_code == 400
    assert response.json() == {"message": "Token not found"}

def test_book_delete_success(client_with_test_db):
    response = client_with_test_db.delete("/book_delete/Test Book", headers={"Authorization": "Bearer validtoken"})
    assert response.status_code == 200
    assert response.json() == {"message": "Book deleted successfully"}

def test_book_delete_token_not_found(client_with_test_db, mock_auth_service):
    mock_auth_service.side_effect = TokenNotFoundError()
    response = client_with_test_db.delete("/book_delete/Test Book")
    assert response.status_code == 400
    assert response.json() == {"message": "Token not found"}

def test_active_book_list_success(client_with_test_db):
    response = client_with_test_db.get("/active_book_list", headers={"Authorization": "Bearer validtoken"})
    assert response.status_code == 200
    assert "books" in response.json()

def test_active_book_list_token_not_found(client_with_test_db, mock_auth_service):
    mock_auth_service.side_effect = TokenNotFoundError()
    response = client_with_test_db.get("/active_book_list")
    assert response.status_code == 400
    assert response.json() == {"message": "Token not found"}

def test_inactive_book_list_success(client_with_test_db):
    response = client_with_test_db.get("/inactive_book_list", headers={"Authorization": "Bearer validtoken"})
    assert response.status_code == 200
    assert "books" in response.json()

def test_inactive_book_list_token_not_found(client_with_test_db, mock_auth_service):
    mock_auth_service.side_effect = TokenNotFoundError()
    response = client_with_test_db.get("/inactive_book_list")
    assert response.status_code == 400
    assert response.json() == {"message": "Token not found"}

def test_edit_book_success(client_with_test_db):
    response = client_with_test_db.post("/edit_book/Test Book", json={
        "title": "New Title",
        "author": "New Author",
        "description": "New Description",
        "status": True
    }, headers={"Authorization": "Bearer validtoken"})
    assert response.status_code == 200
    assert response.json() == {"message": "Book edited successfully"}

def test_edit_book_token_not_found(client_with_test_db, mock_auth_service):
    mock_auth_service.side_effect = TokenNotFoundError()
    response = client_with_test_db.post("/edit_book/Test Book", json={
        "title": "New Title",
        "author": "New Author",
        "description": "New Description",
        "status": True
    })
    assert response.status_code == 400
    assert response.json() == {"message": "Token not found"}
