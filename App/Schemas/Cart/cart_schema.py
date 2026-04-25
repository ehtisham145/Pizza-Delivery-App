from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from App.Schemas.Menu.menu_schema import Pizza_Request

# 1. Add to Cart (User input ke liye)
class AddToCartSchema(BaseModel):
    pizza_id: int = Field(..., gt=0, description="Pizza ki ID honi chahiye")
    size_id: int = Field(..., gt=0)
    quantity: int = Field(default=1, gt=0, le=10) # Max 10 pizzas
    topping_ids: Optional[List[int]] = Field(default_factory=list)

# 2. Update Cart Item (Sirf quantity badalne ke liye)
class UpdateCartItemSchema(BaseModel):
    quantity: int = Field(..., gt=0, le=20)

# --- Response Schemas (Data wapas dikhane ke liye) ---

# Topping ka chota sa info schema
class ToppingInfo(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

# 3. Cart Item Response
class CartItemResponseSchema(BaseModel):
    id: int
    size: str
    quantity: int
    unit_price: float
    sub_total: float
    piza:Pizza_Request

    class Config:
        from_attributes = True

# 4. Full Cart Response
class CartResponseSchema(BaseModel):
    items: List[CartItemResponseSchema]
    total_price: float
    item_count: int

    class Config:
        from_attributes = True