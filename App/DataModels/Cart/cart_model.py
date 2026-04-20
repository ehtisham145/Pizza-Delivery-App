from sqlalchemy.orm import Session
from App.Database.database import Base
from sqlalchemy import Column,Integer,String,Float,Boolean,DateTime,ForeignKey,Numeric
from sqlalchemy.orm import relationship
from App.DataModels.Auth_Users.user_model import User 
import datetime

#========================Cart Table========================
class Cart_Model(Base):
    __tablename__="cart"
    id=Column(Integer,primary_key=True,index=True)
    user_id=Column(Integer,ForeignKey("users.id"),unique=True,index=True,nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)
    #Relationship
    items=relationship("Cart_Item",back_populates="cart",cascade="all, delete-orphan")
    owner=relationship("User",back_populates="cart")


#=========================Cart Items===========================
class Cart_Item(Base):
    __tablename__="cart_items"

    id=Column(Integer,primary_key=True,index=True)
    cart_id=Column(Integer,ForeignKey("cart.id"),index=True,nullable=False)
    pizza_id=Column(Integer,ForeignKey("pizza.id"),index=True,nullable=False)
    size_id=Column(Integer,ForeignKey("size.id"),index=True,nullable=False)
    quantity=Column(Integer,default=1,nullable=False)
    unit_price=Column(Float,nullable=False)
    sub_total=Column(Float,nullable=False)

    #Relationship
    cart = relationship("Cart_Model", back_populates="items")
    pizza = relationship("Pizza") # Pizza table se name lene ke liye
    size_relationship = relationship("Size") # Size table se name lene ke liye
    toppings = relationship("Cart_Item_Topping", back_populates="cart_item")

ss
#========================Cart Item Topping Table==================
class Cart_Item_Topping(Base):
    __tablename__ = "cart_toppings"
    # Dono par primary_key=True lazmi hai
    cart_item_id = Column(Integer, ForeignKey("cart_items.id"), primary_key=True, nullable=False)
    topping_id = Column(Integer, ForeignKey("toppings.id"), primary_key=True, nullable=False)

    cart_item = relationship("Cart_Item", back_populates="toppings")
