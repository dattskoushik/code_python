from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import pytest

from src.main import app, get_db
from src.database import Base

# Create in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def run_before_and_after_tests():
    # Setup: create tables
    Base.metadata.create_all(bind=engine)
    yield
    # Teardown: drop tables
    Base.metadata.drop_all(bind=engine)

def test_create_record():
    response = client.post(
        "/records/",
        json={
            "service_name": "payment-service",
            "severity": "INFO",
            "message": "Payment processed successfully",
            "payload": {"amount": 100, "currency": "USD"}
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["service_name"] == "payment-service"
    assert "id" in data
    assert "timestamp" in data

def test_create_record_invalid_severity():
    response = client.post(
        "/records/",
        json={
            "service_name": "payment-service",
            "severity": "INVALID_LEVEL",
            "message": "Something happened",
        },
    )
    assert response.status_code == 422

def test_read_record():
    # Create a record first
    create_response = client.post(
        "/records/",
        json={
            "service_name": "auth-service",
            "severity": "ERROR",
            "message": "Login failed",
        },
    )
    record_id = create_response.json()["id"]

    # Read it back
    response = client.get(f"/records/{record_id}")
    assert response.status_code == 200
    assert response.json()["message"] == "Login failed"

def test_read_nonexistent_record():
    response = client.get("/records/99999")
    assert response.status_code == 404

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
