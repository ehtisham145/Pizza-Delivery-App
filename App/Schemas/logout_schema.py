from pydantic import BaseModel
class LogoutRequestSchema(BaseModel):
    refresh_token: str