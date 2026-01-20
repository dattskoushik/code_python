import pytest
from src.parser import LogParser
from src.schema import LogLevel

@pytest.fixture
def parser():
    return LogParser()

def test_parse_valid_line(parser):
    line = "[2023-10-27T10:00:00Z] [INFO] [abc-123] System started."
    entry = parser.parse_line(line)

    assert entry is not None
    assert entry.timestamp.year == 2023
    assert entry.level == LogLevel.INFO
    assert entry.trace_id == "abc-123"
    assert entry.message == "System started."

def test_parse_invalid_format(parser):
    # Missing brackets
    line = "2023-10-27T10:00:00Z INFO abc-123 System started."
    entry = parser.parse_line(line)
    assert entry is None

def test_parse_invalid_timestamp(parser):
    line = "[invalid-date] [INFO] [abc-123] Message"
    entry = parser.parse_line(line)
    assert entry is None

def test_parse_invalid_level(parser):
    line = "[2023-10-27T10:00:00Z] [CRITICAL] [abc-123] Message" # CRITICAL is not in Enum
    entry = parser.parse_line(line)
    assert entry is None

def test_parse_invalid_trace_id(parser):
    line = "[2023-10-27T10:00:00Z] [INFO] [invalid_trace!] Message" # contains special chars not allowed
    entry = parser.parse_line(line)
    assert entry is None

def test_parse_multiple_lines(parser):
    lines = [
        "[2023-10-27T10:00:00Z] [INFO] [abc-123] Line 1",
        "Invalid Line",
        "[2023-10-27T10:01:00Z] [ERROR] [def-456] Line 2"
    ]
    results = parser.parse_lines(lines)

    assert len(results) == 2
    assert results[0]["message"] == "Line 1"
    assert results[1]["message"] == "Line 2"
    assert results[1]["level"] == "ERROR"
