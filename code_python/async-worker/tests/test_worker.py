import pytest
import asyncio
from src.worker import JobManager
from src.models import JobStatus
from src.database import get_db

@pytest.mark.asyncio
async def test_worker_processing(test_db):
    manager = JobManager(db_path=test_db)

    # Enqueue a fast job
    job_id = await manager.enqueue_job({"duration": 0.01}) # very fast

    # Start worker in background
    task = asyncio.create_task(manager.worker_loop())

    # Wait for completion (poll DB)
    found = False
    for _ in range(20):
        await asyncio.sleep(0.1)
        async for db in get_db(test_db):
            async with db.execute("SELECT status FROM jobs WHERE id = ?", (job_id,)) as cursor:
                row = await cursor.fetchone()
                if row and row['status'] == JobStatus.COMPLETED:
                    found = True
        if found:
            break

    manager.stop()
    try:
        await asyncio.wait_for(task, timeout=1.0)
    except (asyncio.CancelledError, asyncio.TimeoutError):
        pass

    assert found
