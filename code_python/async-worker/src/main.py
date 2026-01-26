import asyncio
import logging
import random
import aiosqlite
from datetime import datetime

from .db import AsyncJobDB
from .models import JobCreate, JobStatus
from .worker import WorkerPool

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("AsyncETL")

DB_PATH = "jobs.db"

async def produce_jobs(db: AsyncJobDB, queue: asyncio.Queue, count: int = 10):
    """Simulates a producer creating jobs."""
    task_types = [
        ("math_op", {"operation": "add", "a": 10, "b": 20}),
        ("math_op", {"operation": "multiply", "a": 5, "b": 5}),
        ("text_reverse", {"text": "Asyncio is powerful"}),
        ("text_reverse", {"text": "Data Engineering"}),
        ("mock_api_fetch", {"url": "https://api.example.com/data/1"}),
        ("mock_api_fetch", {"url": "https://api.example.com/users/5"}),
        ("math_op", {"operation": "divide", "a": 10, "b": 0}), # Should fail
    ]

    for i in range(count):
        task_name, payload = random.choice(task_types)
        # Add some randomness to payload to make it unique
        if "a" in payload:
            payload = payload.copy()
            payload["a"] = random.randint(1, 100)

        job_in = JobCreate(task_type=task_name, payload=payload)
        job = await db.create_job(job_in)
        logger.info(f"Producer: Created Job {job.id} ({task_name})")
        await queue.put(job.id)
        await asyncio.sleep(0.2) # Simulate incoming request rate

async def main():
    logger.info("Starting Async Data Processing Worker Demo")

    db = AsyncJobDB(DB_PATH)
    await db.init_db()

    queue = asyncio.Queue()
    worker_pool = WorkerPool(db, queue, concurrency=4)

    try:
        await worker_pool.start()

        job_count = 10
        producer_task = asyncio.create_task(produce_jobs(db, queue, count=job_count))

        # We wait for producer to finish
        await producer_task

        # Wait for queue to be empty (workers processed everything)
        await queue.join()

        logger.info("Queue empty. Fetching final results...")

        # Print Summary
        async with aiosqlite.connect(DB_PATH) as conn:
            async with conn.execute("SELECT id, task_type, status, result, error FROM jobs ORDER BY id DESC LIMIT ?", (job_count,)) as cursor:
                rows = await cursor.fetchall()
                print("\n--- Processing Report (Last 10 Jobs) ---")
                print(f"{'ID':<5} {'Type':<15} {'Status':<12} {'Result/Error'}")
                print("-" * 60)
                for row in reversed(rows):
                    res = row[3] if row[3] else row[4]
                    print(f"{row[0]:<5} {row[1]:<15} {row[2]:<12} {str(res)[:50]}")
                print("-" * 60)

    except KeyboardInterrupt:
        logger.info("Interrupted by user.")
    finally:
        await worker_pool.stop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
