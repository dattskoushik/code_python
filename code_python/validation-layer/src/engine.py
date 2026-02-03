from typing import Type, List, Dict, Any
from pydantic import BaseModel, ValidationError

def validate_dataset(raw_data: List[Dict[str, Any]], model: Type[BaseModel]) -> Dict[str, Any]:
    """
    Validates a list of dictionaries against a Pydantic model.
    Returns a summary containing valid records and structured errors.
    """
    valid_records = []
    errors = []

    for index, record in enumerate(raw_data):
        try:
            # Pydantic V2 usage
            instance = model.model_validate(record)
            # Dump to dict (serialization)
            valid_records.append(instance.model_dump())
        except ValidationError as e:
            # Parse errors
            error_details = []
            for err in e.errors():
                # Flatten location tuple to string
                loc = " -> ".join([str(x) for x in err['loc']])
                msg = err['msg']
                error_details.append(f"Field '{loc}': {msg}")

            errors.append({
                "index": index,
                "original_data": record,
                "errors": error_details
            })

    return {
        "valid_count": len(valid_records),
        "invalid_count": len(errors),
        "valid_records": valid_records,
        "errors": errors
    }
