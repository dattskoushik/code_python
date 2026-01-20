from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, field_validator, ConfigDict

class LogLevel(str, Enum):
    INFO = "INFO"
    ERROR = "ERROR"
    WARN = "WARN"
    DEBUG = "DEBUG"

class LogEntry(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    timestamp: datetime
    level: LogLevel
    trace_id: str = Field(..., pattern=r"^[a-f0-9\-]+$")
    message: str

    @field_validator("timestamp", mode="before")
    @classmethod
    def parse_timestamp(cls, v):
        if isinstance(v, datetime):
            return v
        # Attempt to parse ISO format if it's a string
        try:
            return datetime.fromisoformat(v.replace("Z", "+00:00"))
        except ValueError:
            raise ValueError("Invalid timestamp format. Expected ISO 8601.")
