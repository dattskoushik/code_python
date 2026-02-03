# Engineering a Rule-Based Query Planner from Scratch

Dynamic query generation is the backbone of modern Headless BI tools, versatile APIs, and data exploration platforms. However, passing raw strings to your database is a recipe for disaster—both in terms of security and performance. On **Day 22** of my 30-day technical sprint, I architected a robust **Query Planner** in Python that parses high-level JSON logic into an Abstract Syntax Tree (AST), applies deterministic optimizations, and compiles the result into clean, efficient SQL.

## The Problem: The "String Builder" Trap

When building APIs that support complex filtering (e.g., "Give me users who joined in 2023 AND (are active OR have premium status)"), developers often resort to conditional string concatenation.

```python
# The Anti-Pattern
sql = "SELECT * FROM users WHERE 1=1"
if params.get('active'):
    sql += " AND active = 1"
# ... scaling this is a nightmare
```

This approach is fragile. It makes it impossible to:
1.  **Optimize Logic**: You can't easily detect that `status='active' AND status='active'` is redundant.
2.  **Validate Semantics**: Is the user trying to filter on a column that doesn't exist?
3.  **Ensure Determinism**: `A AND B` often produces a different cache key than `B AND A`.

## The Solution: A Three-Stage Pipeline

I implemented a compiler architecture consisting of three distinct phases: **Parsing**, **Optimization**, and **Compilation**.

### 1. The Immutable AST (Abstract Syntax Tree)
Using **Pydantic V2**, I defined a strictly typed grammar. Every part of a SQL query—`SelectStmt`, `Join`, `LogicOp`—is a frozen model. This immutability is critical; it allows the optimizer to return *new* versions of the tree without side effects, making the system predictable and thread-safe.

```python
class LogicOp(Expression):
    op: Literal['AND', 'OR']
    left: Expression
    right: Expression
    # ... strict typing enforces valid structures
```

### 2. The Optimizer: Canonicalization & Simplification
This is the core of the project. The optimizer traverses the AST recursively. I implemented two key strategies:

**A. Boolean Algebra Simplification**
The system automatically reduces complex logic:
- `True AND X` $\rightarrow$ `X`
- `(1=1) AND (age > 20)` $\rightarrow$ `age > 20`
- `X AND X` $\rightarrow$ `X` (Deduplication)

**B. Canonicalization (Deterministic Sorting)**
To ensure that logically identical queries produce the same SQL (and thus hit the same database cache), I implemented a canonicalization rule.
- Input 1: `(age > 20) AND (status = 'active')`
- Input 2: `(status = 'active') AND (age > 20)`
- **Output (Both)**: `(age > 20) AND (status = 'active')`

By sorting operands based on their representation, the system ensures consistent output regardless of input order.

### 3. The SQL Compiler
The final stage translates the optimized AST into ANSI SQL. Because the AST handles the structural integrity (nested parentheses, operator precedence), the compiler logic remains linear and simple. It supports:
- **Joins**: Explicit `LEFT/INNER JOIN` handling.
- **Group By / Order By**: Structured sorting and aggregation.
- **Deeply Nested Filters**: Arbitrary depth of `AND`/`OR` logic.

## Implementation Highlight: The Optimization Loop

Here is how the optimizer handles canonicalization and simplification in a single pass:

```python
if op in ('AND', 'OR'):
    # Canonicalization: Sort operands for deterministic output
    if repr(left) > repr(right):
        left, right = right, left

    # Simplification: Redundancy removal
    if repr(left) == repr(right):
        return left
```

## Use Cases

1.  **Headless BI Engines**: Allow front-end applications to generate complex reports without writing SQL.
2.  **Secure Public APIs**: Expose a filtering language that is strictly mapped to allowed AST nodes, preventing SQL injection by design.
3.  **Query Caching Layers**: By canonicalizing queries before they hit the database, you significantly increase cache hit rates for equivalent requests.

## Conclusion

Writing a query planner reminds us that SQL is just another language to be compiled. By treating queries as data structures (ASTs) rather than strings, we gain immense power over execution, optimization, and safety.
