import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.main import app
from src.database import Base, get_db
from src.models import Employee

# Setup in-memory SQLite for testing
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
def run_around_tests():
    Base.metadata.create_all(bind=engine)
    # Seed data
    db = TestingSessionLocal()
    employees = [
        Employee(full_name="Alice Test", department="Engineering", salary=100000, is_active=True),
        Employee(full_name="Bob Test", department="Sales", salary=50000, is_active=True),
        Employee(full_name="Charlie Test", department="Engineering", salary=80000, is_active=False),
    ]
    db.add_all(employees)
    db.commit()
    db.close()

    yield

    Base.metadata.drop_all(bind=engine)

def test_pagination():
    response = client.get("/employees?page=1&page_size=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 2
    assert data["total"] == 3
    assert data["total_pages"] == 2

    response = client.get("/employees?page=2&page_size=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1

def test_filtering():
    # Filter by department
    response = client.get("/employees?department=Engineering")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 2
    assert all(item["department"] == "Engineering" for item in data["items"])

    # Filter by salary > 60000
    response = client.get("/employees?salary__gt=60000")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 2 # Alice and Charlie

    # Filter by active status
    response = client.get("/employees?is_active=false")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["full_name"] == "Charlie Test"

def test_sorting():
    # Sort by salary desc
    response = client.get("/employees?sort_by=salary&order=desc")
    assert response.status_code == 200
    data = response.json()
    salaries = [item["salary"] for item in data["items"]]
    assert salaries == [100000.0, 80000.0, 50000.0]

    # Sort by salary asc
    response = client.get("/employees?sort_by=salary&order=asc")
    assert response.status_code == 200
    data = response.json()
    salaries = [item["salary"] for item in data["items"]]
    assert salaries == [50000.0, 80000.0, 100000.0]

def test_invalid_sorting_field():
    response = client.get("/employees?sort_by=invalid_field")
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid sort field: invalid_field"
