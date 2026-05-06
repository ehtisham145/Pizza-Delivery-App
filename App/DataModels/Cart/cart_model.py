from sqlalchemy.orm import Session
from App.Database.database import Base
from sqlalchemy import Column,Integer,String,Float,Boolean,DateTime,ForeignKey,Numeric
from sqlalchemy.orm import relationship
from datetime import datetime,timezone

#========================Cart Table========================
class Cart_Model(Base):
    __tablename__="cart"
    id  = Column(Integer,primary_key=True,index=True)
    user_id =    Column(Integer,ForeignKey("users.id"),unique=True,index=True,nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                    onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    #Relationship
    items =  relationship("Cart_Item",back_populates="cart",cascade="all, delete-orphan",lazy="select")
    owner = relationship("User",back_populates="cart")

    #Handling Prices and Other Features
    @property
    def total_price(self):
        return round(sum(item.sub_total for item in self.items),2) if self.items else 0.0

    @property
    def item_count(self):
        return len(self.items) if self.items else 0

    def __repr__(self):
        return f"<Cart user_id={self.user_id} items={self.item_count}>"

#=========================Cart Items===========================
class Cart_Item(Base):
    __tablename__="cart_items"

    id = Column(Integer,primary_key=True,index=True)
    cart_id =    Column(Integer,ForeignKey("cart.id"),index=True,nullable=False)
    pizza_id =   Column(Integer,ForeignKey("pizza.id"),index=True,nullable=False)
    size_id =    Column(Integer,ForeignKey("size.id"),index=True,nullable=False)
    size =   Column(String,nullable=False)
    quantity =   Column(Integer,default=1,nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    sub_total  = Column(Numeric(10, 2), nullable=False)

    #Relationship
    cart = relationship("Cart_Model",   back_populates="items")
    pizza = relationship("Pizza_Model", back_populates="cart_items") 
    size= relationship("Size_Model",    back_populates="cart_items") 
    topping = relationship("Cart_Item_Topping", back_populates="cart_item" , cascade="all, delete-orphan")


#========================Cart Item Topping Table==================
class Cart_Item_Topping(Base):
    __tablename__ = "cart_toppings"
    cart_item_id = Column(Integer, ForeignKey("cart_items.id"), primary_key=True, nullable=False)
    topping_id = Column(Integer, ForeignKey("toppings.id"), primary_key=True, nullable=False)

    #Relationship
    cart_item = relationship("Cart_Item", back_populates="toppings")
