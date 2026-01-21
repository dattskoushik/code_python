from typing import Optional, Any, Dict
from sqlalchemy.orm import Query
from sqlalchemy import and_

# Map string operators to SQLAlchemy operators or logic
def apply_filters(query: Query, model: Any, filters: Dict[str, Any]) -> Query:
    """
    Applies filters to the query.
    Supported conventions:
    field: exact match
    field__gt: greater than
    field__gte: greater than or equal
    field__lt: less than
    field__lte: less than or equal
    field__contains: string contains (ilike)
    """
    conditions = []

    for key, value in filters.items():
        if value is None:
            continue

        if "__" in key:
            field_name, op = key.split("__", 1)
        else:
            field_name, op = key, "eq"

        if not hasattr(model, field_name):
            continue

        column = getattr(model, field_name)

        if op == "eq":
            conditions.append(column == value)
        elif op == "gt":
            conditions.append(column > value)
        elif op == "gte":
            conditions.append(column >= value)
        elif op == "lt":
            conditions.append(column < value)
        elif op == "lte":
            conditions.append(column <= value)
        elif op == "contains":
            conditions.append(column.ilike(f"%{value}%"))

    if conditions:
        query = query.filter(and_(*conditions))

    return query
