# Day 01: Log Parser

**Project:** Log Parser
**Author:** dattskoushik
**Status:** Completed

## Overview

A production-grade log parser built with Python 3.12+ and Pydantic V2. This tool ingests raw log files, validates them against a strict schema, and outputs structured JSON.

## Features

- **Regex Extraction**: Efficiently captures fields from raw text logs.
- **Strict Validation**: Uses Pydantic V2 for robust type checking and validation (Timestamps, Enums, Regex patterns).
- **Structured Output**: Generates JSON reports with metadata, valid logs, and error details.
- **CLI Interface**: Simple command-line usage.

## Installation

```bash
cd code_python/log-parser
pip install -r requirements.txt
```

## Usage

Run the parser on the provided sample log:

```bash
python3 -m src.main sample.log -o output.json
```

Or run tests:

```bash
python3 -m unittest discover tests
```

## Schema

Input format:
```text
[TIMESTAMP] {SEVERITY} [MODULE] - USER_ID: ACTION | MESSAGE
```

Output format (JSON):
```json
{
  "metadata": { ... },
  "logs": [ ... ],
  "errors": [ ... ]
}
```
