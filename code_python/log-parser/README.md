# Day 01: Log Parser

**Project:** Log Parser
**Author:** dattskoushik
**Status:** Completed

## Overview

A production-grade log parser built with Python 3.12+ and Pydantic V2. This tool ingests raw log files, validates them against a strict schema, and outputs structured JSON containing valid logs, error details, and execution metadata.

## Features

- **Regex Extraction**: Efficiently captures fields from raw text logs.
- **Strict Validation**: Uses Pydantic V2 for robust type checking and validation (Timestamps, Enums, Regex patterns).
- **Structured Output**: Generates JSON reports with metadata, valid logs, and error details.
- **CLI Interface**: Simple command-line usage with file input and optional output file.

## Installation

```bash
cd code_python/log-parser
pip install -r requirements.txt
```

## Usage

Run the parser on a log file:

```bash
python3 -m src.main input.log -o output.json
```

If `-o` is omitted, output is printed to stdout.

## Schema

Input format:
```text
[TIMESTAMP] [LEVEL] [TRACE_ID] MESSAGE
```

Output format (JSON):
```json
{
  "metadata": {
    "timestamp": "...",
    "total_processed": 10,
    "valid_count": 9,
    "error_count": 1
  },
  "logs": [ ... ],
  "errors": [ ... ]
}
```
