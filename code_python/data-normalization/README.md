# Day 07: Data Normalization

## Project Overview
This project implements a Data Normalization pipeline that transforms raw, denormalized CSV data into a structured 3NF (Third Normal Form) relational schema using PostgreSQL (simulated via SQLAlchemy/SQLite for this environment).

## Features
- **Raw Data Generation**: Simulates a messy legacy export (denormalized).
- **Relational Modeling**: Defines `Customer`, `Product`, `Order`, and `OrderItem` models.
- **Normalization ETL**:
    - Extracts unique entities.
    - Handles relationships and foreign keys.
    - Idempotent execution (safe to run multiple times).

## Usage

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Generate Data**:
   ```bash
   python -m src.generator
   ```

3. **Run Normalization**:
   ```bash
   python -m src.main
   ```

## Tech Stack
- Python 3.12+
- SQLAlchemy (ORM)
- Pytest
