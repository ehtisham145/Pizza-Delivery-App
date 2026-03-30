from sqlalchemy import create_engine
#ORMs are used to convert your python code into sql queries so that operations in database can be performed without writing sql queries
from sqlalchemy.orm import declarative_base,sessionmaker,Session
#When you want to convert your python class with the data base tables you use declarative_base class

#-----------------Base-------------------

Base=declarative_base()

#When you want to convert your python class code in to database table then you use declarative base table
# for creating a connection between python app and database we use create engine module of sql
# Agar password khali (empty) hai

#-----------------DB URL------------------------------
DB_URL = "sqlite:///./pizza_delivery.db"

#------------------Create Connection------------------
engine=create_engine(DB_URL,connect_args={"check_same_thread": False})

#When you want to perform create read update and delete operations on your data base then you use Sessionmaker but these operations will finalized only once 
#you run command session.commit()

#------------------Create Session---------------------
#session maker is used to create a session and define the properties of databse in session maker
SessionLocal=sessionmaker(bind=engine)

# 2. Session (The Object / Asli Kaam)
# Jab aap SessionLocal() (jo sessionmaker se bana hota hai) ko call karte hain, toh ek Session Object banta hai. 
# Ye wo asli cheez hai jo database se "Haath milati" hai.

#------------------Dependency------------------------
def get_db(): #This function creates a session for you then you use this session to perform operations on database and then you close this session
    db: Session = SessionLocal()
    try:
        yield db  # route me ye session milega
    finally:
        db.close()


