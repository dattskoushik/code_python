"""
validators.py

Reusable validation logic and regex patterns.
"""
import re
from typing import Optional

# Regex Patterns
SKU_PATTERN = re.compile(r"^[A-Z0-9]{3,}-[A-Z0-9]{3,}$")
PHONE_PATTERN = re.compile(r"^\+[1-9]\d{1,14}$")
CURRENCY_CODES = {"USD", "EUR", "GBP", "JPY", "CAD", "AUD"}

def validate_sku(sku: str) -> bool:
    """
    Validates that the SKU follows the pattern: XXX-XXX (alphanumeric).
    """
    if not sku:
        return False
    return bool(SKU_PATTERN.match(sku))

def validate_phone_number(phone: str) -> bool:
    """
    Validates phone number format (E.164-ish).
    Must start with + and contain digits.
    """
    if not phone:
        return False
    return bool(PHONE_PATTERN.match(phone))

def validate_currency_code(code: str) -> bool:
    """
    Validates if the currency code is in the allowed list.
    """
    return code in CURRENCY_CODES
