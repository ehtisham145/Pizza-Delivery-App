from sqlalchemy.orm import Session
from App.Database.database import Base
from sqlalchemy import Column,Integer,String,Float,Boolean,DateTime,ForeignKey,Numeric
from sqlalchemy.orm import relationship
import datetime
from App.DataModels.Menu.menu_model import Pizza_Model,Size_Model

#========================Cart Table========================
class Cart_Model(Base):
    __tablename__="cart"
    id=Column(Integer,primary_key=True,index=True)
    user_id=Column(Integer,ForeignKey("users.id"),unique=True,index=True,nullable=False)
    # created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    # updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)

    #Relationship
    items=relationship("Cart_Item",back_populates="cart",cascade="all, delete-orphan")
    owner=relationship("User",back_populates="cart")

    #Handling Prices and Other Features
    @property
    def total_price(self):
        return round(sum(item.sub_total for item in self.items),2) if self.items else 0.0

    @property
    def item_count(self):
        return len(self.items) if self.items else 0

#=========================Cart Items===========================
class Cart_Item(Base):
    __tablename__="cart_items"

    id=Column(Integer,primary_key=True,index=True)
    cart_id=Column(Integer,ForeignKey("cart.id"),index=True,nullable=False)
    pizza_id=Column(Integer,ForeignKey("pizza.id"),index=True,nullable=False)
    size_id=Column(Integer,ForeignKey("size.id"),index=True,nullable=False)
    size=Column(String,nullable=False)
    quantity=Column(Integer,default=1,nullable=False)
    unit_price=Column(Float,nullable=False)
    sub_total=Column(Integer,nullable=False)

    #Relationship
    cart = relationship("Cart_Model", back_populates="items")
    piza = relationship("Pizza_Model",back_populates="piz") 
    size_relationship = relationship("Size_Model",back_populates="siz") 
    toppings = relationship("Cart_Item_Topping", back_populates="cart_item")


#========================Cart Item Topping Table==================
class Cart_Item_Topping(Base):
    __tablename__ = "cart_toppings"
    cart_item_id = Column(Integer, ForeignKey("cart_items.id"), primary_key=True, nullable=False)
    topping_id = Column(Integer, ForeignKey("toppings.id"), primary_key=True, nullable=False)

    #Relationship
    cart_item = relationship("Cart_Item", back_populates="toppings")
