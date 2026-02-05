from src.db import get_engine, get_session_factory, init_db
from src.etl import extract_simulated_data, get_target_state, detect_changes, load_changes
import os

def run_etl(scenario: str, session_factory):
    print(f"\n--- Running ETL Scenario: {scenario} ---")

    with session_factory() as session:
        # 1. Extract
        source_data = extract_simulated_data(scenario)
        print(f"Extracted {len(source_data)} records.")

        # 2. Get Current State (Delta Detection)
        target_map = get_target_state(session)
        print(f"Target DB has {len(target_map)} records.")

        # 3. Detect Changes
        to_insert, to_update, unchanged = detect_changes(source_data, target_map)
        print(f"Detected Changes: Inserts={len(to_insert)}, Updates={len(to_update)}, Unchanged={len(unchanged)}")

        # 4. Load
        if to_insert or to_update:
            load_changes(session, to_insert, to_update)
            print("Changes applied successfully.")
        else:
            print("No changes to apply.")

def main():
    # Remove existing db for clean run
    if os.path.exists("etl.db"):
        os.remove("etl.db")

    db_url = "sqlite:///etl.db"
    engine = get_engine(db_url)
    init_db(engine)
    Session = get_session_factory(engine)

    # Run Initial Load
    run_etl("initial", Session)

    # Run Update Load
    # Scenario 'update': Modifies 2 records, adds 1, leaves 1 unchanged.
    run_etl("update", Session)

    # Run No-Op Load (Idempotency check)
    # Should result in 0 inserts, 0 updates.
    run_etl("update", Session)

if __name__ == "__main__":
    main()
