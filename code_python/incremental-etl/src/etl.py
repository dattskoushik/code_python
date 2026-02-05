import hashlib
import json
from typing import List, Dict, Any, Tuple
from .storage import Storage
from .models import CustomerSource

class IncrementalLoader:
    def __init__(self, storage: Storage):
        self.storage = storage

    def _compute_hash(self, data: Dict[str, Any]) -> str:
        """
        Computes a deterministic SHA256 hash of the record's business fields.
        Excludes 'id' because that's the key; we want to detect content changes.
        """
        # Filter out ID and any metadata if present
        # We only care about business value fields
        payload = {k: v for k, v in data.items() if k != 'id'}

        # Sort keys to ensure deterministic output
        # Use default=str to handle datetime or other types serialization
        encoded = json.dumps(payload, sort_keys=True, default=str).encode('utf-8')
        return hashlib.sha256(encoded).hexdigest()

    def process(self, source_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Main ETL loop:
        1. Fetch current DB state (ID -> Hash map).
        2. Iterate source records.
        3. Validate and Hash.
        4. Detect Delta (Insert vs Update vs Unchanged).
        5. Persist changes.
        """
        # 1. Fetch State
        current_state = self.storage.get_current_state()

        inserts = []
        updates = []
        unchanged_count = 0
        errors = []

        # 2. Iterate
        for idx, row in enumerate(source_data):
            try:
                # Validation
                # This ensures we only work with fields defined in our model
                model = CustomerSource(**row)
                clean_data = model.model_dump()
            except Exception as e:
                # Aggregate errors
                errors.append({"index": idx, "data": row, "error": str(e)})
                continue

            # 3. Compute Hash
            record_hash = self._compute_hash(clean_data)

            pk = clean_data['id']

            # Prepare record for persistence
            # We add row_hash to the payload
            db_record = clean_data.copy()
            db_record['row_hash'] = record_hash

            # 4. Delta Detection
            if pk not in current_state:
                inserts.append(db_record)
            elif current_state[pk] != record_hash:
                updates.append(db_record)
            else:
                unchanged_count += 1

        # 5. Persist
        self.storage.apply_batch(inserts, updates)

        return {
            "inserted": len(inserts),
            "updated": len(updates),
            "unchanged": unchanged_count,
            "errors": len(errors),
            "error_list": errors
        }
