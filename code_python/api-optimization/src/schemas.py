from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class EmployeeBase(BaseModel):
    full_name: str
    department: str
    salary: float
    is_active: bool = True

class EmployeeCreate(EmployeeBase):
    pass

class EmployeeRead(EmployeeBase):
    id: int
    joining_date: datetime

    model_config = ConfigDict(from_attributes=True)

class EmployeeFilterParams(BaseModel):
    department: Optional[str] = None
    salary__gt: Optional[float] = None
    salary__lt: Optional[float] = None
    is_active: Optional[bool] = None
    full_name__contains: Optional[str] = None
