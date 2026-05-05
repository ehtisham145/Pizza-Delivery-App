from sqlalchemy import Column,Integer,String,Boolean,DateTime,ForeignKey,Text
from App.Database.database import Base
from sqlalchemy.orm import relationship
from datetime import datetime,timezone
#1.----------------------------------Notification Model-------------------------------
class Notification_Model(Base):
    __tablename__="notifications"
    id=Column(Integer,primary_key=True,index=True)
    user_id=Column(Integer,ForeignKey("users.id",ondelete="CASCADE"),index=True,nullable=False)
    title=Column(String(255),nullable=False)
    message=Column(Text,nullable=False)
    is_read=Column(Boolean, default=False,index=True)
    created_at=Column(DateTime,default=lambda: datetime.now(timezone.utc))

    #Relationship
    user_relationship=relationship("User",back_populates="notification_relationship")
