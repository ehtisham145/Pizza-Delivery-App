from App.Database.database import Base
from sqlalchemy import Column, Integer, Text, String, Boolean, DateTime
from datetime import datetime,timezone
from sqlalchemy.orm import relationship

class User(Base):
    """
    Represents the 'users' table in the database for authentication and profile management.
    """
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(25), nullable=False)
    email = Column(String(80), unique=True, index=True,nullable=False)    
    password = Column(String(255), nullable=False)
    phone_number = Column(String(11), nullable=False)    
    role = Column(String(20), nullable=False, default="user")
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))    
    updated_at   = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                          onupdate=lambda: datetime.now(timezone.utc))
    
    #Relationship
    cart = relationship("Cart_Model",       back_populates="owner",            uselist=False, cascade="all, delete-orphan")
    order=relationship("Order_Model",       back_populates="user",             cascade="all, delete-orphan", lazy="select")
    address=relationship("Delivery_Model",  back_populates="user",             cascade="all, delete-orphan", lazy="select")
    payment=relationship("Payment_Model",   back_populates="user" ,            lazy="select")
    review=relationship("Review_Model",     back_populates="user",             lazy="select")
    notification=relationship("Notification_Model",back_populates="user",      cascade="all, delete-orphan", lazy="select")
    # ------------------ Object Representation ------------------------
    # The __repr__ method returns a string representation of the object.
    # It is used for debugging; instead of a memory address, 
    # it prints a readable string like <User ehtisham>.
    def __repr__(self):
        return f"<User {self.full_name}>"