# Day 09: Building an Incremental ETL Pipeline with Delta Detection

In the world of data engineering, the most expensive operation is often the movement of data itself. Naively truncating and reloading tables or processing every single record regardless of its state is a recipe for latency and resource exhaustion. Today, I tackled this problem by building a robust **Incremental ETL** pipeline in Python that intelligently detects and applies only necessary changes.

## The Problem: The Cost of Redundancy

Traditional "Full Load" strategies are simple but inefficient. As datasets grow from thousands to millions of rows, re-processing unchanged data becomes unsustainable. The challenge is to identify *what* changed (Inserts, Updates, Deletes) without fetching the entire destination dataset into memory or putting excessive load on the database.

## The Solution: Lightweight Delta Detection

My approach relies on a **Deterministic Hashing Strategy**. By computing a hash (e.g., SHA-256) of the incoming row's data and storing it alongside the record in the destination, we can perform a lightweight comparison.

### Architecture

1.  **Extract**: Pull raw data from the source (simulated here as a list of Pydantic models).
2.  **Map**: Fetch a lightweight map of `{Primary Key: Row Hash}` from the destination. This avoids pulling full row content.
3.  **Detect**: Iterate through source records:
    *   **Insert**: ID not in map.
    *   **Update**: ID in map, but calculated hash differs.
    *   **Ignore**: ID in map, hash matches.
4.  **Load**: Use bulk operations to apply changes efficiently.

## Implementation Highlights

### 1. Deterministic Hashing with Pydantic

Using Pydantic's `model_dump_json()` ensures that we serialize our data consistently before hashing.

```python
def compute_row_hash(record: ProductSource) -> str:
    # serializing with strict ordering is crucial
    record_json = record.model_dump_json()
    return hashlib.sha256(record_json.encode('utf-8')).hexdigest()
```

### 2. SQLAlchemy 2.0 Bulk Updates

One of the cleanest features in SQLAlchemy 2.0 is the ability to pass a list of dictionaries to `session.execute(update(Model))`. This allows for high-performance bulk updates without manually constructing complex SQL case statements.

```python
if to_update:
    session.execute(update(ProductModel), to_update)
```

This method is significantly faster than iterating through ORM objects and updating attributes one by one.

## Results

Running the pipeline against a simulated dataset demonstrated the efficiency of this pattern:

*   **Initial Load**: Processed and inserted all records.
*   **Incremental Run**: Correctly identified 1 new record, 2 modified records, and ignored the rest.
*   **Idempotency**: A subsequent run resulted in zero database operations, proving the system is stable and efficient.

## Key Takeaways

*   **Fail Fast, process less**: The earlier you filter out unchanged data, the faster your pipeline runs.
*   **Hashing is cheap**: CPU cycles for hashing are far cheaper than I/O bandwidth.
*   **Bulk over Iteration**: Always prefer set-based operations for database writes.

---
*Author: dattskoushik*
*Date: Day 09 of 30*
