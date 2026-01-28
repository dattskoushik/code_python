# Day 01: Building a Robust Log Parser

## The Problem
In distributed systems, logs are often the first line of defense for observability. However, logs are frequently generated in unstructured or semi-structured formats that are difficult to query programmatically. A simple `grep` is insufficient when dealing with millions of lines containing complex metadata like trace IDs, timestamps, and severity levels. Without a structured format, automated analysis, alerting, and metrics generation become impossible tasks. The challenge lies in converting these raw string streams into strongly-typed, validatable objects that downstream systems (like ELK stacks or data warehouses) can ingest reliably.

## The Solution
For Day 1 of my 30-day technical sprint, I implemented a modular Log Parser in Python. The core design philosophy centers on **strict validation**, **extensibility**, and **detailed error reporting**.

### 1. Regex-Driven Extraction
I utilized Python's `re` module to define a strict grammar for log lines. The pattern expects a specific structure: `[TIMESTAMP] [LEVEL] [TRACE_ID] MESSAGE`.

```python
LOG_PATTERN = re.compile(
    r"^\[(?P<timestamp>.*?)\] \[(?P<level>.*?)\] \[(?P<trace_id>.*?)\] (?P<message>.*)$"
)
```

### 2. Pydantic for Schema Validation
Extraction is only half the battle; validation is where data integrity is enforced. I leveraged **Pydantic V2** to define a `LogEntry` model.

```python
class LogEntry(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    timestamp: datetime
    level: LogLevel
    trace_id: str = Field(..., pattern=r"^[a-f0-9\-]+$")
    message: str
```

- **Enums for Log Levels:** Ensures only valid levels (INFO, ERROR, WARN, DEBUG) are processed.
- **DateTime Parsing:** Automatically converts ISO 8601 strings into Python `datetime` objects.
- **Field Validation:** `trace_id` is validated against a regex pattern to ensure it matches the expected hex/hyphen format.

### 3. Structured Output with Error Aggregation
Instead of failing silently on bad lines, the parser returns a comprehensive JSON structure containing metadata, successfully parsed logs, and detailed errors for malformed lines.

```json
{
  "metadata": {
    "timestamp": "2023-10-27T12:00:00+00:00",
    "total_processed": 100,
    "valid_count": 98,
    "error_count": 2
  },
  "logs": [
    {
      "timestamp": "2023-10-27T10:00:00+00:00",
      "level": "INFO",
      "trace_id": "abc-123",
      "message": "System started."
    }
  ],
  "errors": [
    {
      "line_number": 42,
      "raw_content": "Invalid Line...",
      "error": "Regex mismatch. Invalid format."
    }
  ]
}
```

This approach ensures that "garbage in" doesn't break the pipeline, but is instead flagged for investigation.

## Use Cases
- **Log Shipping Agents:** This parser can serve as the core logic for a lightweight sidecar that tails log files, converts them to JSON, and ships them to a centralized collector.
- **Security Auditing:** By validating `trace_id` formats and timestamps, security teams can quickly scan for anomalous log entries.
- **ETL Pre-processing:** Before loading access logs into a data warehouse, this parser ensures that all timestamp columns are strictly typed and indexed correctly.
