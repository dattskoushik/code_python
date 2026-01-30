from typing import Any
from .ast_nodes import Node, SelectStmt, LogicOp, BinaryOp, Literal, Expression

def optimize(node: Node) -> Node:
    """
    Recursively optimizes the AST by applying constant folding and boolean simplification rules.
    """
    if isinstance(node, SelectStmt):
        # Optimize the WHERE clause
        new_where = optimize(node.where) if node.where else None

        # If WHERE becomes True, remove it?
        # Usually SQL 'WHERE 1=1' is fine, but removing it is cleaner.
        if is_literal_true(new_where):
            new_where = None

        # If WHERE becomes False, the query returns nothing.
        # We could replace the whole query with an empty set representation,
        # but for now let's keep the WHERE False to let the SQL engine handle (or return EmptyResult).

        return SelectStmt(
            table=node.table,
            columns=node.columns,
            where=new_where
        )

    if isinstance(node, LogicOp):
        # Recurse first (bottom-up)
        left = optimize(node.left)
        right = optimize(node.right)

        op = node.op.upper()

        if op == 'AND':
            # True AND X -> X
            if is_literal_true(left): return right
            if is_literal_true(right): return left
            # False AND X -> False
            if is_literal_false(left): return Literal(value=False)
            if is_literal_false(right): return Literal(value=False)
            # X AND X -> X
            if left == right: return left

        elif op == 'OR':
            # True OR X -> True
            if is_literal_true(left): return Literal(value=True)
            if is_literal_true(right): return Literal(value=True)
            # False OR X -> X
            if is_literal_false(left): return right
            if is_literal_false(right): return left
            # X OR X -> X
            if left == right: return left

        return LogicOp(op=node.op, left=left, right=right)

    if isinstance(node, BinaryOp):
        left = optimize(node.left)
        right = optimize(node.right)

        # Constant Folding: If both sides are literals, compute the result
        if isinstance(left, Literal) and isinstance(right, Literal):
            result = evaluate_binary_op(node.op, left.value, right.value)
            if result is not None:
                return Literal(value=result)

        return BinaryOp(op=node.op, left=left, right=right)

    return node

def is_literal_true(node: Node) -> bool:
    return isinstance(node, Literal) and node.value is True

def is_literal_false(node: Node) -> bool:
    return isinstance(node, Literal) and node.value is False

def evaluate_binary_op(op: str, val1: Any, val2: Any) -> Any:
    op = op.lower()
    try:
        if op == '=' or op == 'eq': return val1 == val2
        if op == '!=' or op == 'neq': return val1 != val2
        if op == '>': return val1 > val2
        if op == '<': return val1 < val2
        if op == '>=': return val1 >= val2
        if op == '<=': return val1 <= val2
        if op == '+': return val1 + val2
        if op == '-': return val1 - val2
        if op == '*': return val1 * val2
        if op == '/': return val1 / val2
    except Exception:
        return None
    return None
