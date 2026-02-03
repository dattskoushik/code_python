from typing import Any, Dict, List, Union
from .ast_models import SelectStmt, Expression, BinaryOp, LogicOp, Literal, Identifier, Join, Sort

def parse_query(data: Dict[str, Any]) -> SelectStmt:
    """
    Parses a JSON-like dictionary into a SelectStmt AST.
    """
    table = data.get("table")
    if not table:
        raise ValueError("Query must specify a 'table'.")

    columns = data.get("columns", [])
    if not columns:
        raise ValueError("Query must specify 'columns' list (or use ['*']).")

    # Parse Where
    where_data = data.get("where")
    where_clause = None
    if where_data:
        where_clause = parse_expr(where_data)

    # Parse Joins
    joins_data = data.get("joins", [])
    joins = []
    for j in joins_data:
        joins.append(Join(
            type=j.get("type", "INNER"),
            table=j["table"],
            on=parse_expr(j["on"])
        ))

    # Parse Group By
    group_by = data.get("group_by", [])

    # Parse Order By
    order_by_data = data.get("order_by", [])
    order_by = []
    for o in order_by_data:
        # Support simple string "field" or object {"field": "f", "direction": "DESC"}
        if isinstance(o, str):
            order_by.append(Sort(field=o))
        else:
            order_by.append(Sort(field=o["field"], direction=o.get("direction", "ASC")))

    limit = data.get("limit")

    return SelectStmt(
        table=table,
        columns=columns,
        joins=joins,
        where=where_clause,
        group_by=group_by,
        order_by=order_by,
        limit=limit
    )

def parse_expr(data: Any) -> Expression:
    """
    Parses a dictionary or primitive into an Expression AST node.
    """
    # Handle primitives -> Literal
    if isinstance(data, (int, float, bool)) or data is None:
        return Literal(value=data)

    # Handle strings -> Literal (default)
    # NOTE: In some parsers string might be identifier, but let's stick to explicit structure
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

            # Unary Not? Not implemented in current AST models, sticking to Binary/Logic

            left = parse_expr(data.get("left"))
            right = parse_expr(data.get("right"))

            if op in ('AND', 'OR'):
                return LogicOp(op=op, left=left, right=right)
            else:
                return BinaryOp(op=op, left=left, right=right)

    raise ValueError(f"Unknown expression format: {data}")
