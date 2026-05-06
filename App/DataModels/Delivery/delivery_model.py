from sqlalchemy import Column,Integer,String,Boolean,ForeignKey,Enum as SQLEnum,Float,DateTime
from App.Utils.constant import AddressStatusEnum
from datetime import datetime,timezone

#=================================Delivery Address=============================
class Delivery_Model(Base):
    __tablename__="delivery_addresses"
    id  = Column(Integer,primary_key=True,index=True)
    user_id =   Column(Integer,ForeignKey("users.id"),nullable=False,index=True)
    label   =  Column(SQLEnum(AddressStatusEnum),nullable=False)
    street  =   Column(String(150),nullable=False)
    city    =   Column(String(100),nullable=False)
    zip_code =   Column(String(10),nullable=False)
    is_default = Column(Boolean,default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    #relationship
    user=relationship("User",back_populates="address")
    orders = relationship("Order_Model", back_populates="address", cascade="all, delete-orphan", lazy="select")

    def __repr__(self):
         return f"<Delivery_Model user_id={self.user_id} city={self.city} label={self.label}>"