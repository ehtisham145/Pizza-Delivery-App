from pydantic import BaseModel
from datetime import datetime
class RefreshTokenSchema(BaseModel):
    token:str   
    # IMPORTANT: The link to your User table
    user_id:int
    created_at:datetime
    expires_at:datetime
    is_revoked:bool

    class ConfigDict:
        form_attributes=True