import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from Database.database import Base
from Database.models import user, subject
from Controller.main import app  # Assuming the FastAPI app is defined in Controller/main.py
from Data.subject import subject_register
from Service.subject_service import subject_service

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

def test_subject_register_success(client_with_test_db):
    response = client_with_test_db.post("/subject_register", json={
        "name": "Math"
    }, headers={"Authorization": "Bearer validtoken"})
    assert response.status_code == 201
    assert response.json() == {"message": "Subject registered successfully"}

def test_subject_register_token_not_found(client_with_test_db):
    response = client_with_test_db.post("/subject_register", json={
        "name": "Math"
    })
    assert response.status_code == 400
    assert response.json() == {"message": "Token not found"}

def test_delete_subject_success(client_with_test_db):
    response = client_with_test_db.delete("/delete_subject/Math", headers={"Authorization": "Bearer validtoken"})
    assert response.status_code == 200
    assert response.json() == {"message": "Subject deleted successfully"}

def test_delete_subject_not_found(client_with_test_db):
    response = client_with_test_db.delete("/delete_subject/NonExistentSubject", headers={"Authorization": "Bearer validtoken"})
    assert response.status_code == 404
    assert response.json() == {"message": "Subject not found"}

def test_delete_subject_unauthorized(client_with_test_db):
    response = client_with_test_db.delete("/delete_subject/Math", headers={"Authorization": "Bearer invalidtoken"})
    assert response.status_code == 401
    assert response.json() == {"message": "You are not authorized to delete this subject"}

def test_get_subject_success(client_with_test_db):
    response = client_with_test_db.get("/subject/Math", headers={"Authorization": "Bearer validtoken"})
    assert response.status_code == 200
    assert response.json() == {"message": "Subject retrieved successfully"}

def test_get_subject_not_found(client_with_test_db):
    response = client_with_test_db.get("/subject/NonExistentSubject", headers={"Authorization": "Bearer validtoken"})
    assert response.status_code == 404
    assert response.json() == {"message": "Subject not found"}

def test_edit_subject_success(client_with_test_db):
    response = client_with_test_db.get("/edit_subject/Math", params={"new_subject": "Advanced Math"}, headers={"Authorization": "Bearer validtoken"})
    assert response.status_code == 200
    assert response.json() == {"message": "Subject edited successfully"}

def test_edit_subject_not_found(client_with_test_db):
    response = client_with_test_db.get("/edit_subject/NonExistentSubject", params={"new_subject": "Advanced Math"}, headers={"Authorization": "Bearer validtoken"})
    assert response.status_code == 404
    assert response.json() == {"message": "Subject not found"}

def test_edit_subject_unauthorized(client_with_test_db):
    response = client_with_test_db.get("/edit_subject/Math", params={"new_subject": "Advanced Math"}, headers={"Authorization": "Bearer invalidtoken"})
    assert response.status_code == 401
    assert response.json() == {"message": "You are not authorized to edit this subject"}
