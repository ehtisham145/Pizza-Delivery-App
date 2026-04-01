import re
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional

# ----------------- REUSABLE VALIDATION MIXINS -----------------

class PhoneNumber(BaseModel):
    """
    Base class for Pakistani phone number validation.
    Can be reused in Profile Update or Registration schemas.
    """
    phone_number: str = Field(..., json_schema_extra={"examples": ["03001234567"]})

    @field_validator("phone_number")
    @classmethod
    def validate_pk_number(cls, v: str) -> str:
        # Remove whitespaces and dashes
        clean = re.sub(r"[\s\-]", "", v)
        
        # Regex for Pakistani mobile formats (03xx, 923xx, +923xx)
        pk_pattern = r"^(?:\+92|92|0)?3\d{9}$"
        
        if not re.match(pk_pattern, clean):
            raise ValueError("Invalid Pakistani phone number format.")
        
        return clean

class Password(BaseModel):
    """
    Base class for strong password validation.
    Ensures 1 Upper, 1 Lower, 1 Digit, and 1 Special Character.
    """
    password: str = Field(..., min_length=8)

    @field_validator("password")
    @classmethod
    def validate_complexity(cls, v: str) -> str:
        # Regex lookahead for complexity requirements
        complexity_pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
        
        if not re.match(complexity_pattern, v):
            raise ValueError(
                "Password must contain at least one uppercase letter, "
                "one lowercase letter, one number, and one special character."
            )
        return v

# ----------------- MAIN REGISTER SCHEMA -----------------

class UserRegisterSchema(PhoneNumber,Password):
    """
    Final Registration Schema inheriting Phone and Password logic.
    Follows DRY (Don't Repeat Yourself) principle.
    """
    full_name: str = Field(..., min_length=5, max_length=20)
    email: EmailStr


    class ConfigDict:
        from_attributes = True
        str_strip_whitespace = True  # Automatically trims spaces from all strings


#---------------------------------Respone Schema----------------------------------
class UserResponseSchema(PhoneNumber,Password):
    full_name: str = Field(..., min_length=5, max_length=20)
    email: EmailStr


