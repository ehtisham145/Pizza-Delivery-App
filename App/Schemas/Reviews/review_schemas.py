from pydantic import BaseModel,Field
from datetime import datetime
#1.======================Review Create Schema============================
class ReviewCreateSchema(BaseModel):
    order_id:str=Field(...,description="Id of your Order")
    rating:float=Field(...,ge=0, le=5,description="Reviews and Rating")
    comment:str=Field(...,description="Enter your Comment ")

    model_config={
        "from_attributes":True
    }

#2.======================Review Response Schema============================
class ReviewResponseSchema(BaseModel):
    rating:float=Field(...,description="Reviews and Rating")
    comment:str=Field(...,ge=0, le=5,description="Enter your Comment ")
    created_at:datetime
    full_name:str=Field(...,description="user name")

    model_config={
        "from_attributes":True
    }

ReviewResponseSchema.model_rebuild()