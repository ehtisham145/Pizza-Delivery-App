from pydantic import BaseModel,AfterValidator
from typing import Annotated
from App.Utils.validator import validate_password_strength 

PasswordStr=Annotated[str,AfterValidator(validate_password_strength)]

#---------------------Change Password Model-------------------------
# Schemas
class ChangePasswordSchema(BaseModel):
    old_password: PasswordStr
    new_password: PasswordStr
    confirm_new_password: PasswordStr