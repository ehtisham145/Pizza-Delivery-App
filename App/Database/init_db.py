from App.Database.database import engine,Base
def create_tables():
    print("Tables are creating...")
    Base.metadata.create_all(bind=engine)

print(create_tables())
