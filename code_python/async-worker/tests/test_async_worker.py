import asyncio
import os
import pytest
import pytest_asyncio
from datetime import datetime

from src.db import AsyncJobDB
from src.models import JobCreate, JobStatus
from src.worker import WorkerPool
from src.tasks import execute_task

TEST_DB = "test_jobs.db"

@pytest_asyncio.fixture
async def db():
    # Setup
    database = AsyncJobDB(TEST_DB)
    await database.init_db()
    yield database
    # Teardown
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)

@pytest.mark.asyncio
async def test_create_and_get_job(db):
    payload = {"foo": "bar"}
    job_in = JobCreate(task_type="test_task", payload=payload)
    job = await db.create_job(job_in)

    assert job.id is not None
    assert job.status == JobStatus.PENDING
    assert job.payload == payload

    fetched = await db.get_job(job.id)
    assert fetched.id == job.id
    assert fetched.payload == payload

@pytest.mark.asyncio
async def test_task_execution():
    # Test Math
    res = await execute_task("math_op", {"operation": "add", "a": 1, "b": 2})
    assert res["result"] == 3

    # Test Reverse
    res = await execute_task("text_reverse", {"text": "abc"})
    assert res["result"] == "cba"

@pytest.mark.asyncio
async def test_worker_processing(db):
    queue = asyncio.Queue()
    pool = WorkerPool(db, queue, concurrency=1)
    await pool.start()

    # Create Job
    job = await db.create_job(JobCreate(task_type="math_op", payload={"operation": "multiply", "a": 2, "b": 3}))
    await queue.put(job.id)

    # Wait for processing
    # We can join the queue
    await queue.join()

    # Verify
    updated_job = await db.get_job(job.id)
    assert updated_job.status == JobStatus.COMPLETED
    assert updated_job.result == {"result": 6}

    await pool.stop()

@pytest.mark.asyncio
async def test_worker_failure_handling(db):
    queue = asyncio.Queue()
    pool = WorkerPool(db, queue, concurrency=1)
    await pool.start()

    # Create Job that fails (unknown op)
    job = await db.create_job(JobCreate(task_type="math_op", payload={"operation": "unknown", "a": 1}))
    await queue.put(job.id)

    await queue.join()

    updated_job = await db.get_job(job.id)
    assert updated_job.status == JobStatus.FAILED
    assert "ValueError" in updated_job.error

    await pool.stop()
