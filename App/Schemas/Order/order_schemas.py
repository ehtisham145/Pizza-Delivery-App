from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from App.Utils.constant import OrderStatusEnum, PizzaSizeEnum, PizzaToppingEnum

class OrderItemSchema(BaseModel):
    pizza_id: int = Field(..., gt=0, description="Pizza unique ID")
    size: PizzaSizeEnum
    toppings: List[PizzaToppingEnum] = [] 
    quantity: int = Field(..., gt=0)

    subtotal: float = Field(..., gt=0)

    model_config = ConfigDict(from_attributes=True)

# 2. Place Order
class PlaceOrderSchema(BaseModel):
    address_id: int = Field(..., gt=0, description="Valid ID of your Address")
    payment_method_id: int = Field(..., gt=0, description="Payment Method ID")
    items: List[OrderItemSchema] = Field(..., min_length=1, description="List of pizzas ordered")
    notes: Optional[str] = Field(None, max_length=500)

class OrderStatusUpdateSchema(BaseModel):
    new_status: OrderStatusEnum

    model_config=ConfigDict(from_attributes=True)


class OrderResponseSchema(BaseModel):
    id: int
    status: OrderStatusEnum
    total_price: float = Field(..., gt=0)
    

    items: List[OrderItemSchema] 
    
    # Address and Payment 
    address_id: int 
    payment_method_id: int
    
    created_at: datetime

    # SQLAlchemy models se direct data uthane ke liye
    model_config = ConfigDict(from_attributes=True)