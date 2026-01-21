# API Optimization Demo

A FastAPI implementation demonstrating advanced API querying patterns including pagination, filtering, and sorting.

## Features

- **Pagination**: Offset-based pagination with customizable page size.
- **Filtering**: Dynamic filtering supporting multiple operators (`eq`, `gt`, `lt`, `contains`, etc.).
- **Sorting**: Flexible sorting on any field in ascending or descending order.

## Setup

1.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

2.  Run the application:
    ```bash
    uvicorn src.main:app --reload
    ```

3.  Access the documentation at `http://127.0.0.1:8000/docs`.

## Usage

### Seeding Data

First, populate the database:

```bash
curl -X POST http://127.0.0.1:8000/seed
```

### Querying

**Pagination:**
```
GET /employees?page=2&page_size=5
```

**Filtering:**
```
GET /employees?department=Engineering&salary__gt=80000
```

**Sorting:**
```
GET /employees?sort_by=salary&order=desc
```

**Combined:**
```
GET /employees?department=Sales&sort_by=joining_date&order=desc&page=1
```
