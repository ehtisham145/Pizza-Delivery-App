from pydantic import BaseModel
from datetime import datetime
class RefreshTokenRequest(BaseModel):
    refresh_token:str   
    # IMPORTANT: The link to your User table so that you can word
    user_id:int
    created_at:datetime
    expires_at:datetime
    is_revoked:bool

    model_config={
        "form_attributes":True
    }