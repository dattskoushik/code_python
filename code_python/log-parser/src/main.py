import sys
import json
import argparse
from pathlib import Path
from .parser import LogParser

def main():
    parser = argparse.ArgumentParser(description="Parse log files into structured JSON.")
    parser.add_argument("file", help="Path to the log file to parse.")
    args = parser.parse_args()

    file_path = Path(args.file)
    if not file_path.exists():
        print(f"Error: File '{file_path}' not found.", file=sys.stderr)
        sys.exit(1)

    log_parser = LogParser()

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        parsed_logs = log_parser.parse_lines(lines)
        print(json.dumps(parsed_logs, indent=2))

    except Exception as e:
        print(f"Error processing file: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
