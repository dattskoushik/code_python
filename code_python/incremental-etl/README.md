# Day 09: Incremental ETL with Delta Detection

A robust incremental data loading system that uses hashing to identify new, updated, and unchanged records, minimizing unnecessary database writes.

## Features

- **Delta Detection**: Compares incoming data against existing state using SHA256 hashing.
- **Upsert Logic**: Automatically inserts new records and updates changed ones.
- **Validation**: Uses Pydantic to ensure data integrity before processing.
- **Efficiency**: Fetches existing state in bulk to avoid N+1 queries.

## Usage

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Demo**:
   ```bash
   python3 -m src.main
   ```
   This will execute a demonstration script showing:
   - Initial load.
   - Incremental load (inserts, updates, ignores).
   - Error handling.

3. **Run Tests**:
   ```bash
   python3 -m pytest
   ```

## Architecture

- **`src/models.py`**: Pydantic models for input validation and SQLAlchemy models for persistence.
- **`src/storage.py`**: Database interaction layer handling connections and bulk operations.
- **`src/etl.py`**: Core logic for hashing and delta comparison.
