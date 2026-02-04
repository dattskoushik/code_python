# Building an Incremental ETL Pipeline with Python and Delta Detection

Data pipelines often start simple: truncate the destination table and reload everything. This "Full Refresh" strategy works when you have 1,000 rows. It fails catastrophically when you have 100 million. On **Day 09** of my 30-day technical sprint, I built a robust **Incremental ETL (Extract, Transform, Load)** system that uses cryptographic hashing to detect deltas and apply efficient updates.

## The Problem: The "Full Refresh" Bottleneck

Reloading your entire dataset every night is wasteful and risky.
1.  **Latency**: Processing 10GB of data to update 5MB of changes takes hours.
2.  **Downtime**: Truncate-and-load often leaves tables empty or locked during the process.
3.  **Cost**: Cloud warehouses (Snowflake, BigQuery) charge by the compute unit. Processing unchanged data burns money.

The challenge is to identify *exactly* what changed without scanning the entire history of every row row-by-row in the database.

## The Solution: Row-Level Fingerprinting

I implemented a "Delta Detection" engine that uses SHA256 hashing to compare incoming source data against the current state of the database.

### 1. The Hashing Strategy
Instead of comparing every column (`if new.name != old.name or new.email != old.email ...`), I compute a single deterministic hash of the business value columns.

```python
def compute_hash(record: Dict[str, Any]) -> str:
    # Exclude ID (key) and sort keys for determinism
    payload = {k: v for k, v in record.items() if k != 'id'}
    encoded = json.dumps(payload, sort_keys=True, default=str).encode('utf-8')
    return hashlib.sha256(encoded).hexdigest()
```

By storing this hash alongside the record in the database, the comparison becomes an O(1) lookup.

### 2. State-Based Comparison
To maximize performance, I pull the existing state (IDs and Hashes) into memory. This avoids the "N+1 Select" problem where you query the DB for every single incoming row.

```python
# Fetch current state: {id: hash}
current_state = storage.get_current_state()

for row in source_data:
    row_hash = compute_hash(row)
    pk = row['id']

    if pk not in current_state:
        inserts.append(row)
    elif current_state[pk] != row_hash:
        updates.append(row)
    # else: Unchanged, do nothing
```

### 3. Bulk Operations
Once the deltas are identified, I use SQLAlchemy's bulk execution methods (`execute(insert(...))` and `execute(update(...))`) to apply changes in batches. This reduces network round-trips significantly compared to saving objects one by one.

## Use Cases

1.  **Customer Data Sync**: Syncing CRM data (Salesforce) to a data warehouse where only 1% of records change daily.
2.  **Configuration Management**: Detecting changes in infrastructure configuration files to trigger deployments.
3.  **Audit Logs**: Tracking exactly *when* a record changed by updating an `updated_at` timestamp only when the hash changes.

## Conclusion

Incremental ETL isn't just about speed; it's about correctness and resource responsibility. By moving the comparison logic to a calculated hash, we decouple the schema complexity from the change detection logic, resulting in a cleaner, faster, and more maintainable pipeline.
