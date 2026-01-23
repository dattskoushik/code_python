import asyncio
import logging
from contextlib import asynccontextmanager
import json
from datetime import datetime, UTC

from fastapi import FastAPI, Depends, HTTPException
from aiosqlite import Connection

from .database import init_db, get_db
from .models import JobCreate, JobResponse, JobStatus
from .worker import JobManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

job_manager = JobManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Initializing database...")
    await init_db()
    logger.info("Starting worker...")
    worker_task = asyncio.create_task(job_manager.worker_loop())
    yield
    # Shutdown
    logger.info("Stopping worker...")
    job_manager.stop()
    try:
        await worker_task
    except asyncio.CancelledError:
        pass
    logger.info("Worker stopped.")


app = FastAPI(title="Async Job Processor", lifespan=lifespan)


@app.post("/jobs", response_model=JobResponse, status_code=201)
async def create_job(job_data: JobCreate):
    job_id = await job_manager.enqueue_job(job_data.payload)
    now = datetime.now(UTC)
    return JobResponse(
        id=job_id,
        status=JobStatus.QUEUED,
        payload=job_data.payload,
        created_at=now,
        updated_at=now
    )


@app.get("/jobs/{job_id}", response_model=JobResponse)
async def get_job(job_id: str, db: Connection = Depends(get_db)):
    # Iterate over the async generator to get the connection
    # Note: Depends(get_db) with yield will provide the yielded value.
    # FastAPI handles the async generator context.

    async with db.execute(
        "SELECT * FROM jobs WHERE id = ?", (job_id,)
    ) as cursor:
        row = await cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Job not found")

        result = json.loads(row['result']) if row['result'] else None
        payload = json.loads(row['payload']) if row['payload'] else {}

        # Helper to parse SQLite timestamp if needed
        # or let Pydantic handle it
        return JobResponse(
            id=row['id'],
            status=row['status'],
            payload=payload,
            result=result,
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )
