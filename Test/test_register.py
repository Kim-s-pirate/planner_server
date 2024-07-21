import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from Database.database import Base, get_db
from Database.models import user
from Controller.main import app  # Assuming the FastAPI app is defined in Controller/main.py
from Data.user import user_register, user_edit
from Service.user_service import user_service

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

# Test cases

def test_register_success(client_with_test_db):
    response = client_with_test_db.post("/register", json={
        "email": "test@example.com",
        "password": "testpassword",
        "userid": "testuser",
        "username": "testusername"
    })
    assert response.status_code == 201
    assert response.json() == {"message": "User registered successfully"}

def test_register_email_duplicated(client_with_test_db):
    # First, register the user
    client_with_test_db.post("/register", json={
        "email": "duplicate@example.com",
        "password": "testpassword",
        "userid": "uniqueuserid",
        "username": "uniqueusername"
    })
    # Try to register the same email again
    response = client_with_test_db.post("/register", json={
        "email": "duplicate@example.com",
        "password": "testpassword",
        "userid": "newuserid",
        "username": "newusername"
    })
    assert response.status_code == 302
    assert response.json() == {"message": "email duplicated"}

def test_register_userid_duplicated(client_with_test_db):
    # First, register the user
    client_with_test_db.post("/register", json={
        "email": "uniqueemail@example.com",
        "password": "testpassword",
        "userid": "duplicateuserid",
        "username": "uniqueusername"
    })
    # Try to register the same userid again
    response = client_with_test_db.post("/register", json={
        "email": "newemail@example.com",
        "password": "testpassword",
        "userid": "duplicateuserid",
        "username": "newusername"
    })
    assert response.status_code == 302
    assert response.json() == {"message": "userid duplicated"}

def test_duplicate_id_user_not_found(client_with_test_db):
    response = client_with_test_db.get("/duplicate_id", params={"userid": "nonexistentuser"})
    assert response.status_code == 200
    assert response.json() == {"message": "User not found"}

def test_duplicate_id_user_exists(client_with_test_db):
    client_with_test_db.post("/register", json={
        "email": "testuser@example.com",
        "password": "testpassword",
        "userid": "existinguser",
        "username": "testusername"
    })
    response = client_with_test_db.get("/duplicate_id", params={"userid": "existinguser"})
    assert response.status_code == 302
    assert response.json() == {"message": "User already exists"}

def test_duplicate_email_user_not_found(client_with_test_db):
    response = client_with_test_db.get("/duplicate_email", params={"email": "nonexistent@example.com"})
    assert response.status_code == 200
    assert response.json() == {"message": "User not found"}

def test_duplicate_email_user_exists(client_with_test_db):
    client_with_test_db.post("/register", json={
        "email": "existingemail@example.com",
        "password": "testpassword",
        "userid": "uniqueuserid",
        "username": "testusername"
    })
    response = client_with_test_db.get("/duplicate_email", params={"email": "existingemail@example.com"})
    assert response.status_code == 302
    assert response.json() == {"message": "User already exists"}

def test_user_delete_unauthorized(client_with_test_db):
    # Register a user
    client_with_test_db.post("/register", json={
        "email": "deleteuser@example.com",
        "password": "testpassword",
        "userid": "deleteuserid",
        "username": "testusername"
    })
    # Try to delete the user without proper authorization
    response = client_with_test_db.delete("/user_delete/deleteuserid")
    assert response.status_code == 401
    assert response.json() == {"message": "You are not authorized to delete this user"}

def test_user_delete_authorized(client_with_test_db):
    # Register a user
    client_with_test_db.post("/register", json={
        "email": "authorized@example.com",
        "password": "testpassword",
        "userid": "authorizeduser",
        "username": "testusername"
    })
    # Assume a token function for authorized deletion
    # Normally you would implement the token authentication in the tests
    response = client_with_test_db.delete("/user_delete/authorizeduser", headers={"Authorization": "Bearer validtoken"})
    assert response.status_code == 200
    assert response.json() == {"message": "User deleted successfully"}

def test_test_rollback(client_with_test_db):
    response = client_with_test_db.get("/test")
    assert response.status_code == 200
    assert response.json() == {"message": "Temporary user rolled back successfully"}

def test_edit_user_unauthorized(client_with_test_db):
    response = client_with_test_db.post("/edit_user/testuser", json={
        "email": "edit@example.com",
        "password": "newpassword",
        "userid": "edituserid",
        "username": "editusername"
    })
    assert response.status_code == 401
    assert response.json() == {"message": "You are not authorized to edit this user"}

def test_edit_user_authorized(client_with_test_db):
    # Register a user
    client_with_test_db.post("/register", json={
        "email": "edit@example.com",
        "password": "testpassword",
        "userid": "edituserid",
        "username": "editusername"
    })
    # Assume a token function for authorized edit
    # Normally you would implement the token authentication in the tests
    response = client_with_test_db.post("/edit_user/edituserid", json={
        "email": "newedit@example.com",
        "password": "newpassword",
        "userid": "newedituserid",
        "username": "neweditusername"
    }, headers={"Authorization": "Bearer validtoken"})
    assert response.status_code == 200
    assert response.json() == {"message": "User edited successfully"}