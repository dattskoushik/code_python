# Rule-Based Query Planner & Optimizer

A lightweight, robust query translation engine that converts high-level JSON queries into optimized SQL. Built for Day 22 of the 30-Day Technical Sprint.

## Features

- **JSON-based Query Language**: Simple, intuitive structure for defining selections and filters.
- **AST-based Architecture**: Parses queries into an Abstract Syntax Tree using strictly typed Pydantic models.
- **Rule-Based Optimizer**:
  - **Constant Folding**: Pre-calculates constant expressions (e.g., `1 + 1` → `2`).
  - **Boolean Simplification**: Reduces complex logic (e.g., `condition AND True` → `condition`, `False OR X` → `X`).
  - **Redundancy Removal**: Eliminates duplicate predicates.
- **SQL Compiler**: Generates clean, valid SQL from the optimized AST.
- **CLI Tool**: `main.py` entry point for file-based processing.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### CLI

1. Create a query file (e.g., `query.json`):
   ```json
   {
       "table": "users",
       "columns": ["id", "email"],
       "where": {
           "op": "AND",
           "left": {"op": "=", "left": {"col": "status"}, "right": "active"},
           "right": {"op": ">", "left": {"col": "created_at"}, "right": "2023-01-01"}
       }
   }
   ```

2. Run the planner:
   ```bash
   python3 -m src.main query.json
   ```

3. Output:
   ```sql
   SELECT id, email FROM users WHERE ((status = 'active') AND (created_at > '2023-01-01'));
   ```

### Optimization Demo

Query: `1=1 AND age > 18`

Command:
```bash
python3 -m src.main query.json
```
Output:
```sql
SELECT * FROM users WHERE (age > 18);
```
(The `1=1` is folded to `True`, and `True AND X` simplifies to `X`).

## Architecture

- **`parser.py`**: Validates JSON and builds the initial AST.
- **`optimizer.py`**: Recursively traverses the AST, applying simplification rules.
- **`compiler.py`**: Converts the AST into SQL strings.
- **`ast_nodes.py`**: Immutable Pydantic models defining the language grammar.

## Testing

```bash
python3 -m pytest
```
