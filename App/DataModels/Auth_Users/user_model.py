from App.Database.database import Base
from sqlalchemy import Column, Integer, Text, String, Boolean, DateTime
from datetime import datetime
from sqlalchemy.orm import relationship
from App.DataModels.Reviews.reviews_model import Review_Model

class User(Base):
    """
    Represents the 'users' table in the database for authentication and profile management.
    """
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(25), nullable=False)
    email = Column(String(80), unique=True, nullable=False)    
    password = Column(Text, nullable=False)
    phone_number = Column(String(11), nullable=False)    
    role = Column(String(20), nullable=False, default="user")
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)    
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    #Relationship
    cart = relationship("Cart_Model", back_populates="owner", uselist=False, cascade="all, delete-orphan")
    order_relationship=relationship("Order_Model",back_populates="user_relationship")
    address_relationship=relationship("Delivery_Model",back_populates="user_relationship")
    payment_relationship=relationship("Payment_Model",back_populates="user_relationship")
    review_relationship=relationship("Review_Model",back_populates="user_relationship")
    notification_relationship=relationship("Notification_Model",back_populates="user_relationship")
    # ------------------ Object Representation ------------------------
    # The __repr__ method returns a string representation of the object.
    # It is used for debugging; instead of a memory address, 
    # it prints a readable string like <User ehtisham>.
    def __repr__(self):
        return f"<User {self.full_name}>"