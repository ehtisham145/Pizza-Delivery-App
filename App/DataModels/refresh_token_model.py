from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from App.Database.database import Base

class RefreshToken(Base):
    __tablename__ = "refresh_tokens" # Good practice to name the table

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, index=True, nullable=False)
    
    # IMPORTANT: The link to your User table
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Use server_default for automatic timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)
    
    is_revoked = Column(Boolean, default=False)