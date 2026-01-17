# Day 01: Log Parser

A robust, regex-based log parser that converts unstructured log files into structured JSON data.

## Features

- **Custom Format Support**: Parses logs in the format `[TIMESTAMP] {SEVERITY} [MODULE] - USER: ACTION | MESSAGE`.
- **Strict Validation**: Validates timestamps, severity levels, and structural integrity.
- **Error Reporting**: detailed reporting of invalid lines including line numbers and error reasons.
- **JSON Output**: Produces clean JSON output suitable for ingestion into other tools.

## Usage

### Prerequisites

- Python 3.8+

### Running the Parser

```bash
python3 parser.py input_file.log [-o output_file.json] [-q]
```

**Arguments:**
- `input_file`: Path to the raw log file.
- `-o`, `--output`: (Optional) Path to write the JSON output. If omitted, prints to stdout.
- `-q`, `--quiet`: (Optional) Suppress summary output when writing to a file.

### Example

```bash
# Run on sample data
python3 parser.py sample.log -o parsed_logs.json
```

## Testing

Run the unit tests:

```bash
python3 tests.py
```

## Project Structure

- `parser.py`: Core logic for parsing and validation.
- `sample.log`: Sample log file with valid and invalid entries.
- `tests.py`: Unit tests.
