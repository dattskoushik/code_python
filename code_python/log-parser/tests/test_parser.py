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

def test_parse_file_valid_lines(parser):
    lines = [
        "[2023-10-27T10:00:00Z] [INFO] [abc-123] Line 1",
        "[2023-10-27T10:01:00Z] [ERROR] [def-456] Line 2"
    ]
    result = parser.parse_file(lines)

    assert result["metadata"]["valid_count"] == 2
    assert result["metadata"]["error_count"] == 0
    assert len(result["logs"]) == 2
    assert len(result["errors"]) == 0

    assert result["logs"][0]["message"] == "Line 1"
    assert result["logs"][1]["message"] == "Line 2"
    assert result["logs"][1]["level"] == "ERROR"

def test_parse_file_mixed_lines(parser):
    lines = [
        "[2023-10-27T10:00:00Z] [INFO] [abc-123] Line 1",
        "Invalid Line",
        "[2023-10-27T10:01:00Z] [ERROR] [def-456] Line 2"
    ]
    result = parser.parse_file(lines)

    assert result["metadata"]["valid_count"] == 2
    assert result["metadata"]["error_count"] == 1
    assert len(result["logs"]) == 2
    assert len(result["errors"]) == 1

    assert result["errors"][0]["line_number"] == 2
    assert result["errors"][0]["raw_content"] == "Invalid Line"
    assert "Regex mismatch" in result["errors"][0]["error"]

def test_parse_file_validation_error(parser):
    lines = [
        "[2023-10-27T10:00:00Z] [CRITICAL] [abc-123] Message" # CRITICAL not valid
    ]
    result = parser.parse_file(lines)

    assert result["metadata"]["valid_count"] == 0
    assert result["metadata"]["error_count"] == 1
    # Check that error details are present. The exact string representation might vary slightly.
    error_list = result["errors"][0]["error"]
    assert isinstance(error_list, list) # Pydantic returns list of dicts
    assert any(e['type'] == 'enum' for e in error_list)
