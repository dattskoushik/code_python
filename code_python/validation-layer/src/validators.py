import re
from datetime import datetime, timezone
from typing import Any

# Regex patterns for use with Pydantic's `pattern` argument
SKU_PATTERN = r"^[A-Z]{3}-\d{5}$"
PHONE_PATTERN = r"^\+?[1-9]\d{1,14}$"  # E.164 standard

def validate_not_future(v: datetime) -> datetime:
    """
    Validator to ensure a datetime object is not in the future.
    """
    # Ensure timezone awareness for comparison
    now = datetime.now(timezone.utc)

    if v.tzinfo is None:
        # If naive, assume UTC
        v_aware = v.replace(tzinfo=timezone.utc)
    else:
        v_aware = v

    if v_aware > now:
        raise ValueError("Date cannot be in the future")

    return v
