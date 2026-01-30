import pytest
from src.ast_nodes import LogicOp, BinaryOp, Literal, Identifier
from src.optimizer import optimize

def test_constant_folding():
    # 1 + 1 = 2
    node = BinaryOp(op='+', left=Literal(value=1), right=Literal(value=1))
    optimized = optimize(node)
    assert isinstance(optimized, Literal)
    assert optimized.value == 2

def test_boolean_simplification_and():
    # True AND X -> X
    x = Identifier(name='x')
    node = LogicOp(op='AND', left=Literal(value=True), right=x)
    optimized = optimize(node)
    assert optimized == x

    # False AND X -> False
    node = LogicOp(op='AND', left=Literal(value=False), right=x)
    optimized = optimize(node)
    assert isinstance(optimized, Literal)
    assert optimized.value is False

def test_boolean_simplification_or():
    # True OR X -> True
    x = Identifier(name='x')
    node = LogicOp(op='OR', left=Literal(value=True), right=x)
    optimized = optimize(node)
    assert isinstance(optimized, Literal)
    assert optimized.value is True

def test_redundancy_removal():
    # X AND X -> X
    x = Identifier(name='x')
    node = LogicOp(op='AND', left=x, right=x)
    optimized = optimize(node)
    assert optimized == x

def test_complex_tree():
    # (1=1) AND (x > 10) -> True AND (x > 10) -> (x > 10)
    tree = LogicOp(
        op='AND',
        left=BinaryOp(op='eq', left=Literal(value=1), right=Literal(value=1)),
        right=BinaryOp(op='gt', left=Identifier(name='x'), right=Literal(value=10))
    )
    optimized = optimize(tree)
    assert isinstance(optimized, BinaryOp)
    assert optimized.op == 'gt'
