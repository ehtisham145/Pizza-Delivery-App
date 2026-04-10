import re
from typing import Annotated
from App.Utils.validator import validate_password_strength,validate_phone_no
from pydantic import BaseModel, EmailStr, Field,AfterValidator, Field
from enum import Enum
from pydantic import BaseModel, Field, EmailStr
# ----------------- REUSABLE TYPES -----------------
# This creates a "Type" that is a string, but ALWAYS runs your function after checking the string
PasswordStr = Annotated[str, AfterValidator(validate_password_strength)]
PhoneStr = Annotated[str, AfterValidator(validate_phone_no)]

#first of all check whether user enter detail is string and if not str such as tuple list or dict 
#  an error will occur before applying validation 

# ----------------- MAIN REGISTER SCHEMA -----------------
class UserRegisterSchema(BaseModel):
    """
    Final Registration Schema inheriting Phone and Password logic.
    Follows DRY (Don't Repeat Yourself) principle.
    """
    full_name: str = Field(..., min_length=5, max_length=20)
    email: EmailStr
    phone_number:PhoneStr
    password:PasswordStr
    role:str

    class ConfigDict:
        from_attributes = True
        str_strip_whitespace = True  # Automatically trims spaces from all strings



class UserResponseSchema(BaseModel):
    id: int  # Added ID
    full_name: str = Field(..., min_length=5, max_length=25)
    email: EmailStr
    phone_number: str  
    role: str
    is_active: bool
    
    class ConfigDict:
        from_attributes = True
        str_strip_whitespace = True  # Automatically trims spaces from all strings
