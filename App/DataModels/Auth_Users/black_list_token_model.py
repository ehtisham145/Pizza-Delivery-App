from sqlalchemy import Column,Integer,String,DateTime
from datetime import datetime
from App.Database.database import Base

class BlackListTokens(Base):
    __tablename__="blacklist_tokens"
    id=Column(Integer,primary_key=True,index=True)
    token = Column(String, unique=True, nullable=False, index=True)
    blacklisted_on = Column(DateTime, default=datetime.utcnow)