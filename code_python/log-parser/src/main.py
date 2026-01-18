#!/usr/bin/env python3
import argparse
import sys
import json
from .parser import process_log_file

def main():
    parser = argparse.ArgumentParser(description="Day 01 Log Parser - dattskoushik")
    parser.add_argument('input_file', help="Path to the log file")
    parser.add_argument('-o', '--output', help="Path to output JSON file")
    parser.add_argument('-q', '--quiet', action='store_true', help="Suppress summary output when writing to file")

    args = parser.parse_args()

    try:
        result = process_log_file(args.input_file)
    except FileNotFoundError:
        print(f"Error: File '{args.input_file}' not found.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)

    # Convert Pydantic model to JSON string (using model_dump_json)
    json_output = result.model_dump_json(indent=2)

    if args.output:
        try:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(json_output)
            if not args.quiet:
                print(f"Successfully parsed {result.metadata.valid_count} logs.")
                print(f"Found {result.metadata.invalid_count} errors.")
                print(f"Output written to {args.output}")
        except IOError as e:
            print(f"Error writing to file '{args.output}': {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print(json_output)

if __name__ == "__main__":
    main()
