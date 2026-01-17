# Day 02: FastAPI Log Ingestion

A high-performance REST API for ingesting and retrieving logs, built with FastAPI, SQLAlchemy, and Pydantic.

## Features

- **Batch Ingestion**: `POST /ingest` accepts arrays of log records.
- **Strict Validation**: Pydantic V2 schemas ensure data integrity.
- **Persistence**: SQLite database with SQLAlchemy ORM.
- **Pagination**: `GET /logs` supports limit and offset.

## Setup & Run

### Prerequisites

- Python 3.12+

### Installation

```bash
cd code_python/fastapi-log-api
pip install fastapi uvicorn sqlalchemy pydantic
```

### Running the Server

```bash
uvicorn main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.
Interactive documentation is at `http://127.0.0.1:8000/docs`.

## Testing

```bash
pytest tests.py
```
