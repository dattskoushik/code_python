from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, EmailStr
from sqlalchemy import String, Integer, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# Pydantic Model for Input Data
class CustomerSource(BaseModel):
    id: int
    name: str
    email: EmailStr
    status: str

# SQLAlchemy Base
class Base(DeclarativeBase):
    pass

# SQLAlchemy Model for Persistence
class CustomerDB(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    email: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String)

    # Metadata for Incremental ETL
    row_hash: Mapped[str] = mapped_column(String, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<Customer(id={self.id}, name='{self.name}', hash='{self.row_hash}')>"
