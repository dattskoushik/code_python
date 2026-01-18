import re
import sys
from typing import List, Tuple, Dict, Any
from pydantic import ValidationError
from .models import LogEntry, LogError, ParsingResult, ParsingMetadata
from datetime import datetime, timezone

# Regex to capture raw fields before validation
# [TIMESTAMP] {SEVERITY} [MODULE_ID] - USER_ID: ACTION | MESSAGE
LOG_PATTERN = re.compile(
    r'^\[(?P<timestamp>.*?)\] \{(?P<severity>.*?)\} \[(?P<module>.*?)\] - (?P<user_id>.*?): (?P<action>.*?) \| (?P<message>.*)$'
)

def parse_line(line: str, line_number: int) -> Tuple[LogEntry | None, LogError | None]:
    """
    Parses a single line. Returns a tuple (LogEntry, LogError).
    One of them will be None.
    """
    line = line.strip()
    if not line:
        return None, LogError(line_number=line_number, raw_content=line, error_message="Empty line")

    match = LOG_PATTERN.match(line)
    if not match:
        return None, LogError(line_number=line_number, raw_content=line, error_message="Invalid log format")

    raw_data = match.groupdict()

    try:
        entry = LogEntry(
            timestamp=raw_data['timestamp'],
            severity=raw_data['severity'],
            module=raw_data['module'],
            user_id=raw_data['user_id'],
            action=raw_data['action'],
            message=raw_data['message']
        )
        return entry, None
    except ValidationError as e:
        # Pydantic validation error
        # Format the error message to be concise
        errors = "; ".join([f"{err['loc'][0]}: {err['msg']}" for err in e.errors()])
        return None, LogError(line_number=line_number, raw_content=line, error_message=errors)
    except Exception as e:
        return None, LogError(line_number=line_number, raw_content=line, error_message=str(e))

def process_log_file(file_path: str) -> ParsingResult:
    """
    Reads a file and returns a ParsingResult object.
    """
    valid_logs: List[LogEntry] = []
    errors: List[LogError] = []
    total_lines = 0

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f, 1):
                total_lines += 1
                entry, error = parse_line(line, i)
                if entry:
                    valid_logs.append(entry)
                elif error:
                    errors.append(error)
                else:
                    # Should not happen if parse_line is correct, but safe fallback
                    pass
    except FileNotFoundError:
        # In a real app we might raise or handle differently.
        # Here we just print and exit as per CLI style, or re-raise.
        raise

    metadata = ParsingMetadata(
        total_processed=total_lines,
        valid_count=len(valid_logs),
        invalid_count=len(errors),
        timestamp=datetime.now(timezone.utc)
    )

    return ParsingResult(metadata=metadata, logs=valid_logs, errors=errors)
