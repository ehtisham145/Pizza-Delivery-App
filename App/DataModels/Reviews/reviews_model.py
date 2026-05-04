from App.Database.database import Base
from sqlalchemy import Column,Integer,String,ForeignKey,DateTime,Float,String
from sqlalchemy import DateTime
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

#1.=============================Review Model========================
class Review_Model(Base):
    __tablename__="reviews"
    id=Column(Integer,primary_key=True,index=True)
    order_id=Column(String,ForeignKey("orders.id"),unique=True,default=lambda:str(uuid.uuid4()))
    user_id=Column(Integer,ForeignKey("users.id"))
    pizza_id=Column(Integer,ForeignKey("pizza.id"))
    rating=Column(Float,nullable=False,index=True)
    comment=Column(String,nullable=True)
    created_at=Column(DateTime,default=datetime.utcnow)

    #Relationship
    user_relationship=relationship("User",back_populates="review_relationship")
    order_relationship=relationship("Order_Model",back_populates="review_relationship")
    pizza_relationship=relationship("Pizza_Model",back_populates="review_relationship")