import re
from typing import Optional, List, Dict, Any, Iterable
from datetime import datetime, timezone
from pydantic import ValidationError
from .schema import LogEntry

# Regex pattern to match the log format: [TIMESTAMP] [LEVEL] [TRACE_ID] MESSAGE
LOG_PATTERN = re.compile(
    r"^\[(?P<timestamp>.*?)\] \[(?P<level>.*?)\] \[(?P<trace_id>.*?)\] (?P<message>.*)$"
)

class LogParser:
    def __init__(self):
        pass

    def parse_line(self, line: str) -> Optional[LogEntry]:
        """
        Parses a single line of log text into a LogEntry object.
        Returns None if the line is malformed or invalid.
        Useful for individual line testing.
        """
        line = line.strip()
        if not line:
            return None

        match = LOG_PATTERN.match(line)
        if not match:
            return None

        data = match.groupdict()

        try:
            return LogEntry(**data)
        except ValidationError:
            return None

    def parse_file(self, lines: Iterable[str]) -> Dict[str, Any]:
        """
        Parses an iterable of lines and returns a structured dictionary
        containing metadata, valid logs, and errors.
        """
        valid_logs = []
        errors = []

        # specific timezone aware now
        start_time = datetime.now(timezone.utc)

        for i, line in enumerate(lines, start=1):
            line = line.strip()
            if not line:
                continue

            match = LOG_PATTERN.match(line)
            if not match:
                errors.append({
                    "line_number": i,
                    "raw_content": line,
                    "error": "Regex mismatch. Invalid format."
                })
                continue

            data = match.groupdict()

            try:
                entry = LogEntry(**data)
                valid_logs.append(entry.model_dump(mode='json'))
            except ValidationError as e:
                errors.append({
                    "line_number": i,
                    "raw_content": line,
                    "error": e.errors(include_url=False)
                })

        return {
            "metadata": {
                "timestamp": start_time.isoformat(),
                "total_processed": len(valid_logs) + len(errors),
                "valid_count": len(valid_logs),
                "error_count": len(errors)
            },
            "logs": valid_logs,
            "errors": errors
        }
