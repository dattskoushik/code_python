from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .database import engine, Base, get_db
from .models import Record, RecordCreate, RecordResponse

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for database initialization.
    Ensures tables are created when the application starts.
    """
    # Create database tables
    # In a real production scenario, we would use Alembic for migrations.
    # For this sprint, we initialize them here for simplicity.
    Base.metadata.create_all(bind=engine)
    yield
    # Cleanup if necessary

app = FastAPI(
    title="High-Performance Ingestion API",
    description="A lightweight, high-throughput API for ingesting structured log records.",
    version="1.0.0",
    lifespan=lifespan
)

@app.post("/records/", response_model=RecordResponse, status_code=status.HTTP_201_CREATED)
def create_record(record: RecordCreate, db: Session = Depends(get_db)):
    """
    Ingest a new record into the system.

    - **service_name**: The name of the originating service.
    - **severity**: Log level (INFO, WARN, ERROR, DEBUG, CRITICAL).
    - **message**: The content of the log.
    - **payload**: Optional JSON dictionary with extra context.
    """
    db_record = Record(
        service_name=record.service_name,
        severity=record.severity,
        message=record.message,
        payload=record.payload
    )
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record

@app.get("/records/{record_id}", response_model=RecordResponse)
def read_record(record_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a specific record by ID.
    """
    db_record = db.query(Record).filter(Record.id == record_id).first()
    if db_record is None:
        raise HTTPException(status_code=404, detail="Record not found")
    return db_record

@app.get("/health")
def health_check():
    """
    Health check endpoint to ensure the service is running.
    """
    return {"status": "ok"}
