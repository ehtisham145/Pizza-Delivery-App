from pydantic import BaseModel
from datetime import datetime
class RefreshTokenSchema(BaseModel):
    refresh_token:str   
    # IMPORTANT: The link to your User table
    user_id:int
    created_at:datetime
    expires_at:datetime
    is_revoked:bool

    model_config={
        "form_attributes":True
    }