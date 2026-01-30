from src.ast_nodes import SelectStmt, Literal, BinaryOp, Identifier, LogicOp
from src.compiler import compile_to_sql

def test_compile_select_basic():
    stmt = SelectStmt(table='users', columns=['id', 'name'])
    sql = compile_to_sql(stmt)
    assert sql == "SELECT id, name FROM users;"

def test_compile_where_clause():
    stmt = SelectStmt(
        table='users',
        columns=['*'],
        where=BinaryOp(op='>', left=Identifier(name='age'), right=Literal(value=18))
    )
    sql = compile_to_sql(stmt)
    # Note: compiler output spacing is rigid
    assert sql == "SELECT * FROM users WHERE (age > 18);"

def test_compile_nested_logic():
    where = LogicOp(
        op='AND',
        left=BinaryOp(op='eq', left=Identifier(name='status'), right=Literal(value='active')),
        right=BinaryOp(op='lt', left=Identifier(name='score'), right=Literal(value=10))
    )
    stmt = SelectStmt(table='data', columns=['id'], where=where)
    sql = compile_to_sql(stmt)
    assert sql == "SELECT id FROM data WHERE ((status = 'active') AND (score < 10));"

def test_compile_literals():
    assert compile_to_sql(Literal(value=None)) == "NULL"
    assert compile_to_sql(Literal(value=True)) == "TRUE"
    assert compile_to_sql(Literal(value="O'Neil")) == "'O''Neil'"
