# Day 07: Data Normalization - From Chaos to Structure

## The Problem

In the real world, data is rarely clean. Legacy systems, third-party exports, and user-generated content often come in flat, denormalized formats like CSV or Excel. These files contain redundant information—repeating customer details for every transaction or duplicating product metadata across thousands of rows.

Storing data this way leads to:
1.  **Data Inconsistency**: Updating a customer's email in one row doesn't update it in others.
2.  **Bloat**: Storing "John Doe" strings millions of times wastes storage.
3.  **Slow Queries**: Aggregating or searching non-indexed, repeated text is inefficient.

The challenge is to take this "chaos" and transform it into a structured, relational schema (3NF) without losing data integrity.

## The Solution

For Day 07, I built a robust **Data Normalization Pipeline** using Python and SQLAlchemy. The system ingests raw, messy CSV files and decomposes them into distinct entities: `Customers`, `Products`, `Orders`, and `OrderItems`.

### Key Architecture Components

1.  **Declarative Models**: Defined a clear schema using SQLAlchemy's ORM.
    ```python
    class Customer(Base):
        __tablename__ = "customers"
        id: Mapped[int] = mapped_column(primary_key=True)
        email: Mapped[str] = mapped_column(String(100), unique=True)
        # ...
    ```

2.  **Smart Caching & Idempotency**:
    The core normalizer uses in-memory dictionaries to cache entities (`email -> Customer` object) during processing. This drastically reduces database round-trips (avoiding N+1 SELECTs) while ensuring we don't insert duplicates.

    ```python
    if email not in customer_cache:
        # Check DB first (for restartability)
        customer = session.execute(select(Customer).where(Customer.email == email)).scalar()
        if not customer:
            customer = Customer(...)
            session.add(customer)
        customer_cache[email] = customer
    ```

3.  **Transactional Integrity**:
    The entire batch is wrapped in a session. If any part of the normalization fails (e.g., a data type mismatch), the transaction rolls back, leaving the database in a clean state.

### Tech Stack
-   **Python 3.12**: Core logic.
-   **SQLAlchemy**: ORM for database abstraction (simulating PostgreSQL).
-   **Pytest**: Verification of normalization logic using in-memory databases.

## Use Cases

1.  **Legacy Migrations**: Moving data from old mainframes or flat-file systems to modern SQL warehouses.
2.  **E-commerce Imports**: Onboarding product catalogs from suppliers who provide messy Excel sheets.
3.  **Log Analysis**: Extracting structured entities (users, IPs) from unstructured application logs for analytics.

## Conclusion

Normalization is the bedrock of Data Engineering. By converting raw streams into structured entities, we enable powerful analytics, ensure data integrity, and pave the way for scalable applications.
