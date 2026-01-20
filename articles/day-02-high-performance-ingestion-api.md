# Day 02: Building a High-Performance Ingestion API with FastAPI

As distributed systems grow, so does the challenge of collecting dispersed data. Whether it's application logs, clickstream data, or IoT sensor readings, we need a reliable entry point into our data infrastructure. Today, we're building a lightweight, high-performance ingestion API using FastAPI.

## The Problem

In a microservices architecture, services are often polyglot and distributed. Centralizing logs or events requires a unified interface. A direct database connection from every service is an anti-pattern (tight coupling, connection exhaustion). We need a buffer or a gateway—a dedicated API that accepts JSON payloads, validates them strictly, and persists them for downstream processing.

The requirements are:
1.  **High Throughput**: It shouldn't slow down the producers.
2.  **Strict Validation**: Garbage in, garbage out. We need to stop bad data at the gate.
3.  **Simplicity**: It should be easy to deploy and maintain.

## The Solution

We'll use **FastAPI** for the web layer, **Pydantic V2** for validation, and **SQLAlchemy** for persistence.

### Why FastAPI?

FastAPI is built on top of Starlette (for the web parts) and Pydantic (for the data parts). It leverages Python's modern `async/await` syntax, making it incredibly fast. But the real killer feature is the automatic data validation and documentation.

### Implementation Highlights

**1. Pydantic Models for Validation**

We define our data schema using Pydantic. This ensures that every incoming record matches our expectations before our code even runs.

```python
class RecordCreate(BaseModel):
    service_name: str = Field(..., min_length=1, max_length=50)
    severity: str = Field(..., pattern="^(INFO|WARN|ERROR|DEBUG|CRITICAL)$")
    message: str = Field(..., min_length=1)
    payload: Optional[Dict[str, Any]] = None
```

With Pydantic V2, validation is implemented in Rust, providing significant performance gains over V1.

**2. SQLAlchemy Session Management**

We use a dependency injection pattern to manage database sessions. This ensures that a new session is created for each request and closed afterwards, preventing connection leaks.

```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**3. Asynchronous Potential**

While our initial implementation uses synchronous SQLite (which is file-based and blocks), FastAPI allows us to easily switch to `asyncpg` or `aiosqlite` if we need to handle thousands of concurrent non-blocking connections.

## Use Cases

1.  **Centralized Logging**: Services send logs to this API instead of writing to local files.
2.  **Audit Trails**: Record critical user actions (login, payment, settings change) for compliance.
3.  **IoT Data Collection**: Edge devices push sensor readings to the cloud via HTTP.

## Next Steps

To make this production-ready, we would:
*   Add authentication (API Keys or JWT).
*   Switch to PostgreSQL or TimescaleDB for better time-series performance.
*   Introduce a message queue (Kafka/RabbitMQ) behind the API to decouple ingestion from processing.

This project lays the foundation for a robust data pipeline.
