import sys
import json
import argparse
from pathlib import Path
from .parser import LogParser

def main():
    parser = argparse.ArgumentParser(description="Parse log files into structured JSON.")
    parser.add_argument("file", help="Path to the log file to parse.")
    parser.add_argument("-o", "--output", help="Path to the output JSON file.", default=None)
    args = parser.parse_args()

    file_path = Path(args.file)
    if not file_path.exists():
        print(f"Error: File '{file_path}' not found.", file=sys.stderr)
        sys.exit(1)

    log_parser = LogParser()

    try:
        # Use generator to read file line by line
        with open(file_path, "r", encoding="utf-8") as f:
            result = log_parser.parse_file(f)

        output_json = json.dumps(result, indent=2)

        if args.output:
            with open(args.output, "w", encoding="utf-8") as out_f:
                out_f.write(output_json)
            print(f"Successfully wrote output to {args.output}")
        else:
            print(output_json)

    except Exception as e:
        print(f"Error processing file: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
