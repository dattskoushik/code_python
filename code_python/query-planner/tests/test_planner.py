import pytest
from src.ast_models import SelectStmt, Join, Sort, LogicOp, BinaryOp, Literal, Identifier
from src.parser import parse_query
from src.optimizer import optimize
from src.compiler import compile_to_sql

def test_parser_full_query():
    data = {
        "table": "users",
        "columns": ["id", "email"],
        "joins": [
            {"type": "LEFT", "table": "posts", "on": {"op": "=", "left": {"col": "users.id"}, "right": {"col": "posts.user_id"}}}
        ],
        "where": {
            "op": "AND",
            "left": {"op": ">", "left": {"col": "age"}, "right": 18},
            "right": {"op": "=", "left": {"col": "active"}, "right": True}
        },
        "group_by": ["department"],
        "order_by": [{"field": "created_at", "direction": "DESC"}],
        "limit": 10
    }

    ast = parse_query(data)
    assert isinstance(ast, SelectStmt)
    assert ast.table == "users"
    assert len(ast.joins) == 1
    assert ast.joins[0].type == "LEFT"
    assert len(ast.order_by) == 1
    assert ast.order_by[0].direction == "DESC"
    assert ast.limit == 10

def test_optimizer_canonicalization():
    # Test that 'b' AND 'a' becomes 'a' AND 'b' (sorting)
    node = LogicOp(
        op='AND',
        left=Identifier(name='b'),
        right=Identifier(name='a')
    )

    optimized = optimize(node)

    # Expect: left='a', right='b'
    assert isinstance(optimized, LogicOp)
    assert optimized.left.name == 'a'
    assert optimized.right.name == 'b'

def test_optimizer_simplification():
    # 1=1 AND x>5 -> x>5
    node = LogicOp(
        op='AND',
        left=BinaryOp(op='=', left=Literal(value=1), right=Literal(value=1)),
        right=BinaryOp(op='>', left=Identifier(name='x'), right=Literal(value=5))
    )

    optimized = optimize(node)
    assert isinstance(optimized, BinaryOp)
    assert optimized.op == '>'
    assert optimized.right.value == 5

def test_compiler_output():
    # Construct a full AST
    ast = SelectStmt(
        table="users",
        columns=["name", "age"],
        where=BinaryOp(op='>', left=Identifier(name='age'), right=Literal(value=21)),
        order_by=[Sort(field="name", direction="ASC")]
    )

    sql = compile_to_sql(ast)
    # Identifiers should now be quoted
    expected = 'SELECT "name", "age" FROM "users" WHERE ("age" > 21) ORDER BY "name" ASC;'
    assert sql == expected

def test_compiler_joins():
    ast = SelectStmt(
        table="A",
        columns=["*"],
        joins=[
            Join(
                type="INNER",
                table="B",
                on=BinaryOp(op='=', left=Identifier(name='A.id'), right=Identifier(name='B.a_id'))
            )
        ]
    )
    sql = compile_to_sql(ast)
    # A.id -> "A"."id"
    expected = 'SELECT * FROM "A" INNER JOIN "B" ON ("A"."id" = "B"."a_id");'
    assert sql == expected
