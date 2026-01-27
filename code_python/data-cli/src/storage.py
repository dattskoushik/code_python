import csv
import json
from pathlib import Path
from typing import List
from .models import Asset

def save_to_json(data: List[Asset], filepath: str):
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)

    # Convert Pydantic models to dicts
    json_data = [asset.model_dump() for asset in data]

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=4)

def save_to_csv(data: List[Asset], filepath: str):
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)

    if not data:
        return

    # Get fields from model definition
    headers = Asset.model_fields.keys()

    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for asset in data:
            writer.writerow(asset.model_dump())
