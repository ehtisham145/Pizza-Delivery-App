from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict, field_validator
from App.Utils.constant import PizzaSizeEnum, PizzaToppingEnum, OrderStatusEnum

#1. ======================== Order Item Schema ========================
class OrderItemSchema(BaseModel):
    """Represents a single pizza line item in an order response."""

    pizza_id:   int             = Field(..., description="ID of the pizza")
    pizza_name: str             = Field(..., description="Name of the pizza")
    size_name:  PizzaSizeEnum   = Field(..., description="Selected size")
    quantity:   int             = Field(..., gt=0, description="Quantity ordered")
    unit_price: Decimal         = Field(..., gt=0, decimal_places=2, description="Price per unit")
    sub_total:  Decimal         = Field(..., gt=0, decimal_places=2, description="Line total")

    model_config = ConfigDict(from_attributes=True)

#2. ======================== Order Response Schema ========================
class OrderResponseSchema(BaseModel):
    """Schema returned when fetching a single order."""
    id:          str            = Field(..., description="UUID of the order")
    status:      OrderStatusEnum = Field(..., description="Current order status")
    total_price: Decimal        = Field(..., gt=0, decimal_places=2, description="Order total")
    notes:       Optional[str]  = Field(None, description="Delivery notes")
    created_at:  datetime
    updated_at:  Optional[datetime] = None
    order_item: List[OrderItemSchema]=[]

    model_config = ConfigDict(from_attributes=True)


#3. ======================== Order Update Status Schema ========================    
class OrderStatusUpdateSchema(BaseModel):
    new_status: OrderStatusEnum = Field(..., description="New status to apply to the order")
    @field_validator("new_status")
    def validate_status_transition(cls,v):
        if v == OrderStatusEnum.PENDING.value:
            raise ValueError("Cannot revert order status back to pending")
        return v
    model_config=ConfigDict(from_attributes=True)


#4. ======================== Order History Schema ========================
class OrderHistorySchema(BaseModel):
    """Schema for returning a user's full order history."""

    id:   int    = Field(..., description="ID of the user")
    full_name: str    = Field(..., description="Full name of the user")
    email:     str    = Field(..., description="Email of the user")
    order:    List[OrderResponseSchema] = []

    model_config = ConfigDict(from_attributes=True)

#5.=========================Place Order Schema=============================

class PlaceOrderSchema(BaseModel):
    address_id : int = Field(...,description="ID of your Address")
    notes: str | None