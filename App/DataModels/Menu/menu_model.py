from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Numeric
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import relationship
from App.Database.database import Base
from App.Utils.constant import PizzaCategoryEnum, PizzaSizeEnum

#1.=========================Category Table===========================
class Category_Model(Base):
    __tablename__="categories"
    id=Column(Integer,primary_key=True,index=True)
    name = Column(
        SQLEnum(PizzaCategoryEnum, values_callable=lambda obj: [item.value for item in obj]),
        index=True, 
        unique=True, 
        nullable=False
    )
    description=Column(String(500),nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    def __repr__(self): # Check whether data table is working correctly in Database
        return f"<Category (name={self.name}>"

#2.========================== Pizza Table ===========================
class Pizza_Model(Base):
    __tablename__ = "pizza" 
    id = Column(Integer, primary_key=True)    
    name = Column(String(100), index=True,unique=True, nullable=False) 
    description = Column(String(500), nullable=False)
    base_price = Column(Numeric(10,2), nullable=False)
    image_url = Column(String(255), nullable=False)
    is_available = Column(Boolean, default=True, index=True)    
    category_id = Column(Integer,ForeignKey("categories.id"),index=True,nullable=False)    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))    
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
    onupdate=lambda: datetime.now(timezone.utc))

    #Relationship
    cart_items = relationship("Cart_Item",      back_populates="pizza")
    order =     relationship("Order_Item_Model",back_populates="pizza")
    review =    relationship("Review_Model",    back_populates="pizza")
    
    def __repr__(self): # Check whether data table is working correctly in Database
        return f"<Pizza(name={self.name}, size={self.base_price})>"

#2.==========================Size Table===========================
class Size_Model(Base):
    __tablename__="size"
    id=Column(Integer,primary_key=True,index=True)
    size=Column(SQLEnum(PizzaSizeEnum, values_callable=lambda obj: [item.value for item in obj]),
        index=True, 
        unique=True, 
        nullable=False)
    price_multiplier = Column(Numeric(10,2), nullable=False, default=1.0)
    #Relationship
    cart_items=relationship("Cart_Item",back_populates="size_cart")
    def __repr__(self):
        return f"<Size(size={self.size}, multiplier={self.price_multiplier})>"

#3.==========================Topping Table===========================
class Topping_Model(Base):
    __tablename__="toppings" 
    id = Column(Integer,primary_key=True,index=True)
    name =   Column(String(100),index=True,nullable=False)
    extra_price =    Column(Numeric(10,2),index=True,nullable=False)
    is_available =   Column(Boolean,default=True,index=True)
    created_at   = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at   = Column(DateTime, default=lambda: datetime.now(timezone.utc),
    onupdate=lambda: datetime.now(timezone.utc))
    #relationship
    cart_item_toppings = relationship("Cart_Item_Topping", back_populates="topping")
    
    def __repr__(self): # Check whether data table is working correctly in Database
        return f"<Topping (name={self.name}, size={self.extra_price})>"
