# Building a Rule-Based Query Optimizer in Python

Generating SQL dynamically is a common requirement for Headless BI tools, versatile APIs, and custom reporting engines. However, simply concatenating strings is dangerous and inefficient. On **Day 22** of my technical sprint, I architected a **Query Planner** that parses high-level JSON logic into an Abstract Syntax Tree (AST), applies optimization rules, and compiles it into clean SQL.

## The Problem

When building flexible data APIs, we often receive filters from the frontend in a structured format (JSON). Converting this directly to SQL often leads to:
1.  **Inefficient Queries**: Users might send redundant filters like `status='active' AND status='active'`.
2.  **Complex String Manipulation**: Handling nested `AND`/`OR` logic with string builders is error-prone.
3.  **Security Risks**: Direct injection of values without validation.

A "dumb" translator blindly converts every node. A "smart" planner understands the *intent* of the query.

## The Solution: AST-Driven Architecture

Instead of writing strings immediately, we first build an intermediate representation.

### 1. The Abstract Syntax Tree (AST)
I defined the grammar using **Pydantic** models to ensure type safety and immutability. Immutability is crucial for the optimizer, as it allows us to return *new* simplified nodes without side effects.

```python
class BinaryOp(Expression):
    left: Expression
    op: str
    right: Expression
```

### 2. The Optimizer Pass
This is where the magic happens. The optimizer traverses the tree bottom-up. It applies rules similar to how database engines (like Postgres or SQLite) optimize execution plans, but at the logical level.

**Key Optimizations Implemented:**

*   **Constant Folding**:
    If an expression consists entirely of literals (e.g., `1 + 1` or `'a' = 'a'`), it is evaluated immediately.
    *   *Input*: `{"op": "=", "left": 1, "right": 1}`
    *   *Result*: `Literal(True)`

*   **Boolean Simplification**:
    We apply algebraic rules to simplify logic gates.
    *   `True AND X` $\rightarrow$ `X`
    *   `False OR X` $\rightarrow$ `X`
    *   `False AND X` $\rightarrow$ `False`

*   **Redundancy Elimination**:
    *   `X AND X` $\rightarrow$ `X`

### 3. The Compiler
The final stage is a visitor that converts the optimized AST into the target SQL dialect. Because the tree is already simplified, the compiler's job is purely formatting.

## Code Highlight: The Optimization Loop

Here is a snippet of the recursive optimization logic for boolean `AND` operations:

```python
if op == 'AND':
    # True AND X -> X
    if is_literal_true(left): return right
    if is_literal_true(right): return left

    # False AND X -> False
    if is_literal_false(left): return Literal(value=False)

    # X AND X -> X
    if left == right: return left
```

This simple logic cascades. A complex query like `(1=1) AND (age > 20)` first folds `1=1` to `True`, then simplifies `True AND (age > 20)` to just `age > 20`.

## Use Cases

1.  **SaaS Filters**: allow users to save complex filter views without storing raw SQL.
2.  **Security Layer**: The parser acts as a firewall; only valid AST nodes (columns, supported ops) are compiled.
3.  **Cross-Database Compatibility**: The AST can be compiled to SQL, Mongo Query Language, or Elasticsearch DSL just by swapping the Compiler module.

## Conclusion

Building a query planner demystifies how databases understand our code. By separating parsing, optimization, and compilation, we gain immense control over the reliability and performance of dynamic queries.
