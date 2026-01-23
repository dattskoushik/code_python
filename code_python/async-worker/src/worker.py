import asyncio
import logging
import traceback
from typing import List

from .db import AsyncJobDB
from .models import JobStatus
from .tasks import execute_task

logger = logging.getLogger(__name__)

class WorkerPool:
    def __init__(self, db: AsyncJobDB, queue: asyncio.Queue, concurrency: int = 3):
        self.db = db
        self.queue = queue
        self.concurrency = concurrency
        self.workers: List[asyncio.Task] = []
        self.stop_event = asyncio.Event()

    async def start(self):
        """Starts the worker pool."""
        logger.info(f"Starting worker pool with {self.concurrency} workers.")
        for i in range(self.concurrency):
            task = asyncio.create_task(self.worker_loop(i))
            self.workers.append(task)

    async def stop(self):
        """Stops the worker pool gracefully."""
        logger.info("Stopping worker pool...")
        self.stop_event.set()
        # Wait for workers to finish current task (or until they notice stop_event)
        # We can push None to queue to unblock workers waiting on get()
        for _ in range(self.concurrency):
            await self.queue.put(None)

        await asyncio.gather(*self.workers, return_exceptions=True)
        logger.info("Worker pool stopped.")

    async def worker_loop(self, worker_id: int):
        """Main loop for a single worker."""
        logger.info(f"Worker {worker_id} started.")
        while not self.stop_event.is_set():
            try:
                job_id = await self.queue.get()

                if job_id is None:
                    self.queue.task_done()
                    break

                await self.process_job(worker_id, job_id)
                self.queue.task_done()
            except Exception as e:
                logger.error(f"Worker {worker_id} encountered critical error: {e}")

    async def process_job(self, worker_id: int, job_id: int):
        """Processes a single job."""
        try:
            # 1. Fetch Job
            job = await self.db.get_job(job_id)
            if not job:
                logger.warning(f"Worker {worker_id}: Job {job_id} not found in DB.")
                return

            if job.status != JobStatus.PENDING:
                logger.warning(f"Worker {worker_id}: Job {job_id} is not PENDING (status: {job.status}). Skipping.")
                return

            logger.info(f"Worker {worker_id}: Processing Job {job_id} ({job.task_type})")

            # 2. Update Status to PROCESSING
            await self.db.update_job_status(job_id, JobStatus.PROCESSING)

            # 3. Execute Task
            try:
                result = await execute_task(job.task_type, job.payload)
                await self.db.update_job_status(job_id, JobStatus.COMPLETED, result=result)
                logger.info(f"Worker {worker_id}: Job {job_id} COMPLETED.")
            except Exception as e:
                logger.error(f"Worker {worker_id}: Job {job_id} FAILED: {e}")
                error_msg = f"{type(e).__name__}: {str(e)}"
                await self.db.update_job_status(job_id, JobStatus.FAILED, error=error_msg)

        except Exception as e:
            logger.error(f"Worker {worker_id}: Failed to process job {job_id} wrapper: {e}")
            # Try to fail the job in DB if possible
            try:
                await self.db.update_job_status(job_id, JobStatus.FAILED, error="System Error during processing")
            except:
                pass
