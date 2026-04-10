from sqlalchemy import Integer,Column,Table,String,DateTime,ForeignKey,Float,Boolean,Enum
from App.Database.database import Base
from typing import Optional
from datetime import datetime
import enum
#=========================Category Table===========================

class Category_Model(Base):
    
    __tablename__="Categories"
    
    id=Column(Integer,primary_key=True,index=True)
    
    name=Column(String(100),index=True,nullable=False)
    
    description=Column(String(500),nullable=True)
    
    created_at:Optional=Column(DateTime,default=datetime.utcnow)

    
    def __repr__(self): # Check whether data table is working correctly in Database
        return f"<Category (name={self.name}, size={self.description})>"

#========================== Pizza Table ===========================


class Pizza_Model(Base):

    __tablename__ = "pizzas" # Table names are usually plural by convention

    id = Column(Integer, primary_key=True) # Primary keys are indexed by default
    
    # Keep index here: You will search/filter by name often
    name = Column(String(100), index=True, nullable=False) 
    
    # Remove index: Too long for a standard B-Tree index
    description = Column(String(500), nullable=False)
    
    # Index here if you plan to let users "Sort by Price"
    base_price = Column(Float, index=True, nullable=False)
    
    # Remove index: Never used in a WHERE clause
    image_url = Column(String(255), nullable=False)
    
    # Useful for filtering "Out of Stock" items
    is_available = Column(Boolean, default=True, index=True)
    
    # Fixed Foreign Key (Assumes your category table is named 'categories')
    category_id = Column(Integer, ForeignKey("Categories.id"), nullable=False)
    
    # Use datetime.utcnow (no brackets) so it generates a new time for every entry
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # onupdate ensures the timestamp refreshes whenever the row is edited
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self): # Check whether data table is working correctly in Database
        return f"<Pizza(name={self.name}, size={self.description})>"

#==========================Size Table===========================
class PizzaSize(enum.Enum):
    SMALL="small"
    MEDIUM="medium"
    LARGE="large"
    X_Large="X-Large"


class Size_Model(Base):
    __tablename__="size"
    id=Column(Integer,primary_key=True,index=True)
    size=Column(Enum(PizzaSize),nullable=False,default=PizzaSize.MEDIUM)
    price_multiplier = Column(Float, nullable=False, default=1.0)

    
    def __repr__(self): # Check whether data table is working correctly in Database
        return f"<Size(name={self.name}, size={self.size})>"

# 2. How to use it in your logic

# The goal of this table is to adjust the final price. In your backend logic, your calculation would look like this:

#     Total Price = Pizza.base_price×Size.price_multiplier

# Example Values:

#     Small: 0.8 (Discounted)

#     Medium: 1.0 (Base price)

#     Large: 1.5 (50% extra)

#     X-Large: 2.0 (Double price)

#==========================Topping Table===========================

class ToppingModel(Base):
    __tablename__="toppings"
    
    id=Column(Integer,primary_key=True,index=True)
    
    name=Column(String(100),index=True,nullable=False)
    
    extra_price=Column(Float,index=True,nullable=False)

    is_availble=Column(Boolean,default=True,index=True)

    def __repr__(self): # Check whether data table is working correctly in Database
        return f"<Topping (name={self.name}, size={self.extra_price})>"
