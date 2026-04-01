from pydantic import BaseModel, Field
from App.Schemas.user_schemas.register_schema import PhoneNumber
# ----------------- Update Request -----------------
class UserUpdateSchema(PhoneNumber):
    """
    Schema for capturing Updating credentials.
    No complexity validation is performed here.
    """
    full_name: str = Field(..., min_length=5, max_length=20)
    
    class ConfigDict:
        from_attributes = True
        str_strip_whitespace = True

        
#----------------------Response-----------------------
class UserUpdateResponseSchema(BaseModel):
    """
    Schema for the data sent back to the user after a successful update.
    We don't need to inherit validation here, just show the data.
    """
    id: int
    full_name: str
    phone_number: str
    email: str  # Usually included so the user sees their current email

    class ConfigDict:
        from_attributes = True # Allows Pydantic to read SQLAlchemy objects