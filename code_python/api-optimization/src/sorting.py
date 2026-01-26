from typing import Optional, Any
from sqlalchemy.orm import Query
from sqlalchemy import asc, desc

def apply_sorting(query: Query, model: Any, sort_by: Optional[str] = None, order: str = "asc") -> Query:
    if not sort_by:
        return query

    if not hasattr(model, sort_by):
        raise ValueError(f"Invalid sort field: {sort_by}")

    column = getattr(model, sort_by)

    if order.lower() == "desc":
        return query.order_by(desc(column))

    return query.order_by(asc(column))
