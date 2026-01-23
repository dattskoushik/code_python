import aiosqlite
import json
import logging
from datetime import datetime, timezone
from typing import Optional, List

from .models import Job, JobCreate, JobStatus

DB_PATH = "jobs.db"

class AsyncJobDB:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path

    async def init_db(self):
        """Initialize the database table."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS jobs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_type TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    status TEXT NOT NULL,
                    result TEXT,
                    error TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            await db.commit()

    async def create_job(self, job_create: JobCreate) -> Job:
        now = datetime.now(timezone.utc).isoformat()
        payload_json = json.dumps(job_create.payload)

        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """
                INSERT INTO jobs (task_type, payload, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (job_create.task_type, payload_json, JobStatus.PENDING.value, now, now)
            )
            job_id = cursor.lastrowid
            await db.commit()

            return Job(
                id=job_id,
                task_type=job_create.task_type,
                payload=job_create.payload,
                status=JobStatus.PENDING,
                created_at=datetime.fromisoformat(now),
                updated_at=datetime.fromisoformat(now)
            )

    async def get_job(self, job_id: int) -> Optional[Job]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    return self._row_to_job(row)
        return None

    async def update_job_status(self, job_id: int, status: JobStatus, result: Optional[dict] = None, error: Optional[str] = None):
        now = datetime.now(timezone.utc).isoformat()
        result_json = json.dumps(result) if result else None

        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                UPDATE jobs
                SET status = ?, result = ?, error = ?, updated_at = ?
                WHERE id = ?
                """,
                (status.value, result_json, error, now, job_id)
            )
            await db.commit()

    def _row_to_job(self, row: aiosqlite.Row) -> Job:
        return Job(
            id=row['id'],
            task_type=row['task_type'],
            payload=json.loads(row['payload']),
            status=JobStatus(row['status']),
            result=json.loads(row['result']) if row['result'] else None,
            error=row['error'],
            created_at=datetime.fromisoformat(row['created_at']),
            updated_at=datetime.fromisoformat(row['updated_at'])
        )
