from pydantic import BaseModel,Field
from datetime import datetime
class RefreshTokenRequest(BaseModel):
    refresh_token:str   
    # IMPORTANT: The link to your User table
    user_id:int=Field(...,description="ID of user")
    created_at:datetime
    expires_at:datetime
    is_revoked:bool

    model_config={
        "from_attributes":True
    }