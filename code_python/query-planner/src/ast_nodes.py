from typing import List, Optional, Any, Union
from pydantic import BaseModel, ConfigDict

class Node(BaseModel):
    model_config = ConfigDict(frozen=True) # Immutable AST is good for optimization safety

class Expression(Node):
    pass

class Literal(Expression):
    value: Any

    def __repr__(self):
        return f"Literal({self.value})"

class Identifier(Expression):
    name: str

    def __repr__(self):
        return f"Id({self.name})"

class BinaryOp(Expression):
    left: Expression
    op: str
    right: Expression

    def __repr__(self):
        return f"({self.left} {self.op} {self.right})"

class LogicOp(Expression):
    op: str  # 'AND', 'OR'
    left: Expression
    right: Expression

    def __repr__(self):
        return f"({self.left} {self.op} {self.right})"

class SelectStmt(Node):
    table: str
    columns: List[str]  # keeping it simple: list of column names
    where: Optional[Expression] = None

    def __repr__(self):
        return f"SELECT {self.columns} FROM {self.table} WHERE {self.where}"
