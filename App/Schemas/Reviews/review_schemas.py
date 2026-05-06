from pydantic import BaseModel,Field
from datetime import datetime,timezone
from typing import Optional
#1.======================Review Create Schema============================
class ReviewCreateSchema(BaseModel):
    order_id: str   = Field(..., description="ID of the order being reviewed")
    pizza_id: int   = Field(..., description="ID of the pizza being reviewed")
    rating:   float = Field(..., ge=1, le=5, description="Rating from 1 to 5")
    omment:  Optional[str] = Field(None, max_length=1000, description="Optional comment")
    model_config={
        "from_attributes":True
    }

#2.======================Review Response Schema============================
class ReviewResponseSchema(BaseModel):
    id:         int   = Field(..., description="Review ID")
    order_id:   str   = Field(..., description="Associated order ID")
    rating:     float = Field(..., ge=1, le=5, description="Rating from 1 to 5")
    comment:    Optional[str] = Field(None, description="Reviewer's comment")
    full_name:  str   = Field(..., description="Name of the reviewer")
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config={
        "from_attributes":True
    }


