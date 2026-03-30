from App.Database.database import Base
from sqlalchemy import Column, Integer, Text, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = "users"  # 1. 'user' se 'users' kar diya
    id = Column(Integer, primary_key=True)
    username = Column(String(25), unique=True)
    email = Column(String(80), unique=True)
    password = Column(Text, nullable=False)
    is_staff = Column(Boolean, default=False)
    is_active = Column(Boolean, default=False)
    
    # Relationship with Order
    orders = relationship("Order", back_populates="user") 

#------------------Object Rule------------------------
#When you create a class object in python then python checks whether you pass __repr__ or __str__ function
#otherwise just memory address of your object is printed so to avoid this we use
#print(object) → __str__() → __repr__() → default memory By writing this function debugging of code becomes easy
    def __repr__(self):
        # 2. 'self.user_name' ko 'self.username' kar diya
        return f"<User {self.username}>"