from pydantic import BaseModel,Field
from App.Utils.constant import PaymentMethodEnum,PaymentStatusEnum
from enum import Enum
from datetime import datetime
from typing import Optional


#1.===================================Payment Response Schema================================
class PaymentResponseSchema(BaseModel):
    id:str=Field(...,description="UUID of payment")
    order_id:int=Field(...,gt=0,description="Linked Order ID")
    method:PaymentMethodEnum
    status:PaymentStatusEnum
    amount:float=Field(...,gt=0,description="Total Amount to be paid")
    paid_at:Optional[datetime]=None

    model_config={
        "from_attributes":True
    }

#2.===================================Payment Status Update Schema======================================
class PaymentStatusUpdateSchema(BaseModel):
    status:PaymentStatusEnum
