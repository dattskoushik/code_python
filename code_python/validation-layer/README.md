# Day 08: Validation Layer

## Project Overview
This project implements a **Universal Validation Layer** using Pydantic V2. It is designed to act as a robust data quality gate for ingesting complex datasets (e.g., e-commerce orders, customer profiles).

The system enforces strict schema definitions, performs cross-field validation logic, and aggregates errors into a structured report rather than failing on the first error.

## Features
- **Pydantic V2 Models**: Utilizes `field_validator` and `model_validator` for granular control.
- **Reusable Validators**: Regular expressions and logic for SKUs, phone numbers, and currencies separated into a utility module.
- **Batch Processing**: A `validate_batch` engine that processes lists of records and returns a clean separation of valid vs. invalid data.
- **Detailed Error Reporting**: Aggregates multiple errors per record with precise location paths.

## Structure
- `src/models.py`: Defines the `Customer`, `Product`, and `Order` schemas.
- `src/validators.py`: Contains pure python validation helpers.
- `src/processor.py`: Logic to apply models to raw data.
- `src/main.py`: Demo script.

## Usage

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run Demo**:
   ```bash
   python -m src.main
   ```

3. **Run Tests**:
   ```bash
   python -m pytest
   ```

## Tech Stack
- Python 3.12+
- Pydantic V2
- Pytest
- Email-Validator
