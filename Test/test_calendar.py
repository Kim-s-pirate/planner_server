import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from Database.database import Base, get_db
from Database.models import user, schedule, calendar_goal
from Controller.main import app  # Assuming the FastAPI app is defined in Controller/main.py
from Data.schedule import day_schedule_register
from Data.calendar import calendar_goal_register
from Service.calendar_service import calendar_service

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

def test_register_schedule_success(client_with_test_db):
    response = client_with_test_db.post("/register_schedule", json={
        "date": "2023-07-21",
        "schedule": [{"title": "Test Event", "start_time": "09:00", "end_time": "10:00"}]
    }, headers={"Authorization": "Bearer validtoken"})
    assert response.status_code == 200
    assert response.json() == {"message": "Schedule registered successfully"}

def test_register_schedule_token_not_found(client_with_test_db):
    response = client_with_test_db.post("/register_schedule", json={
        "date": "2023-07-21",
        "schedule": [{"title": "Test Event", "start_time": "09:00", "end_time": "10:00"}]
    })
    assert response.status_code == 400
    assert response.json() == {"message": "Token not found"}

def test_get_month_schedule_success(client_with_test_db):
    response = client_with_test_db.get("/get_month_schedule", params={"year": "2023", "month": "07"}, headers={"Authorization": "Bearer validtoken"})
    assert response.status_code == 200
    assert "schedule" in response.json()

def test_get_month_schedule_token_not_found(client_with_test_db):
    response = client_with_test_db.get("/get_month_schedule", params={"year": "2023", "month": "07"})
    assert response.status_code == 400
    assert response.json() == {"message": "Token not found"}

def test_register_calendar_goal_success(client_with_test_db):
    response = client_with_test_db.post("/register_calendar_goal", json={
        "year": "2023",
        "month": "07",
        "month_goal": "Read 3 books",
        "week_goal": ["Finish project", "Go hiking"]
    }, headers={"Authorization": "Bearer validtoken"})
    assert response.status_code == 200
    assert response.json() == {"message": "Goal registered successfully"}

def test_register_calendar_goal_token_not_found(client_with_test_db):
    response = client_with_test_db.post("/register_calendar_goal", json={
        "year": "2023",
        "month": "07",
        "month_goal": "Read 3 books",
        "week_goal": ["Finish project", "Go hiking"]
    })
    assert response.status_code == 400
    assert response.json() == {"message": "Token not found"}
