from typing import Any
from .ast_models import Node, SelectStmt, LogicOp, BinaryOp, Literal, Expression, Join

def optimize(node: Node) -> Node:
    """
    Recursively optimizes the AST by applying constant folding, boolean simplification,
    and canonicalization rules.
    """
    if isinstance(node, SelectStmt):
        # Optimize the WHERE clause
        new_where = optimize(node.where) if node.where else None

        if is_literal_true(new_where):
            new_where = None

        # Optimize Joins
        new_joins = []
        for j in node.joins:
            new_on = optimize(j.on)
            # If JOIN ON True -> Cross Join behavior effectively (but explicit True)
            new_joins.append(Join(type=j.type, table=j.table, on=new_on))

        return SelectStmt(
            table=node.table,
            columns=node.columns,
            joins=new_joins,
            where=new_where,
            group_by=node.group_by,
            order_by=node.order_by,
            limit=node.limit
        )

    if isinstance(node, LogicOp):
        # Recurse first (bottom-up)
        left = optimize(node.left)
        right = optimize(node.right)

        op = node.op.upper()

        # Rule: Canonicalization (Sorting)
        # Ensure deterministic order: Literal < Identifier < Others, or just str(repr)
        # Only swap if commutative (AND, OR)
        if op in ('AND', 'OR'):
            if repr(left) > repr(right):
                left, right = right, left

        # Rule: Boolean Simplification
        if op == 'AND':
            # True AND X -> X
            if is_literal_true(left): return right
            if is_literal_true(right): return left
            # False AND X -> False
            if is_literal_false(left): return Literal(value=False)
            if is_literal_false(right): return Literal(value=False)
            # X AND X -> X
            if repr(left) == repr(right): return left

        elif op == 'OR':
            # True OR X -> True
            if is_literal_true(left): return Literal(value=True)
            if is_literal_true(right): return Literal(value=True)
            # False OR X -> X
            if is_literal_false(left): return right
            if is_literal_false(right): return left
            # X OR X -> X
            if repr(left) == repr(right): return left

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
        # Simple arithmetic and comparison
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
        if op == 'and': return bool(val1) and bool(val2)
        if op == 'or': return bool(val1) or bool(val2)
    except Exception:
        return None
    return None
