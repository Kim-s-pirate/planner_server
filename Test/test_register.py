import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch
from Database.database import Base
from Controller.main import app
from Database.models import user
from Service.user_service import user_service

# Configure the test database
TEST_DATABASE_URL = "mysql+mysqlconnector://" + DB_USER + ":" + DB_PASSWORD + "@" + DB_HOST + ":3306/eyJuYW1lIjoidGVzdF9wbGFubmVyIn0"

temp_engine = create_engine(TEST_DATABASE_URL.replace('eyJuYW1lIjoidGVzdF9wbGFubmVyIn0', ''))
with temp_engine.connect() as conn:
    conn.execute(text("CREATE DATABASE IF NOT EXISTS eyJuYW1lIjoidGVzdF9wbGFubmVyIn0"))

test_engine = create_engine(TEST_DATABASE_URL, pool_pre_ping=True)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# Create a new database and tables
def create_test_database():
    with test_engine.connect() as conn:
        conn.execute(text("USE eyJuYW1lIjoidGVzdF9wbGFubmVyIn0"))
        conn.commit()
    Base.metadata.create_all(bind=test_engine)

    # Add initial data
    with TestingSessionLocal() as session:
        initial_user = user(
            email="default@example.com",
            password="defaultpassword",
            userid="defaultuserid",
            username="defaultusername"
        )
        session.add(initial_user)
        session.commit()

def drop_test_database():
    with test_engine.connect() as conn:
        conn.execute(text("DROP DATABASE IF EXISTS eyJuYW1lIjoidGVzdF9wbGFubmVyIn0"))
        conn.commit()

@pytest.fixture(scope="module")
def test_db():
    create_test_database()
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=test_engine)
    drop_test_database()

# `db` 객체를 패치하는 픽스처
@pytest.fixture(scope="module")
def client_with_test_db(test_db):
    with patch("Service.user_service.db", test_db):
        yield TestClient(app)

@pytest.fixture
def mock_user_service(monkeypatch):
    # Mock user_service
    class MockUserService:
        @staticmethod
        def find_user_by_email(email):
            raise Exception("Test Exception")

    monkeypatch.setattr(user_service, "find_user_by_email", MockUserService.find_user_by_email)

def test_register_success(client_with_test_db):
    response = client_with_test_db.post("/register", json={
        "email": "test@example.com",
        "password": "testpassword",
        "userid": "testuserid",
        "username": "testusername"
    })
    assert response.status_code == 201
    assert response.json() == {"message": "User registered successfully"}

def test_register_email_duplicated(client_with_test_db):
    response = client_with_test_db.post("/register", json={
        "email": "default@example.com",
        "password": "testpassword",
        "userid": "testuserid",
        "username": "testusername"
    })
    assert response.status_code == 302
    assert response.json() == {"message": "email duplicated"}

def test_register_userid_duplicated(client_with_test_db):
    response = client_with_test_db.post("/register", json={
        "email": "test@example.com",
        "password": "testpassword",
        "userid": "defaultuserid",
        "username": "testusername"
    })
    assert response.status_code == 302
    assert response.json() == {"message": "userid duplicated"}

def test_register_exception_handling(mock_user_service, client_with_test_db):
    response = client_with_test_db.post("/register", json={
        "email": "test@example.com",
        "password": "testpassword",
        "userid": "testuserid",
        "username": "testusername"
    })
    assert response.status_code == 409
    assert response.json() == {"message": "User registration failed"}
