import re

def is_valid_phone(phone: str) -> bool:
    """
    Validates if a phone number matches E.164 format.
    Example: +14155552671
    """
    # Regex: + followed by 1 to 15 digits
    pattern = r"^\+[1-9]\d{1,14}$"
    return bool(re.match(pattern, phone))

def luhn_check(card_number: str) -> bool:
    """
    Validates a credit card number using the Luhn algorithm.
    """
    if not card_number.isdigit():
        return False

    digits = [int(d) for d in card_number]
    checksum = 0
    is_second = False

    # Process digits from right to left
    for digit in reversed(digits):
        if is_second:
            digit = digit * 2
            if digit > 9:
                digit -= 9
        checksum += digit
        is_second = not is_second

    return checksum % 10 == 0

def is_strong_password(password: str) -> bool:
    """
    Validates password strength:
    - At least 8 characters
    - At least one uppercase
    - At least one lowercase
    - At least one digit
    - At least one special character
    """
    if len(password) < 8:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"\d", password):
        return False
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False
    return True
