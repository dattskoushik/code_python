# Validation Layer (Day 08)

A comprehensive data validation library using Pydantic V2, demonstrating strict field checks, custom validators, and robust batch processing error handling.

## Features

- **Strict Schema Enforcement**: Uses Pydantic V2 `ConfigDict(frozen=True)` for immutable models.
- **Complex Validation Rules**:
  - Regex-based formats (SKU, Phone) using `pattern` argument.
  - Cross-field validation (e.g., `total_amount` must equal sum of items).
  - Timezone-aware datetime checks.
- **Batch Processing**:
  - Processes lists of records without halting on individual failures.
  - Aggregates errors with detailed location and message context.
- **CLI Tool**: Simple interface to validate JSON files.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Running the CLI

To validate a JSON file, run the module from the project root:

```bash
# From code_python/validation-layer/
python3 -m src.main sample.json
```

### Programmatic Usage

```python
from src.processor import process_batch

data = [...] # List of dicts
result = process_batch(data)

print(f"Valid: {len(result.valid_orders)}")
print(f"Errors: {len(result.errors)}")
```

## Testing

Run unit tests using pytest:

```bash
# From code_python/validation-layer/
python3 -m pytest
```

## Project Structure

- `src/models.py`: Pydantic models (Order, Customer, OrderItem).
- `src/validators.py`: Reusable validation logic and patterns.
- `src/processor.py`: Batch processing logic.
- `src/main.py`: CLI entry point.
- `tests/`: Unit tests.
