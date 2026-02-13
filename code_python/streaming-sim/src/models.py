from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID, uuid4
from datetime import datetime, timezone
from typing import Any, Dict

class StreamPayload(BaseModel):
    """
    Immutable data model representing a single event in the stream.
    Supports comparison for use in asyncio.PriorityQueue.
    """
    id: UUID = Field(default_factory=uuid4)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    priority: int = Field(..., description="Lower value means higher priority (processed first)")
    event_type: str
    payload: Dict[str, Any]

    model_config = ConfigDict(frozen=True)

    def __lt__(self, other: Any) -> bool:
        if not isinstance(other, StreamPayload):
            return NotImplemented
        # In Python's PriorityQueue, lower items are retrieved first.
        # We want lower priority integer -> higher urgency.
        return self.priority < other.priority
