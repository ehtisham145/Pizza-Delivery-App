import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Numeric, Index
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import relationship
from App.Utils.constant import PizzaSizeEnum, PizzaToppingEnum, OrderStatusEnum
from App.Database.database import Base

#1.============================Order Table===============================
class Order_Model(Base):
    __tablename__="orders"
    id =      Column(String,primary_key=True,default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer,ForeignKey("users.id"),ondelete="CASCADE",nullabl=False,index=True) #Foreign  Key
    status =  Column(SQLEnum(OrderStatusEnum),nullable=False)
    total_price= Column(Numeric(10,2),nullable=False)
    address_id=  Column(ForeignKey("delivery_addresses.id"),index=True,nullable=False, ondelete="SET NULL")
    notes =      Column(String,nullable=True)
    created_at  = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at  = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                         onupdate=lambda: datetime.now(timezone.utc))

    #Relationship
    user = relationship("User",back_populates="order",passive_deletes=True)
    order_item = relationship("Order_Item_Model",back_populates="order", cascade="all, delete-orphan", lazy="select")
    address = relationship("Delivery_Model",back_populates="order")
    payment = relationship("Payment_Model",back_populates="order",uselist=False)
    review = relationship("Review_Model",back_populates="order",uselist=False)

    def __repr__(self):
        return f"<Order id={self.id} user_id={self.user_id} status={self.status}>"

#2.============================Order Item Table===============================
class Order_Item_Model(Base):
    __tablename__="order_items"
    id =        Column(Integer,primary_key=True)
    order_id =  Column(String, ForeignKey("orders.id",on_delete="CASCADE") ,index=True,nullable=False) #Foreign  Key
    pizza_id =   Column(Integer,ForeignKey("pizza.id"),index=True,nullable=False) #Foreign  Key
    pizza_name = Column(String,nullable=False)
    size_name =  Column(SQLEnum(PizzaSizeEnum),nullable=False)
    quantity =   Column(Integer,nullable=False,default=1)
    unit_price = Column(Numeric(10,2),nullable=False)
    sub_total =  Column(Numeric(10,2),nullable=False)

    #Relationship
    order =  relationship("Order_Model",   back_populates="order_item")
    pizza =  relationship("Pizza_Model",   back_populates="order")
    topping = relationship("Order_Topping_Model", back_populates="order_item",  cascade="all, delete-orphan", lazy="select")



#============================Order Item Topping Table===============================
class Order_Topping_Model(Base):
    __tablename__="order_item_toppings"
    id =            Column(Integer,primary_key=True,index=True)
    notes =         Column(String(500),nullable=False)
    order_item_id = Column(Integer,ForeignKey("order_items.id",ondelete="CASCADE"),index=True,nullable=False)
    topping_name =  Column(SQLEnum(PizzaToppingEnum),nullable=False)
    extra_price=    Column(Numeric(10,2),nullable=False)

    #Relationship
    order_item=relationship("Order_Item_Model",back_populates="topping")

    def __repr__(self):
        return f"<Order_Topping order_item_id={self.order_item_id} topping={self.topping_name}>"