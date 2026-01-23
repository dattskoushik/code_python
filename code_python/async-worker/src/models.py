from pydantic import BaseModel, ConfigDict
from enum import Enum
from typing import Optional, Any, Dict
from datetime import datetime


class JobStatus(str, Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class JobCreate(BaseModel):
    payload: Dict[str, Any]


class JobResponse(BaseModel):
    id: str
    status: JobStatus
    payload: Dict[str, Any]
    result: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
