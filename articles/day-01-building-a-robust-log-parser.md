# Day 01: Building a Robust Log Parser in Python

**Date:** October 27, 2023
**Author:** dattskoushik
**Project:** [Day 01 - Log Parser](../code_python/log-parser/)

---

## The 30-Day Technical Sprint Begins

To push the boundaries of my backend engineering skills, I've embarked on a high-intensity 30-day coding sprint. The goal is simple yet demanding: build a production-grade Python project every single day, covering everything from data engineering pipelines to distributed systems concepts.

For Day 01, I decided to tackle a foundational problem in observability: **Log Parsing**.

## The Problem: Chaos in Text

Logs are the lifeblood of debugging, but raw logs are often unstructured text files that are hard to query. A typical legacy system might spit out logs like this:

```text
[2023-10-27 10:00:01] {INFO} [AUTH_SERVICE] - U1001: LOGIN_SUCCESS | User logged in successfully.
```

To make this data useful for analytics or monitoring dashboards, we need to extract fields like timestamp, severity, module, user ID, and the actual message.

## The Solution: Regular Expressions & Pydantic Validation

While `string.split()` works for simple CSVs, complex logs often require the precision of Regular Expressions combined with the robustness of a data validation library. I designed a parser that uses **Pydantic V2** to enforce a strict schema.

### 1. Regex Pattern Design

I used Python's `re` module with named groups to make the extraction code readable:

```python
LOG_PATTERN = re.compile(
    r'^\[(?P<timestamp>.*?)\] \{(?P<severity>.*?)\} \[(?P<module>.*?)\] - (?P<user_id>.*?): (?P<action>.*?) \| (?P<message>.*)$'
)
```

### 2. Pydantic V2 Models

Extraction is only half the battle. Reliability comes from validation. I implemented a `LogEntry` model using Pydantic to handle type coercion and checks.

```python
class LogSeverity(str, Enum):
    INFO = 'INFO'
    WARN = 'WARN'
    ERROR = 'ERROR'
    ...

class LogEntry(BaseModel):
    model_config = ConfigDict(frozen=True)

    timestamp: datetime
    severity: LogSeverity
    module: str = Field(min_length=1)
    user_id: str = Field(pattern=r'^U\d+$')
    ...

    @field_validator('timestamp', mode='before')
    @classmethod
    def parse_timestamp(cls, value: str) -> datetime:
        return datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
```

This ensures:
- **Timestamp Format**: Strictly `YYYY-MM-DD HH:MM:SS`.
- **Severity Levels**: Enum-enforced (INFO, WARN, etc.).
- **Data Integrity**: Invalid data is rejected with clear error messages.

### 3. Structured Output

The final step is converting the parsed data into a machine-readable format. JSON is the industry standard here. The tool outputs a JSON object containing metadata (processing stats) and lists of valid/invalid logs.

```json
{
  "metadata": {
    "total_processed": 8,
    "valid_count": 5,
    "timestamp": "2023-10-27T10:00:00+00:00"
  },
  "logs": [
    {
      "timestamp": "2023-10-27T10:00:01",
      "severity": "INFO",
      "module": "AUTH_SERVICE",
      "message": "User logged in successfully."
    }
    ...
  ]
}
```

## Key Takeaways

- **Pydantic is a lifesaver**: It removes boilerplate validation code and provides standardized error reporting.
- **Regex is powerful, but fragile**: It requires careful crafting to handle edge cases.
- **Observability matters**: Parsing logs is the first step towards building metrics, alerts, and insights.

On to Day 02: Building a FastAPI service to ingest these logs!
