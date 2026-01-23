# Day 04: Building a Resilient Async Processing System with Python

## The Problem

In high-throughput web applications, blocking the main thread for long-running tasks is a recipe for disaster. Operations like generating complex PDF reports, resizing high-resolution images, or sending bulk emails can take seconds or even minutes. If you handle these synchronously within a request-response cycle, your API becomes unresponsive, leaving users waiting and potentially causing timeouts at the load balancer level.

## The Solution

To maintain a responsive user interface while handling heavy workloads, we need to offload these tasks to a background process. The **Async Worker Pattern** decouples the task submission from its execution.

For this project, I implemented a custom asynchronous worker system using Python's `asyncio` library and `aiosqlite`. Instead of introducing heavy external dependencies like Redis and Celery (which are excellent but sometimes overkill for smaller services), I built a lightweight, self-contained job queue backed by SQLite.

## Implementation Details

The system consists of three main components:

1.  **Job Manager & Queue**: A robust `JobManager` class that maintains an in-memory `asyncio.Queue` for immediate processing and persists job states to an SQLite database for reliability.
2.  **The Worker Loop**: A continuously running background task that pulls jobs from the queue, processes them, and updates their status (Queued -> Processing -> Completed/Failed).
3.  **FastAPI Integration**: A REST API that accepts job submissions, returns a tracking ID immediately, and allows clients to poll for status updates.

### Key Features

*   **Persistence**: All jobs are saved to disk. If the application crashes, the worker checks the database on startup and "recovers" any jobs that were still in the `QUEUED` state, adding them back to the memory queue.
*   **Non-blocking**: The entire stack is async, from the API layer to the database interactions, ensuring high concurrency.
*   **Error Handling**: Failed jobs are caught, logged, and marked as `FAILED` in the database with the error message, preventing the worker from crashing.

### Code Highlight: The Worker Loop

```python
    async def worker_loop(self):
        self.is_running = True
        logger.info("Worker started")

        # Recovery phase
        await self._recover_jobs()

        while self.is_running:
            try:
                job_id = await self.queue.get()
                await self._process_job(job_id)
                self.queue.task_done()
            except Exception as e:
                logger.error(f"Worker error: {e}")
```

## Use Cases

This architecture is ideal for:
*   **Data Ingestion**: Processing large uploaded CSV files row-by-row.
*   **Media Processing**: Resizing user avatars or compressing videos.
*   **Third-party Integrations**: Webhooks or API calls to slow external services.

By leveraging `asyncio`, we achieve a high degree of performance and responsiveness with minimal resource overhead.
