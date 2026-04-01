from App.Database.database import Base
from sqlalchemy import Column, Integer, Text, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

class Order(Base):
    ORDER_STATUSES = (
        ("PENDING", "pending"),
        ("IN-TRANSIT", "in-transit"),
        ("DELIVERED", "delivered")
    )

    PIZZA_SIZES = (
        ("SMALL", "small"),
        ("MEDIUM", "medium"),
        ("LARGE", "large"),
        ("EXTRA-LARGE", "extra-large")
    )
    
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True)
    quantity = Column(Integer, nullable=False)
    # Simple String use karein
    order_status = Column(String, default="PENDING")
    pizza_sizes = Column(String, default="SMALL")
    
    # 3. ForeignKey mein bhi 'users.id' kar diya
    # user_id = Column(Integer, ForeignKey('users.id'),nullable=False)
    # user = relationship("User", back_populates='orders')

    def __repr__(self):
        return f"<Order {self.id}>"