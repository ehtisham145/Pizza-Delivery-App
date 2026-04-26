from sqlalchemy import Column,Integer,String,Boolean,ForeignKey,Enum as SQLEnum,DateTime,Float
from App.Utils.constant import PizzaSizeEnum
from App.Database.database import Base
from datetime import datetime
#============================Order Table===============================
class Order_Model(Base):
    __tablename__="orders"
    id=Column(Integer,primary_key=True,index=True)
    user_id=Column(Integer,ForeignKey("users.id"),index=True) #Foreign  Key
    address_id=Column(Integer,ForeignKey("address.id"),index=True) #Foreign  Key
    status=Column(SQLEnum(Order_Status_Enum),nullable=False)
    total_price=Column(Integer,nullable=False)
    notes=Column(String,nullable=True)
    created_at=Column(DateTime,default=datetime.utcnow)
    updated_at=Column(DateTime,default=datetime.utcnow,onupdate=datetime.utcnow)

#============================Order Item Table===============================
class Order_Item_Model(Base):
    id=Column(Integer,primary_key=True)
    order_id=Column(Integer,ForeignKey("orders.id"),index=True) #Foreign  Key
    pizza_id=Column(Integer,ForeignKey("pizza.id"),index=True) #Foreign  Key
    pizza_name=Column()
    size_name=Column(SQLEnum(PizzaSizeEnum),nullable=False)
    quantity=Column(Integer,nullable=False,default=0)
    unit_price=Column(Float,nullable=False)
    sub_total=Column(Float,nullable=False)
