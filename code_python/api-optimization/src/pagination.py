from pydantic import BaseModel, ConfigDict
from typing import Generic, TypeVar, List
from math import ceil

T = TypeVar("T")

class PageParams(BaseModel):
    page: int = 1
    page_size: int = 10

class PagedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int

    model_config = ConfigDict(from_attributes=True)

def paginate(query, params: PageParams):
    total = query.count()
    items = query.offset((params.page - 1) * params.page_size).limit(params.page_size).all()

    total_pages = ceil(total / params.page_size) if params.page_size > 0 else 0

    return {
        "items": items,
        "total": total,
        "page": params.page,
        "page_size": params.page_size,
        "total_pages": total_pages
    }
