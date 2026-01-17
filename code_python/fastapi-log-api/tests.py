from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import pytest
import os
from datetime import datetime

from main import app, get_db, Base

# Setup In-Memory DB for testing
# Use StaticPool to maintain the same in-memory database across threads/connections
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Create tables in memory
Base.metadata.create_all(bind=engine)

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_ingest_logs():
    payload = [
        {
            "timestamp": "2023-10-27T10:00:00",
            "severity": "INFO",
            "module": "AUTH",
            "user_id": "U123",
            "action": "LOGIN",
            "message": "User logged in"
        },
        {
            "timestamp": "2023-10-27T10:01:00",
            "severity": "ERROR",
            "module": "DB",
            "message": "Connection failed"
        }
    ]
    response = client.post("/ingest", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert len(data) == 2
    assert data[0]["module"] == "AUTH"
    assert data[1]["severity"] == "ERROR"
    assert "id" in data[0]

def test_read_logs():
    response = client.get("/logs?limit=5")
    assert response.status_code == 200
    data = response.json()
    # Depending on test order, we expect at least the 2 we just added
    assert len(data) >= 2
    # Verify strict sorting (descending timestamp)
    # The default sort in main.py is order_by(LogRecord.timestamp.desc())
    # 10:01:00 should come before 10:00:00
    # timestamps are strings in JSON
    t1 = datetime.fromisoformat(data[0]["timestamp"])
    t2 = datetime.fromisoformat(data[1]["timestamp"])
    assert t1 >= t2

def test_invalid_severity():
    payload = [{
        "timestamp": "2023-10-27T10:00:00",
        "severity": "UNKNOWN_LEVEL",
        "module": "TEST",
        "message": "Fail"
    }]
    response = client.post("/ingest", json=payload)
    assert response.status_code == 422

def test_missing_field():
    payload = [{
        "severity": "INFO",
        "module": "TEST",
        "message": "Fail"
    }]
    # Missing timestamp
    response = client.post("/ingest", json=payload)
    assert response.status_code == 422

if __name__ == "__main__":
    # Manually run tests if executed as script
    try:
        test_health_check()
        test_ingest_logs()
        test_read_logs()
        test_invalid_severity()
        test_missing_field()
        print("All tests passed!")
    except AssertionError as e:
        print(f"Test failed: {e}")
        exit(1)
