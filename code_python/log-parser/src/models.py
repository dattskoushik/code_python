from enum import Enum
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator, ConfigDict

class LogSeverity(str, Enum):
    INFO = 'INFO'
    WARN = 'WARN'
    ERROR = 'ERROR'
    DEBUG = 'DEBUG'
    CRITICAL = 'CRITICAL'

class LogEntry(BaseModel):
    """
    Represents a single valid log entry.
    """
    model_config = ConfigDict(frozen=True)

    timestamp: datetime
    severity: LogSeverity
    module: str = Field(min_length=1)
    user_id: str = Field(pattern=r'^U\d+$')
    action: str = Field(min_length=1)
    message: str

    @field_validator('timestamp', mode='before')
    @classmethod
    def parse_timestamp(cls, value: str) -> datetime:
        # Expected format: 2023-10-27 10:00:01
        try:
            return datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            raise ValueError("Invalid timestamp format. Expected YYYY-MM-DD HH:MM:SS")

class LogError(BaseModel):
    """
    Represents a failed log parsing attempt.
    """
    line_number: int
    raw_content: str
    error_message: str

class ParsingMetadata(BaseModel):
    total_processed: int
    valid_count: int
    invalid_count: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ParsingResult(BaseModel):
    metadata: ParsingMetadata
    logs: List[LogEntry]
    errors: List[LogError]
