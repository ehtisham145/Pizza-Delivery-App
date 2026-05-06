from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Numeric, CheckConstraint
from sqlalchemy.orm import relationship
from App.Database.database import Base


#1.=============================Review Model========================
class Review_Model(Base):
    __tablename__="reviews"
    id =        Column(Integer,primary_key=True,index=True)
    order_id =  Column(String(36),ForeignKey("orders.id",ondelete="SET NULL"),unique=True,default=lambda:str(uuid.uuid4()))
    user_id =   Column(Integer,ForeignKey("users.id",ondelete="CASCADE"),index=True,nullable=False)
    pizza_id =  Column(Integer,ForeignKey("pizza.id"),nullable=False,index=True)
    rating     = Column(Numeric(3, 1), nullable=False, index=True)
    comment    = Column(String(1000), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))
    __table_args__ = (
        CheckConstraint("rating >= 1 AND rating <= 5", name="valid_rating_range"),
    )

    #Relationship
    user=relationship("User",back_populates="review", passive_deletes=True)
    order=relationship("Order_Model",back_populates="review")
    pizza=relationship("Pizza_Model",back_populates="review", passive_deletes=True)

    def __repr__(self):
        return f"<Review user_id={self.user_id} pizza_id={self.pizza_id} rating={self.rating}>"