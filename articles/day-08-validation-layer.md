# Building a Bulletproof Validation Layer with Pydantic V2

*Day 08 of the 30-Day Python Engineering Sprint*

Data integrity is the silent killer of backend systems. A single malformed record can crash an entire ETL pipeline or, worse, corrupt your database silently. In this project, I built a robust **Validation Layer** using Python's `Pydantic V2` to act as a strict gatekeeper for incoming data.

## The Problem: Garbage In, Crash Later

Traditional validation is often scattered across view functions, utility files, and database constraints. This leads to:
1.  **Inconsistency**: The email regex used in the signup API differs from the one in the CSV importer.
2.  **Fail-Slow**: Systems often crash on the first error, forcing a "fix-run-crash-repeat" cycle for large datasets.
3.  **Opaque Errors**: "Invalid Data" is not a helpful error message for a user who uploaded a 10,000-row spreadsheet.

## The Solution: Declarative, Centralized, and Aggregated

I designed a system that separates validation logic from business logic. By defining strict schemas (Models), we ensure that any data passing through this layer is guaranteed to be correct.

### Key Architecture Decisions

1.  **Pydantic V2**: Leveraged the massive performance improvements (Rust core) and the cleaner `model_validator` API of V2.
2.  **Batch Processing Strategy**: Instead of raising an exception and halting, the processor collects *all* errors for a record, and *all* invalid records in a batch, returning a structured report.
3.  **Cross-Field Validation**: Validating that `discount < total` requires access to multiple fields simultaneously, handled elegantly by Pydantic's `after` validators.

## Implementation Highlights

### 1. Reusable Validator Logic
I separated pure validation logic (regex, math) from the model definitions. This keeps the models clean and allows the validators to be reused elsewhere.

```python
# src/validators.py
SKU_PATTERN = re.compile(r"^[A-Z0-9]{3,}-[A-Z0-9]{3,}$")

def validate_sku(sku: str) -> bool:
    return bool(SKU_PATTERN.match(sku))
```

### 2. The Power of `model_validator`
Pydantic V2 introduced a cleaner syntax for validations that depend on the final state of the model.

```python
# src/models.py
@model_validator(mode='after')
def check_totals(self) -> 'Order':
    calculated_subtotal = sum(item.quantity * item.unit_price for item in self.items)
    if self.discount_amount > calculated_subtotal:
        raise ValueError("Discount amount cannot exceed the subtotal.")
    return self
```

### 3. Structured Error Aggregation
The processor captures `ValidationError` exceptions and parses them into a human-readable format, including the exact field path (e.g., `items -> 2 -> product_sku`).

```python
# src/processor.py
def validate_batch(data, model_class):
    report = ValidationReport()
    for record in data:
        try:
            instance = model_class.model_validate(record)
            report.valid_records.append(instance)
        except ValidationError as e:
            # Parse and store error details
            report.errors.append(...)
    return report
```

## Use Cases

This pattern is essential for:
*   **Bulk CSV/Excel Imports**: Give users a report saying "Rows 5, 12, and 99 failed" with reasons.
*   **API Gateway Middleware**: sanitize request bodies before they reach controller logic.
*   **Configuration Loading**: Validating complex YAML/JSON config files at startup.

By enforcing strict schemas at the edge of the system, we simplify the internal logic—backend services can trust that `order.total_amount` is always a valid float and mathematically consistent.
