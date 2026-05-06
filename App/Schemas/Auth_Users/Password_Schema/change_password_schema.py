from pydantic import BaseModel,AfterValidator,Field
from typing import Annotated
from App.Utils.validator import validate_password_strength 

PasswordStr=Annotated[str,AfterValidator(validate_password_strength)]

#---------------------Change Password Model-------------------------
# Schemas
class ChangePasswordSchema(BaseModel):
    old_password: PasswordStr=Field(...,description="Old Password")
    new_password: PasswordStr=Field(...,description="New Password")
    confirm_new_password: PasswordStr=Field(...,description="Confirm New Password")