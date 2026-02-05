import json
import sys
import os

# Ensure we can import modules if running directly
sys.path.append(os.getcwd())

from src.storage import Storage
from src.etl import IncrementalLoader

def main():
    # Use a file-based DB for persistence across runs in this demo
    db_path = "incremental_etl_demo.db"
    db_url = f"sqlite:///{db_path}"

    # Clean up previous run for demo purposes? No, we want to show persistence.
    # But if I run it multiple times, I might want a fresh start.
    # Let's delete it if it exists to make the output deterministic for this demo script.
    if os.path.exists(db_path):
        os.remove(db_path)

    print(f"Initializing Storage at {db_url}...")
    storage = Storage(db_url)
    storage.init_db()

    loader = IncrementalLoader(storage)

    # --- Run 1: Initial Load ---
    print("\n[Run 1] Initial Load")
    data_v1 = [
        {"id": 101, "name": "Alice Johnson", "email": "alice@example.com", "status": "active"},
        {"id": 102, "name": "Bob Smith", "email": "bob@example.com", "status": "inactive"},
    ]
    stats_v1 = loader.process(data_v1)
    print(json.dumps(stats_v1, indent=2, default=str))

    # --- Run 2: Incremental Load ---
    # Scenarios:
    # 101: Changed email -> Update
    # 102: Unchanged -> Ignore
    # 103: New record -> Insert
    print("\n[Run 2] Delta Load")
    data_v2 = [
        {"id": 101, "name": "Alice Johnson", "email": "alice.new@example.com", "status": "active"},
        {"id": 102, "name": "Bob Smith", "email": "bob@example.com", "status": "inactive"},
        {"id": 103, "name": "Charlie Brown", "email": "charlie@example.com", "status": "pending"},
    ]
    stats_v2 = loader.process(data_v2)
    print(json.dumps(stats_v2, indent=2, default=str))

    # --- Run 3: Validation Error ---
    print("\n[Run 3] Bad Data Load")
    data_v3 = [
        {"id": 104, "name": "Dave", "email": "not-an-email-address", "status": "error"},
    ]
    stats_v3 = loader.process(data_v3)
    print(json.dumps(stats_v3, indent=2, default=str))

    # Verify final state
    print("\n[Final State Check]")
    current_state = storage.get_current_state()
    print(f"Total records in DB: {len(current_state)}")

    storage.close()

    # Cleanup
    if os.path.exists(db_path):
        os.remove(db_path)

if __name__ == "__main__":
    main()
