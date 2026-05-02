from App.Database.database import Base,get_db
from sqlalchemy import Column,Integer,String,Boolean,ForeignKey,Enum as SQLEnum,Float,DateTime
from App.Utils.constant import AddressStatusEnum
from fastapi import Depends
from sqlalchemy.orm import Session,relationship
from enum import Enum
from datetime import datetime

#=================================Delivery Address=============================
class Delivery_Model(Base):
    __tablename__="delivery_addresses"
    id=Column(Integer,primary_key=True,index=True)
    user_id=Column(Integer,ForeignKey("users.id"))
    label=Column(SQLEnum(AddressStatusEnum),nullable=False)
    street=Column(String,nullable=False)
    city=Column(String,nullable=False)
    zip_code=Column(String,nullable=False)
    is_default=Column(Boolean,default=False)
    created_at=Column(DateTime,default=datetime.utcnow)

    #relationship
    user_relationship=relationship("User",back_populates="address_relationship")
    order_relationship=relationship("Order_Model",back_populates="address_relationship")