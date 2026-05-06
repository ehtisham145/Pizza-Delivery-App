from pydantic import BaseModel,Field
from App.Utils.validator import validate_phone_no
from typing import Annotated
from pydantic import AfterValidator

PhoneStr = Annotated[str, AfterValidator(validate_phone_no)]
# ----------------- Update Request -----------------
class UserUpdateSchema(BaseModel):
    """
    Schema for capturing Updating credentials.
    No complexity validation is performed here.
    """
    full_name: str = Field(..., min_length=5, max_length=20,description="Name of User")
    phone_number:PhoneStr=Field(...,description="Phone Number of User")
    model_config={
        "form_attributes":True
    }
        
