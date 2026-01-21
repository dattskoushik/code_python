from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime
from datetime import datetime, UTC
from src.database import Base

class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, index=True)
    department = Column(String, index=True)
    salary = Column(Float)
    joining_date = Column(DateTime, default=lambda: datetime.now(UTC))
    is_active = Column(Boolean, default=True)
