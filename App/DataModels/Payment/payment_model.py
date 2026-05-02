from sqlalchemy import Column,Integer,String,DateTime,Float,Enum as SQLEnum,ForeignKey
from App.Database.database import Base
from sqlalchemy.orm import relationship
import uuid
from uuid import UUID
from datetime import datetime
from App.Utils.constant import PaymentMethodEnum,PaymentStatusEnum
#1.=========================Payment Model============================

class Payment_Model(Base):
    __tablename__="payments"
    id=Column(UUID(as_uuid=True),primary_key=True,index=True,default=uuid.uuid4)
    order_id=Column(Integer,ForeignKey("orders.id"),index=True,unique=True)
    user_id=Column(Integer,ForeignKey("users.id"),index=True)
    method=Column(SQLEnum(PaymentMethodEnum),nullable=False)
    status=Column(SQLEnum(PaymentStatusEnum),default=PaymentStatusEnum.PENDING,nullable=False)
    amount=Column(Float,nullable=False)
    paid_at=Column(DateTime,nullable=True)
    created_at=Column(DateTime,default=datetime.utcnow)

    #Relationship
    payment_relationship=relationship("Order_Model",back_populates="order_relationship")
    user_relationship=relationship("User",back_populates="payment_relationship")