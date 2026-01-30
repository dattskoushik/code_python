from typing import Any
from .ast_nodes import Node, SelectStmt, LogicOp, BinaryOp, Literal, Identifier

def compile_to_sql(node: Node) -> str:
    """
    Compiles an AST node into a SQL string.
    """
    if isinstance(node, SelectStmt):
        cols = "*"
        if node.columns:
            cols = ", ".join(node.columns)

        sql = f"SELECT {cols} FROM {node.table}"

        if node.where:
            where_clause = compile_to_sql(node.where)
            # If where clause is just 'TRUE', we can omit it, but let's include it if present
            # The optimizer might have removed it if it was True.
            sql += f" WHERE {where_clause}"

        return sql + ";"

    if isinstance(node, LogicOp):
        # AND, OR
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
        # default to the op string if not in map (e.g. +, -, =, >)
        op = op_map.get(node.op.lower(), node.op)

        return f"({compile_to_sql(node.left)} {op} {compile_to_sql(node.right)})"

    if isinstance(node, Identifier):
        return node.name

    if isinstance(node, Literal):
        return format_literal(node.value)

    raise ValueError(f"Cannot compile node of type {type(node)}")

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
