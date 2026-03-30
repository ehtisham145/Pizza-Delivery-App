from App.Database.database import engine,Base
from App.Database.database import engine, Base
from App.Database.data_models.user_model import User 
from App.Database.data_models.order_model import Order
def create_tables():
    print("Tables create ho rahe hain...")
    Base.metadata.create_all(bind=engine)
