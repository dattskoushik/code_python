import pytest
from httpx import AsyncClient, ASGITransport
from src.main import app
from src.models import JobStatus
from src.database import get_db
import src.main

@pytest.mark.asyncio
async def test_create_job(test_db, override_get_db):
    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/jobs", json={"payload": {"duration": 0.1}})

    assert response.status_code == 201
    data = response.json()
    assert data["status"] == JobStatus.QUEUED
    assert "id" in data

@pytest.mark.asyncio
async def test_get_job_status(test_db, override_get_db):
    app.dependency_overrides[get_db] = override_get_db

    # Create job
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        create_res = await ac.post("/jobs", json={"payload": {"duration": 0.1}})
        job_id = create_res.json()["id"]

        # Get status
        get_res = await ac.get(f"/jobs/{job_id}")
        assert get_res.status_code == 200
        assert get_res.json()["id"] == job_id
