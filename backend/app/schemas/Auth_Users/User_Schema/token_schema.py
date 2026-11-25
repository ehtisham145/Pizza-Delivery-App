from pydantic import BaseModel

class TokenSchema(BaseModel):
    access_token:str
    refresh_token:str
    token_type:str="bearer"

    model_config={
        "form-attributes":"True",
        "json_schema_extra": {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1...",
                "refresh_token": "eyJhbGciOiJIUzI1...",
                "token_type": "bearer"
            }
        }
    }
