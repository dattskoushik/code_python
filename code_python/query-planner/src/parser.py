from typing import Any, Dict, Union
from .ast_nodes import SelectStmt, Expression, BinaryOp, LogicOp, Literal, Identifier

def parse_query(data: Dict[str, Any]) -> SelectStmt:
    """
    Parses a JSON-like dictionary into a SelectStmt AST.
    """
    table = data.get("table")
    if not table:
        raise ValueError("Query must specify a 'table'.")

    columns = data.get("columns", [])

    where_data = data.get("where")
    where_clause = None
    if where_data:
        where_clause = parse_expr(where_data)

    return SelectStmt(table=table, columns=columns, where=where_clause)

def parse_expr(data: Any) -> Expression:
    """
    Parses a dictionary or primitive into an Expression AST node.
    """
    # Handle primitives -> Literal
    if isinstance(data, (int, float, bool)) or data is None:
        return Literal(value=data)

    # Handle strings -> Literal (default)
    if isinstance(data, str):
        return Literal(value=data)

    # Handle dictionary structures
    if isinstance(data, dict):
        # Case 1: Explicit Identifier {"col": "name"}
        if "col" in data:
            return Identifier(name=data["col"])

        # Case 2: Explicit Literal {"literal": value}
        if "literal" in data:
            return Literal(value=data["literal"])

        # Case 3: Operation {"op": "...", "left": ..., "right": ...}
        if "op" in data:
            op = data["op"].upper()
            left = parse_expr(data.get("left"))
            right = parse_expr(data.get("right"))

            if op in ('AND', 'OR'):
                return LogicOp(op=op, left=left, right=right)
            else:
                return BinaryOp(op=op, left=left, right=right)

    raise ValueError(f"Unknown expression format: {data}")
