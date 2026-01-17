from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.orm import declarative_base
from pydantic import BaseModel, Field, field_validator, ConfigDict

Base = declarative_base()

# --- SQLAlchemy Model ---
class LogRecord(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, index=True, nullable=False)
    severity = Column(String(20), index=True, nullable=False)
    module = Column(String(50), index=True, nullable=False)
    user_id = Column(String(50), index=True, nullable=True)
    action = Column(String(50), nullable=True)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

# --- Pydantic Schemas ---

class LogBase(BaseModel):
    timestamp: datetime
    severity: str = Field(..., min_length=2, max_length=20, description="Log severity level (INFO, WARN, etc.)")
    module: str = Field(..., min_length=1, max_length=50, description="Source module of the log")
    user_id: Optional[str] = Field(None, max_length=50, description="User ID associated with the event")
    action: Optional[str] = Field(None, max_length=50, description="Specific action performed")
    message: str = Field(..., min_length=1, description="Log message content")

    @field_validator('severity')
    @classmethod
    def validate_severity(cls, v):
        allowed = {'INFO', 'WARN', 'ERROR', 'DEBUG', 'CRITICAL', 'FATAL'}
        if v.upper() not in allowed:
            raise ValueError(f"Severity must be one of {allowed}")
        return v.upper()

class LogCreate(LogBase):
    pass

class LogRead(LogBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
