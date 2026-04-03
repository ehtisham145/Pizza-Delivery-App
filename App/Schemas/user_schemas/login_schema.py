from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from App.Schemas.refresh_token_schema import RefreshTokenSchema
# ----------------- Login Request -----------------
class UserLoginSchema(BaseModel):
    """
    Schema for capturing login credentials.
    No complexity validation is performed here.
    """
    email: EmailStr
    password: str = Field(..., min_length=1) # Just ensure it is not empty

# ----------------- Login Response -----------------
class UserLoginResponseSchema(BaseModel):
    """
    Schema for the response after a successful login.
    NEVER return the password (even hashed) in the response.
    """
    refresh_token:RefreshTokenSchema
    access_token: str
    token_type: str = "bearer"
    email: EmailStr
    full_name:str

    class ConfigDict:
        from_attributes = True