from typing import List, Optional, Any, Literal as PyLiteral
from pydantic import BaseModel, ConfigDict, Field

class Node(BaseModel):
    model_config = ConfigDict(frozen=True)

class Expression(Node):
    pass

class Literal(Expression):
    value: Any

class Identifier(Expression):
    name: str

class BinaryOp(Expression):
    left: Expression
    op: str
    right: Expression

class LogicOp(Expression):
    op: PyLiteral['AND', 'OR']
    left: Expression
    right: Expression

class Join(Node):
    type: PyLiteral['INNER', 'LEFT', 'RIGHT', 'FULL'] = 'INNER'
    table: str
    on: Expression

class Sort(Node):
    field: str
    direction: PyLiteral['ASC', 'DESC'] = 'ASC'

class SelectStmt(Node):
    table: str
    columns: List[str]
    joins: List[Join] = Field(default_factory=list)
    where: Optional[Expression] = None
    group_by: List[str] = Field(default_factory=list)
    order_by: List[Sort] = Field(default_factory=list)
    limit: Optional[int] = None
