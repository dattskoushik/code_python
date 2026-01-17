import time
from typing import List
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime, timezone

from models import Base, LogRecord, LogCreate, LogRead

# --- Database Setup ---
SQLALCHEMY_DATABASE_URL = "sqlite:///./logs.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)

# --- FastAPI App ---
app = FastAPI(
    title="Log Ingestion API",
    description="High-performance REST API for log ingestion and persistence.",
    version="1.0.0"
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/ingest", response_model=List[LogRead], status_code=status.HTTP_201_CREATED)
def ingest_logs(logs: List[LogCreate], db: Session = Depends(get_db)):
    """
    Batch ingest log records.

    Accepts a list of log entries, validates them, and persists them to the database.
    Transactional: All logs are saved, or none if an error occurs during commit.
    """
    start_time = time.time()
    db_logs = []

    for log in logs:
        # Use timezone-aware datetime for creation time
        db_log = LogRecord(
            timestamp=log.timestamp,
            severity=log.severity,
            module=log.module,
            user_id=log.user_id,
            action=log.action,
            message=log.message,
            created_at=datetime.now(timezone.utc)
        )
        db_logs.append(db_log)

    try:
        db.add_all(db_logs)
        db.commit()
        # Refresh to get IDs
        for log in db_logs:
            db.refresh(log)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    # Simple metric logging (simulated)
    duration = (time.time() - start_time) * 1000
    print(f"Ingested {len(logs)} logs in {duration:.2f}ms")

    return db_logs

@app.get("/logs", response_model=List[LogRead])
def read_logs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieve logs with pagination.
    """
    logs = db.query(LogRecord).order_by(LogRecord.timestamp.desc()).offset(skip).limit(limit).all()
    return logs

@app.get("/health")
def health_check():
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}
