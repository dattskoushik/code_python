"""
processor.py

Core logic for processing batches of raw data and validating them against Pydantic models.
"""
from typing import List, Dict, Any, Type
from pydantic import ValidationError, BaseModel
from dataclasses import dataclass, field

@dataclass
class ValidationReport:
    """
    Holds the results of a batch validation.
    """
    valid_count: int = 0
    error_count: int = 0
    valid_records: List[BaseModel] = field(default_factory=list)
    errors: List[Dict[str, Any]] = field(default_factory=list)

def validate_batch(data: List[Dict[str, Any]], model_class: Type[BaseModel]) -> ValidationReport:
    """
    Iterates through a list of dictionaries, validating each against the provided model_class.
    Returns a ValidationReport with valid instances and structured errors.
    """
    report = ValidationReport()

    for index, record in enumerate(data):
        try:
            # Pydantic V2 usage: model_validate expects a dict or object
            instance = model_class.model_validate(record)
            report.valid_records.append(instance)
            report.valid_count += 1
        except ValidationError as e:
            report.error_count += 1

            # Format the errors for easier consumption
            formatted_errors = []
            for err in e.errors():
                # 'loc' is a tuple of (field_name, index, etc.)
                field_path = " -> ".join(str(l) for l in err['loc'])
                message = err['msg']
                formatted_errors.append(f"Field '{field_path}': {message}")

            report.errors.append({
                "index": index,
                "original_data": record,
                "error_messages": formatted_errors
            })

    return report
