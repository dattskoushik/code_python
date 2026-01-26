from enum import Enum
from typing import Any, Dict, Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class JobStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class JobBase(BaseModel):
    task_type: str = Field(..., description="The type of task to perform")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Input data for the task")

class JobCreate(JobBase):
    pass

class Job(JobBase):
    id: int
    status: JobStatus = JobStatus.PENDING
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
