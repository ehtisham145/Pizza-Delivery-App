from App.Database.database import Base
from sqlalchemy import Column,String,Boolean,Float,Integer,DateTime
from sqlalchemy.sql import func

#-----------Pizza Data Model------------------
class PizzaModel(Base):
    __tablename__ = "pizzas"
    
    id=Column(Integer,primary_key=True,index=True)

    name=Column(String(100),nullable=False,unique=True,index=True)
    
    price=Column(Float,nullable=False)
    
    description=Column(String(500),nullable=False) # Add some info about pizza
    
    size=Column(String(50),nullable=False)      
    
    category=Column(String(50),nullable=False)
    
    is_available=Column(Boolean,default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self): # Check whether data table is working correctly in Database
        return f"<Pizza(name={self.name}, size={self.size})>"