from App.Database.database import Base
from sqlalchemy import Column, Integer, Text, String, Boolean, DateTime
from datetime import datetime

class User(Base):
    """
    Represents the 'users' table in the database for authentication and profile management.
    """
    __tablename__ = "users"

    # Primary key and indexing for faster lookups
    id = Column(Integer, primary_key=True, index=True)
    
    # Unique identification fields
    full_name = Column(String(25), nullable=False)
    email = Column(String(80), unique=True, nullable=False)
    
    # Secure fields and contact info
    password = Column(Text, nullable=False)
    phone_number = Column(String(11), nullable=False)
    
    # Authorization and Status
    role = Column(String(20), nullable=False, default="user")
    is_active = Column(Boolean, default=False)

    # Timestamps for auditing
    # created_at: Set only when the record is first created
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # updated_at: Automatically refreshes every time the row is modified
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # ------------------ Object Representation ------------------------
    # The __repr__ method returns a string representation of the object.
    # It is used for debugging; instead of a memory address, 
    # it prints a readable string like <User ehtisham>.
    def __repr__(self):
        return f"<User {self.full_name}>"