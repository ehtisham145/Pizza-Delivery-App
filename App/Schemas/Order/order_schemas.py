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


class OrderHistorySchema(BaseModel):
    id:int
    full_name:str
    email:str
    order_relationship: List[OrderResponseSchema] = []
    class Config:
        from_attributes = True

