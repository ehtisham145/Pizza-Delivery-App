from pydantic import BaseModel, EmailStr, field_validator, Field
from typing import Optional
import re
class SignUpModel(BaseModel):
    id:Optional[int]=None
    username:str=Field(..., min_length=3, max_length=20)
    email:EmailStr
    password:str=Field(...,min_length=8)
    #---------------------Validate your Password----------------------
    @field_validator("password")
    @classmethod
    def validate_password_complexity(cls, v: str) -> str:
        # Requirements ka ek map bana lein (Professional approach)
        checks = {
            r'[A-Z]': 'one upper case character',
            r'[a-z]': 'one lower case character',
            r'\d': 'one integer',
            r'[!@#$%^&*(),.?":{}|<>]': 'one special character'
        }

        for pattern, message in checks.items():
            if not re.search(pattern, v):
                raise ValueError(f'Password must contain at least {message}')
        
        return v
    model_config={
        "from_attributes":True
    }


