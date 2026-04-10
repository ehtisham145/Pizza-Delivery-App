import re

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
    Reusable logic for Pakistani phone number validation.
    Supports formats: 03xxxxxxxxx, 923xxxxxxxxx, +923xxxxxxxxx.
    """
    # 1. Clean the string (Remove whitespaces, dashes, or brackets)
    clean_number = re.sub(r"[\s\-\(\)]", "", v)
    
    # 2. Regex for Pakistani mobile formats
    pk_pattern = r"^(?:\+92|92|0)?3\d{9}$"
    
    if not re.match(pk_pattern, clean_number):
        raise ValueError(
            "Invalid phone number. Please use a valid format "
            "(e.g., 03001234567 or +923001234567)."
        )
    
    return clean_number
