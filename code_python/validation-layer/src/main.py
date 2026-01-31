import sys
import json
import argparse
from pathlib import Path
from .processor import process_batch

def main():
    parser = argparse.ArgumentParser(description="Batch Data Validator")
    parser.add_argument("filepath", type=str, help="Path to the JSON data file")
    args = parser.parse_args()

    file_path = Path(args.filepath)
    if not file_path.exists():
        print(f"Error: File not found: {file_path}")
        sys.exit(1)

    try:
        with open(file_path, "r") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Failed to decode JSON: {e}")
        sys.exit(1)

    if not isinstance(data, list):
        print("Error: Root JSON element must be a list of records.")
        sys.exit(1)

    print(f"Processing {len(data)} records from {file_path}...")
    result = process_batch(data)

    print("\n--- Validation Summary ---")
    print(f"Total:   {len(data)}")
    print(f"Valid:   {len(result.valid_orders)}")
    print(f"Invalid: {len(result.errors)}")

    if result.errors:
        print("\n--- Errors ---")
        for err in result.errors:
            print(f"Record #{err['index']} Failed:")
            for detail in err['validation_errors']:
                loc = " -> ".join(str(l) for l in detail['loc'])
                print(f"  - Field: {loc}")
                print(f"    Msg:   {detail['msg']}")
                print(f"    Type:  {detail['type']}")
            print("-" * 20)

if __name__ == "__main__":
    main()
