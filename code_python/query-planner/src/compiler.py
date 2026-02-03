from typing import Any
from .ast_models import Node, SelectStmt, LogicOp, BinaryOp, Literal, Identifier, Join, Sort

def compile_to_sql(node: Node) -> str:
    """
    Compiles an AST node into a SQL string.
    """
    if isinstance(node, SelectStmt):
        cols = "*"
        if node.columns and node.columns != ['*']:
            # Quote columns
            cols = ", ".join([quote_ident(c) for c in node.columns])
        elif node.columns == []:
            cols = "*"

        # Quote table
        table_ref = quote_ident(node.table)
        sql = f"SELECT {cols} FROM {table_ref}"

        # Joins
        if node.joins:
            for j in node.joins:
                join_type = j.type.upper()
                join_table = quote_ident(j.table)
                join_cond = compile_to_sql(j.on)
                sql += f" {join_type} JOIN {join_table} ON {join_cond}"

        # Where
        if node.where:
            where_clause = compile_to_sql(node.where)
            sql += f" WHERE {where_clause}"

        # Group By
        if node.group_by:
            group_clause = ", ".join([quote_ident(c) for c in node.group_by])
            sql += f" GROUP BY {group_clause}"

        # Order By
        if node.order_by:
            order_clause = ", ".join([compile_sort(s) for s in node.order_by])
            sql += f" ORDER BY {order_clause}"

        # Limit
        if node.limit is not None:
            sql += f" LIMIT {node.limit}"

        return sql + ";"

    if isinstance(node, LogicOp):
        return f"({compile_to_sql(node.left)} {node.op} {compile_to_sql(node.right)})"

    if isinstance(node, BinaryOp):
        op_map = {
            'eq': '=',
            'neq': '!=',
            'lt': '<',
            'gt': '>',
            'lte': '<=',
            'gte': '>=',
        }
        op = op_map.get(node.op.lower(), node.op)
        return f"({compile_to_sql(node.left)} {op} {compile_to_sql(node.right)})"

    if isinstance(node, Identifier):
        return quote_ident(node.name)

    if isinstance(node, Literal):
        return format_literal(node.value)

    raise ValueError(f"Cannot compile node of type {type(node)}")

def quote_ident(name: str) -> str:
    """Quotes an identifier with double quotes to prevent injection/syntax errors."""
    if name == "*":
        return "*"
    # Split by dot for table.column
    parts = name.split('.')
    quoted_parts = [f'"{p.replace('"', '""')}"' for p in parts]
    return ".".join(quoted_parts)

def compile_sort(node: Sort) -> str:
    return f"{quote_ident(node.field)} {node.direction}"

def format_literal(value: Any) -> str:
    if value is None:
        return "NULL"
    if isinstance(value, bool):
        return "TRUE" if value else "FALSE"
    if isinstance(value, str):
        # Basic escaping
        escaped = value.replace("'", "''")
        return f"'{escaped}'"
    return str(value)
