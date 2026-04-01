from pydantic import BaseModel,AfterValidator
from typing import Annotated
from App.Utils.validator import validate_password_strength 

PasswordStr=Annotated[str,AfterValidator(validate_password_strength)]

#---------------------Change Password Model-------------------------
class Password_Change_Schema(BaseModel):
    old_password:str
    new_password:PasswordStr
    confirm_new_password:str