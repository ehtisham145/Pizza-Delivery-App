from sqlalchemy import Column,Integer,String,Boolean,DateTime,ForeignKey,Text
from App.Database.database import Base
from sqlalchemy.orm import relationship
from datetime import datetime,timezone
#1.----------------------------------Notification Model-------------------------------
class Notification_Model(Base):
    __tablename__="notifications"
    id =         Column(Integer,primary_key=True,index=True)
    user_id =    Column(Integer,ForeignKey("users.id",ondelete="CASCADE"),index=True,nullable=False)
    title =      Column(String(255),nullable=False)
    message =    Column(Text,nullable=False)
    is_read =    Column(Boolean, default=False,index=True)
    created_at = Column(DateTime,default=lambda: datetime.now(timezone.utc))
    
    # Composite index — optimizes "get unread notifications for user" queries
    __table_args__ = (
        Index("ix_notifications_user_unread", "user_id", "is_read"),
    )

    #Relationship
    user=relationship("User",back_populates="notification",passive_deletes=True)
    def __repr__(self):
        return f"<Notification user_id={self.user_id} title={self.title} read={self.is_read}>"
