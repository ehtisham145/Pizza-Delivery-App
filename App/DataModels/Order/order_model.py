import uuid
from sqlalchemy import Column,Integer,String,Boolean,ForeignKey,Enum as SQLEnum,DateTime,Float
from App.Utils.constant import PizzaSizeEnum,PizzaToppingEnum,PizzaCategoryEnum,OrderStatusEnum
from App.Database.database import Base
from datetime import datetime
from sqlalchemy.orm import relationship

#============================Order Table===============================
class Order_Model(Base):
    __tablename__="orders"
    id=Column(String,primary_key=True,default=lambda: str(uuid.uuid4()))
    user_id=Column(Integer,ForeignKey("users.id"),index=True) #Foreign  Key
    status=Column(SQLEnum(OrderStatusEnum),nullable=False)
    total_price=Column(Integer,nullable=False)
    address_id=Column(ForeignKey("delivery_addresses.id"))
    notes=Column(String,nullable=True)
    created_at=Column(DateTime,default=datetime.utcnow)
    updated_at=Column(DateTime,default=datetime.utcnow,onupdate=datetime.utcnow)

    #Relationship
    user_relationship=relationship("User",back_populates="order_relationship")
    order_item_relationship=relationship("Order_Item_Model",back_populates="order_relationship")
    address_relationship=relationship("Delivery_Model",back_populates="order_relationship")
    payment_relationship=relationship("Payment_Model",back_populates="order_relationship",uselist=False)

#============================Order Item Table===============================
class Order_Item_Model(Base):
    __tablename__="order_items"
    id=Column(Integer,primary_key=True)
    order_id = Column(String, ForeignKey("orders.id"), index=True) #Foreign  Key
    pizza_id=Column(Integer,ForeignKey("pizza.id"),index=True) #Foreign  Key
    pizza_name=Column(String,nullable=False)
    size_name=Column(SQLEnum(PizzaSizeEnum),nullable=False)
    quantity=Column(Integer,nullable=False,default=0)
    unit_price=Column(Float,nullable=False)
    sub_total=Column(Float,nullable=False)

    #Relationship
    order_relationship=relationship("Order_Model",back_populates="order_item_relationship")
    pizza_relationship=relationship("Pizza_Model",back_populates="order_relationship")
    topping_relationship=relationship("Order_Topping_Model",back_populates="order_item_relationship")



#============================Order Item Topping Table===============================
class Order_Topping_Model(Base):
    __tablename__="order_item_toppings"
    id=Column(Integer,primary_key=True,index=True)
    notes=Column(String,nullable=False)
    order_item_id=Column(Integer,ForeignKey("order_items.id"))
    topping_name=Column(SQLEnum(PizzaToppingEnum),nullable=False)
    extra_price=Column(Float,nullable=False)

    #Relationship
    order_item_relationship=relationship("Order_Item_Model",back_populates="topping_relationship")