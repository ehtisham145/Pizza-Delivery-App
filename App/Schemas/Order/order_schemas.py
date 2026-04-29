from pydantic import BaseModel, Field, ConfigDict,computed_field
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from App.Utils.constant import PizzaSizeEnum, PizzaToppingEnum,OrderStatusEnum
from App.Schemas.Menu.menu_schema import Pizza_Request
from enum import Enum
class OrderItemSchema(BaseModel):
    pizza_name:str
    pizza_id: int
    size_name: PizzaSizeEnum
    unit_price: float
    quantity: int
    sub_total: float 

    model_config = ConfigDict(from_attributes=True)

class OrderResponseSchema(BaseModel):
    status: OrderStatusEnum
    total_price: float
    created_at: datetime
    order_item_relationship: list[OrderItemSchema] 

    model_config = ConfigDict(from_attributes=True)

    
class OrderStatusUpdateSchema(BaseModel):
    new_status: OrderStatusEnum
    model_config=ConfigDict(from_attributes=True)


# 2. Place Order
class PlaceOrderSchema(BaseModel):
    address_id: int = Field(..., gt=0, description="Valid ID of your Address")
    payment_method_id: int = Field(..., gt=0, description="Payment Method ID")
    items: List[OrderItemSchema] = Field(..., min_length=1, description="List of pizzas ordered")
    notes: Optional[str] = Field(None, max_length=500)


