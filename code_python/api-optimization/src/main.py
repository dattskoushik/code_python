from fastapi import FastAPI, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from contextlib import asynccontextmanager

from src.database import get_db, engine, Base
from src.models import Employee
from src.schemas import EmployeeRead, EmployeeCreate, EmployeeFilterParams
from src.pagination import PageParams, PagedResponse, paginate
from src.sorting import apply_sorting
from src.filters import apply_filters

# Create tables
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: could seed data here if needed, but we'll use a seed endpoint
    yield
    # Shutdown

app = FastAPI(lifespan=lifespan)

@app.post("/seed")
def seed_data(db: Session = Depends(get_db)):
    if db.query(Employee).count() > 0:
        return {"message": "Data already seeded"}

    employees = [
        Employee(full_name="Alice Johnson", department="Engineering", salary=95000),
        Employee(full_name="Bob Smith", department="Sales", salary=60000),
        Employee(full_name="Charlie Brown", department="Engineering", salary=80000),
        Employee(full_name="Diana Prince", department="Marketing", salary=75000),
        Employee(full_name="Evan Wright", department="Sales", salary=62000),
        Employee(full_name="Fiona Green", department="HR", salary=55000),
        Employee(full_name="George White", department="Engineering", salary=105000),
        Employee(full_name="Hannah Black", department="Marketing", salary=72000),
        Employee(full_name="Ian Grey", department="Sales", salary=58000),
        Employee(full_name="Julia Blue", department="Engineering", salary=88000),
    ]
    db.add_all(employees)
    db.commit()
    return {"message": "Seeded 10 employees"}

@app.get("/employees", response_model=PagedResponse[EmployeeRead])
def get_employees(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    sort_by: Optional[str] = Query(None, description="Field to sort by"),
    order: str = Query("asc", pattern="^(asc|desc)$"),
    department: Optional[str] = None,
    salary__gt: Optional[float] = None,
    salary__lt: Optional[float] = None,
    is_active: Optional[bool] = None,
    full_name__contains: Optional[str] = None
):
    # Construct filter dict from explicit params
    # In a real app, you might iterate over request.query_params, but explicit is cleaner for Swagger
    filters = {
        "department": department,
        "salary__gt": salary__gt,
        "salary__lt": salary__lt,
        "is_active": is_active,
        "full_name__contains": full_name__contains
    }

    query = db.query(Employee)
    query = apply_filters(query, Employee, filters)
    query = apply_sorting(query, Employee, sort_by, order)

    return paginate(query, PageParams(page=page, page_size=page_size))
