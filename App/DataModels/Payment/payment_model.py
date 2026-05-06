import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Numeric, ForeignKey
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import relationship
from App.Database.database import Base
from App.Utils.constant import PaymentMethodEnum, PaymentStatusEnum
#1.=========================Payment Model============================

class Payment_Model(Base):
    __tablename__="payments"
    id ==       Column(String,primary_key=True,default=lambda: str(uuid.uuid4()))
    order_id =   Column(String,ForeignKey("orders.id", ondelete="CASCADE"),index=True,unique=True)
    user_id =    Column(Integer,ForeignKey("users.id", ondelete="CASCADE"),index=True)
    transaction_id = Column(String(255), unique=True, index=True, nullable=True)
    method =    Column(SQLEnum(PaymentMethodEnum),nullable=False)
    status =    Column(SQLEnum(PaymentStatusEnum),default=PaymentStatusEnum.PENDING,nullable=False)
    amount =    Column(Numeric(10,2),nullable=False)
    paid_at =   Column(DateTime,nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                    onupdate=lambda: datetime.now(timezone.utc))

    #Relationship
    order   = relationship("Order_Model",back_populates="payment")
    user =  relationship("User",back_populates="payment")

    def __repr__(self):
        return f"<Payment id={self.id} order_id={self.order_id} status={self.status} amount={self.amount}>"