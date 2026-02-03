from typing import List, Any, Dict
from pydantic import BaseModel, ValidationError
from .models import Order

class BatchValidationResult(BaseModel):
    valid_orders: List[Order] = []
    errors: List[Dict[str, Any]] = []

def process_batch(data: List[Dict[str, Any]]) -> BatchValidationResult:
    """
    Processes a list of raw data dictionaries, validating each against the Order model.
    Returns a result containing lists of valid Order objects and error details.
    """
    valid = []
    errors = []

    for index, record in enumerate(data):
        try:
            order = Order.model_validate(record)
            valid.append(order)
        except ValidationError as e:
            # Capture structured error information
            errors.append({
                "index": index,
                "raw_data": record,
                "validation_errors": e.errors(include_url=False)
            })

    return BatchValidationResult(valid_orders=valid, errors=errors)
