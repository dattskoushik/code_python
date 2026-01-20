import re
import json
from typing import Optional, List
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
        """
        line = line.strip()
        if not line:
            return None

        match = LOG_PATTERN.match(line)
        if not match:
            # In a real system, we might log this as a parsing error
            return None

        data = match.groupdict()

        try:
            return LogEntry(**data)
        except ValidationError:
            return None

    def parse_lines(self, lines: List[str]) -> List[dict]:
        """
        Parses a list of lines and returns a list of valid log dictionaries.
        """
        results = []
        for line in lines:
            entry = self.parse_line(line)
            if entry:
                # Convert to dict, serialize datetime to string
                results.append(json.loads(entry.model_dump_json()))
        return results
