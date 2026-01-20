from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import Column, Integer, String, DateTime, JSON
from pydantic import BaseModel, Field, ConfigDict
import datetime as dt

from .database import Base

# SQLAlchemy Model
class Record(Base):
    __tablename__ = "records"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(dt.UTC))
    service_name = Column(String, index=True, nullable=False)
    severity = Column(String, nullable=False)
    message = Column(String, nullable=False)
    payload = Column(JSON, nullable=True)  # Renamed from meta_data/metadata to payload for clarity

# Pydantic Schemas

class RecordBase(BaseModel):
    service_name: str = Field(..., description="Name of the service generating the log", min_length=1, max_length=50)
    severity: str = Field(..., description="Log severity level", pattern="^(INFO|WARN|ERROR|DEBUG|CRITICAL)$")
    message: str = Field(..., description="Log message content", min_length=1)
    payload: Optional[Dict[str, Any]] = Field(None, description="Optional JSON payload")

class RecordCreate(RecordBase):
    """Schema for creating a new record"""
    pass

class RecordResponse(RecordBase):
    """Schema for returning a record"""
    id: int
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)
