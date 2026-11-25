import re
from uuid import UUID
from fastapi import HTTPException,status
#---------------Validate your Password----------------------
def validate_password_strength(v: str) -> str:
    # 1. Explicit Length Check
    if len(v) < 8:
        raise ValueError("Password must be at least 8 characters long.")
    """
    Reusable logic for strong password validation.
    Ensures: 1 Upper, 1 Lower, 1 Digit, 1 Special Char, and Min 8 Length.
    """
    complexity_pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
    
    if not re.match(complexity_pattern, v):
        raise ValueError(
            "Password must contain at least one uppercase letter, "
            "one lowercase letter, one number, and one special character."
        )
    return v

# ----------------- REUSABLE PHONE VALIDATOR -----------------
def validate_phone_no(v: str) -> str:
    """
    Phone number validation for any country.
    Accepts an optional leading "+" (or "00" international prefix) followed by
    7–15 digits (the E.164 maximum). Spaces, dashes, dots and brackets are
    stripped first, e.g. "+44 7911 123456", "(555) 123-4567", "03001234567".
    """
    # 1. Clean the string (remove whitespace, dashes, dots, brackets)
    clean_number = re.sub(r"[\s\-\.\(\)]", "", v or "")

    # 2. "00" international prefix -> "+"
    if clean_number.startswith("00"):
        clean_number = "+" + clean_number[2:]

    # 3. Optional "+" then 7–15 digits
    if not re.fullmatch(r"\+?\d{7,15}", clean_number):
        raise ValueError(
            "Invalid phone number. Use 7–15 digits, optionally starting with + "
            "and your country code (e.g. +14155552671 or 03001234567)."
        )

    return clean_number

def validate_uuid(id_str: str, entity_name: str = "ID"):
    try:
        return UUID(id_str)
    except (ValueError, AttributeError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid {entity_name} format. Expected a valid UUID."
        )