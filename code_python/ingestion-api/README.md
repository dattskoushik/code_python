# High-Performance Ingestion API

This project implements a high-throughput REST API for ingesting structured log records, built with FastAPI and SQLAlchemy. It is Day 02 of the 30-Day Python Mini-Project Track.

## Features

*   **FastAPI**: High performance, easy to use, and automatic interactive documentation.
*   **SQLAlchemy**: Robust ORM for database interaction.
*   **Pydantic V2**: Modern data validation and serialization.
*   **SQLite**: Lightweight, file-based database for persistence.
*   **Testing**: Full test coverage with Pytest.

## Setup

1.  **Navigate to the project directory**:
    ```bash
    cd code_python/ingestion-api
    ```

2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1.  **Run the application**:
    ```bash
    python3 -m uvicorn src.main:app --reload
    ```
    The API will be available at `http://127.0.0.1:8000`.

2.  **Access Documentation**:
    Open `http://127.0.0.1:8000/docs` to see the interactive API documentation (Swagger UI).

## Endpoints

*   `POST /records/`: Ingest a new log record.
    *   Body:
        ```json
        {
          "service_name": "payment-service",
          "severity": "INFO",
          "message": "Transaction completed",
          "payload": {"transaction_id": "12345", "amount": 50.0}
        }
        ```
*   `GET /records/{id}`: Retrieve a record by ID.
*   `GET /health`: Health check endpoint.

## Testing

Run the test suite with:
```bash
pytest
```
