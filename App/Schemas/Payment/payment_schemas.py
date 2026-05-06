from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, field_validator
from App.Utils.constant import PaymentMethodEnum, PaymentStatusEnum

#1.===================================Payment Create Schema================================
class PaymentCreateSchema(BaseModel):
    order_id: str             = Field(..., description="ID of the order being paid")
    method:   PaymentMethodEnum = Field(..., description="Payment method (e.g. card, cash)")

    model_config={
        "from_attributes":True
    }
#2.===================================Payment Response Schema================================
class PaymentResponseSchema(BaseModel):
    id:str= Field(...,description="UUID of payment")
    order_id: str=Field(...,description="Linked Order ID")
    method: PaymentMethodEnum= Field(..., description="Payment method used")
    status: PaymentStatusEnum = Field(..., description="Current payment status")
    amount: Decimal=Field(...,gt=0,decimal_places=2,description="Total Amount to be paid")
    transaction_id: Optional[str]  = Field(None, description="External gateway transaction ID")
    paid_at: Optional[datetime]=None
    created_at: datetime
    updated_at: Optional[datetime]=None

    model_config={
        "from_attributes":True
    }

#3.===================================Payment Status Update Schema======================================
class PaymentStatusUpdateSchema(BaseModel):
    status: PaymentStatusEnum =Field(...,description="New Payment Status")
    @field_validator("status")
    @classmethod
    def prevent_reverting_to_pending(cls, v):
        if v == PaymentStatusEnum.PENDING:
            raise ValueError("Cannot revert payment status back to PENDING")
        return v

    model_config = ConfigDict(from_attributes=True)
