import asyncio
import json
import uuid
import logging
from datetime import datetime, UTC
from pathlib import Path

from .database import get_db, DB_PATH
from .models import JobStatus

logger = logging.getLogger(__name__)


class JobManager:
    def __init__(self, db_path: Path = DB_PATH):
        self.queue = asyncio.Queue()
        self.db_path = db_path
        self.is_running = False

    async def enqueue_job(self, payload: dict) -> str:
        job_id = str(uuid.uuid4())
        payload_json = json.dumps(payload)

        async for db in get_db(self.db_path):
            await db.execute(
                "INSERT INTO jobs (id, status, payload) VALUES (?, ?, ?)",
                (job_id, JobStatus.QUEUED.value, payload_json)
            )
            await db.commit()

        await self.queue.put(job_id)
        logger.info(f"Job {job_id} enqueued")
        return job_id

    async def _process_job(self, job_id: str):
        logger.info(f"Processing job {job_id}")

        # Fetch job details and update status
        payload = None
        async for db in get_db(self.db_path):
            async with db.execute(
                "SELECT payload FROM jobs WHERE id = ?", (job_id,)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    payload = json.loads(row['payload'])

            if payload:
                await db.execute(
                    "UPDATE jobs SET status = ?, "
                    "updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                    (JobStatus.PROCESSING.value, job_id)
                )
                await db.commit()

        if not payload:
            logger.error(f"Job {job_id} not found in DB")
            return

        try:
            # Simulate heavy work
            # Use 'duration' from payload, default to 5 seconds
            duration = payload.get("duration", 5)
            # Cap duration for sanity
            duration = min(duration, 60)

            await asyncio.sleep(duration)

            result = {
                "processed": True,
                "duration": duration,
                "timestamp": datetime.now(UTC).isoformat()
            }

            async for db in get_db(self.db_path):
                await db.execute(
                    "UPDATE jobs SET status = ?, result = ?, "
                    "updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                    (JobStatus.COMPLETED.value, json.dumps(result), job_id)
                )
                await db.commit()
            logger.info(f"Job {job_id} completed")

        except Exception as e:
            logger.error(f"Job {job_id} failed: {e}")
            async for db in get_db(self.db_path):
                await db.execute(
                    "UPDATE jobs SET status = ?, result = ?, "
                    "updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                    (
                        JobStatus.FAILED.value,
                        json.dumps({"error": str(e)}),
                        job_id
                    )
                )
                await db.commit()

    async def worker_loop(self):
        self.is_running = True
        logger.info("Worker started")

        # Recovery: Repopulate queue from DB
        try:
            async for db in get_db(self.db_path):
                # Reset stuck PROCESSING jobs to QUEUED
                await db.execute(
                    "UPDATE jobs SET status = ? WHERE status = ?",
                    (JobStatus.QUEUED.value, JobStatus.PROCESSING.value)
                )
                await db.commit()

                async with db.execute(
                    "SELECT id FROM jobs WHERE status = ?",
                    (JobStatus.QUEUED.value,)
                ) as cursor:
                    async for row in cursor:
                        await self.queue.put(row['id'])
                        logger.info(f"Recovered job {row['id']}")
        except Exception as e:
            logger.error(f"Error during recovery: {e}")

        while self.is_running:
            try:
                # Wait for a job with a timeout to allow checking is_running
                try:
                    job_id = await asyncio.wait_for(
                        self.queue.get(), timeout=1.0
                    )
                    await self._process_job(job_id)
                    self.queue.task_done()
                except asyncio.TimeoutError:
                    continue
            except asyncio.CancelledError:
                logger.info("Worker cancelled")
                break
            except Exception as e:
                logger.error(f"Worker error: {e}")
                await asyncio.sleep(1)

    def stop(self):
        self.is_running = False
