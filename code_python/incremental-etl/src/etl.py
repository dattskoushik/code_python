import hashlib
import json
from typing import List, Dict, Tuple, Set
from sqlalchemy.orm import Session
from sqlalchemy import select, update, insert
from src.models import ProductSource
from src.db import ProductModel

def compute_row_hash(record: ProductSource) -> str:
    """
    Computes a deterministic hash of the record.
    Using SHA-256 on the JSON representation.
    """
    # Sort keys to ensure deterministic JSON
    record_json = record.model_dump_json(exclude=None)
    return hashlib.sha256(record_json.encode('utf-8')).hexdigest()

def extract_simulated_data(scenario: str = "initial") -> List[ProductSource]:
    """
    Simulates extracting data from a source (e.g. CSV API).
    """
    base_data = [
        ProductSource(id=1, name="Laptop", category="Electronics", price=1200.0, stock=50),
        ProductSource(id=2, name="Mouse", category="Electronics", price=25.0, stock=200),
        ProductSource(id=3, name="Keyboard", category="Electronics", price=45.0, stock=150),
    ]

    if scenario == "initial":
        return base_data
    elif scenario == "update":
        # Modify ID 2 (Price change), ID 3 (Stock change), Add ID 4
        return [
            ProductSource(id=1, name="Laptop", category="Electronics", price=1200.0, stock=50), # Unchanged
            ProductSource(id=2, name="Mouse", category="Electronics", price=30.0, stock=200),   # Changed Price
            ProductSource(id=3, name="Keyboard", category="Electronics", price=45.0, stock=140),# Changed Stock
            ProductSource(id=4, name="Monitor", category="Electronics", price=300.0, stock=40), # New
        ]
    return []

def get_target_state(session: Session) -> Dict[int, str]:
    """
    Fetches a lightweight map of {primary_key: row_hash} from the target DB.
    """
    stmt = select(ProductModel.id, ProductModel.row_hash)
    result = session.execute(stmt).all()
    return {row.id: row.row_hash for row in result}

def detect_changes(source_data: List[ProductSource], target_map: Dict[int, str]) -> Tuple[List[Dict], List[Dict], List[int]]:
    """
    Compares source data against target state map.
    Returns (to_insert, to_update, unchanged_ids)
    """
    to_insert = []
    to_update = []
    unchanged_ids = []

    for record in source_data:
        record_hash = compute_row_hash(record)
        existing_hash = target_map.get(record.id)

        record_dict = record.model_dump()
        record_dict['row_hash'] = record_hash

        if existing_hash is None:
            to_insert.append(record_dict)
        elif existing_hash != record_hash:
            to_update.append(record_dict)
        else:
            unchanged_ids.append(record.id)

    return to_insert, to_update, unchanged_ids

def load_changes(session: Session, to_insert: List[Dict], to_update: List[Dict]):
    """
    Applies changes to the database using efficient bulk operations.
    """
    if to_insert:
        session.execute(insert(ProductModel), to_insert)

    if to_update:
        session.execute(update(ProductModel), to_update)

    session.commit()
