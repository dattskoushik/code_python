#!/usr/bin/env python3
"""
Day 01: Log Parser
Author: dattskoushik

Description:
    A robust log parser that ingests raw log files with a specific format,
    validates the schema and values, and outputs structured JSON.

    Log Format:
    [TIMESTAMP] {SEVERITY} [MODULE_ID] - USER_ID: ACTION | MESSAGE
"""

import re
import json
import sys
import argparse
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

# Constants
VALID_SEVERITIES = {'INFO', 'WARN', 'ERROR', 'DEBUG', 'CRITICAL'}
LOG_PATTERN = re.compile(
    r'^\[(?P<timestamp>.*?)\] \{(?P<severity>.*?)\} \[(?P<module>.*?)\] - (?P<user_id>.*?): (?P<action>.*?) \| (?P<message>.*)$'
)

def parse_line(line: str, line_number: int) -> Dict[str, Any]:
    """
    Parses a single line of log.

    Returns:
        A dictionary containing the parsed data or error details.
    """
    line = line.strip()
    if not line:
        return {'valid': False, 'line': line_number, 'error': 'Empty line'}

    match = LOG_PATTERN.match(line)
    if not match:
        return {'valid': False, 'line': line_number, 'error': 'Invalid format', 'content': line}

    data = match.groupdict()

    # Validation
    # 1. Timestamp
    try:
        dt = datetime.strptime(data['timestamp'], '%Y-%m-%d %H:%M:%S')
        data['timestamp_iso'] = dt.isoformat()
    except ValueError:
        return {'valid': False, 'line': line_number, 'error': 'Invalid timestamp format', 'content': line}

    # 2. Severity
    if data['severity'] not in VALID_SEVERITIES:
        return {'valid': False, 'line': line_number, 'error': f"Invalid severity: {data['severity']}", 'content': line}

    # 3. User ID (Basic check)
    if not data['user_id'].startswith('U'):
         return {'valid': False, 'line': line_number, 'error': f"Invalid User ID format: {data['user_id']}", 'content': line}

    return {
        'valid': True,
        'line': line_number,
        'timestamp': data['timestamp_iso'],
        'severity': data['severity'],
        'module': data['module'],
        'user_id': data['user_id'],
        'action': data['action'],
        'message': data['message']
    }

def process_logs(input_file: str, output_file: Optional[str] = None, quiet: bool = False) -> None:
    """
    Reads logs from input_file, parses them, and writes JSON to output_file or stdout.
    """
    results = []

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f, 1):
                result = parse_line(line, i)
                results.append(result)
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found.", file=sys.stderr)
        sys.exit(1)

    # Separate valid and invalid for reporting
    valid_logs = [r for r in results if r['valid']]
    invalid_logs = [r for r in results if not r['valid']]

    output_data = {
        'metadata': {
            'total_processed': len(results),
            'valid_count': len(valid_logs),
            'invalid_count': len(invalid_logs),
            'timestamp': datetime.now(timezone.utc).isoformat()
        },
        'logs': valid_logs,
        'errors': invalid_logs
    }

    json_output = json.dumps(output_data, indent=2)

    if output_file:
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(json_output)
            if not quiet:
                print(f"Successfully parsed {len(valid_logs)} logs. Output written to {output_file}")
                if invalid_logs:
                    print(f"Found {len(invalid_logs)} errors. Check output for details.")
        except IOError as e:
            print(f"Error writing to file '{output_file}': {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print(json_output)

def main():
    parser = argparse.ArgumentParser(description="Day 01 Log Parser - dattskoushik")
    parser.add_argument('input_file', help="Path to the log file")
    parser.add_argument('-o', '--output', help="Path to output JSON file")
    parser.add_argument('-q', '--quiet', action='store_true', help="Suppress summary output when writing to file")

    args = parser.parse_args()
    process_logs(args.input_file, args.output, args.quiet)

if __name__ == "__main__":
    main()
