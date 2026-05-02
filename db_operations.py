from App.Database.database import get_db 
from App.DataModels.Auth_Users.user_model import User 
from sqlalchemy.orm import Session
from App.DataModels.Menu.menu_model import Category_Model,Size_Model
from sqlalchemy import text,inspect
from App.Utils.constant import PizzaSizeEnum
from App.DataModels.Order.order_model import Order_Model
#============================User Role Upgradation===============================
def update_user_role(user_email: str, new_role: str):
    """
    Generic function to update user roles safely.
    """
    # 1. Initialize Database Session
    db_gen = get_db()
    db = next(db_gen)

    try:
        # 2. Search User
        user = db.query(User).filter(User.email == user_email).first()

        # 3. Validation & Update
        if not user:
            print(f"❌ Error: User with email {user_email} not found.")
            return

        if user.role == new_role:
            print(f"ℹ️ Info: User {user_email} is already {new_role}.")
            return

        # 4. Apply Changes
        user.role = new_role
        db.commit()
        print(f"✅ Success: {user_email} is now {new_role}!")

    except Exception as e:
        db.rollback()
        print(f"🔥 Database Error: {e}")
    finally:
        db.close()


#=============================Rename Table in SQL Alchmey=============================
def rename_sqlite_table_casing(old_name, new_name):
    db_gen = get_db()
    db = next(db_gen)
    
    # We use a middle-man name to trick SQLite
    temp_name = f"{old_name}_temp"
    
    try:
        # 1. Rename to a temporary name
        db.execute(text(f"ALTER TABLE {old_name} RENAME TO {temp_name}"))
        print(f"Step 1: Moved to {temp_name}")
        
        # 2. Rename from temporary to the final lowercase name
        db.execute(text(f"ALTER TABLE {temp_name} RENAME TO {new_name}"))
        print(f"Step 2: Moved to {new_name}")
        
        db.commit()
        print("✅ Success! Table casing updated.")
    except Exception as e:
        db.rollback()
        print(f"❌ Failed: {e}")

#===========================Delete a Table from Data Base=========================
def delete_table(table_name:str):
    db_gen=get_db()
    db=next(db_gen)

    query=text(f"DROP TABLE IF EXISTS {table_name}")

    try:
        db.execute(query)
        db.commit()

    except Exception as e:
        db.rollback()
        print(f"Error : {e}")

#==========================Adding Sizes=======================================
def seed_sizes():
    db_gen = get_db()
    db = next(db_gen)
    
    # FIX 1: Added () to .count()
    if db.query(Size_Model).count() == 0:
        sizes = [
            Size_Model(size=PizzaSizeEnum.SMALL, price_multiplier=0.8),
            Size_Model(size=PizzaSizeEnum.MEDIUM, price_multiplier=1.0),
            Size_Model(size=PizzaSizeEnum.LARGE, price_multiplier=1.5),
            Size_Model(size=PizzaSizeEnum.XLARGE, price_multiplier=2.0),
        ]
        db.add_all(sizes)
        db.commit()
        print("Sizes seeded successfully!")
    else:
        print("Sizes already exist in the database.")
    
    # FIX 2: Close the database session outside the if block
    db.close() 
    
    return {"message": "Data check complete, sizes seeded if table was empty."}


#==============================Delete All Records From Table=========================

def truncate_orders():
    db_gen = get_db()
    db = next(db_gen)
    
    try:
        db.execute(text("DELETE FROM cart")) 
        db.execute(text("DELETE FROM cart_items"))
        db.execute(text("DELETE FROM order_items")) 
        db.execute(text("DELETE FROM orders"))
        db.commit()
        return {"status": "success", "message": "SQLite tables cleared successfully!"}
        
    except Exception as e:
        db.rollback()
        print(f"Error occurred: {e}")
        return {"status": "error", "message": str(e)}
        
    finally:
        db.close()

#============================Drop Tables===============================
def drop_tables():
    db_gen=get_db()
    db=next(db_gen)

    try:
        db.execute(text("DROP TABLE IF EXISTS delivery_addresses"))
        db.execute(text("DROP TABLE IF EXISTS order_items"))
        db.execute(text("DROP TABLE IF EXISTS orders"))

        print("Tables Deleted Successfully")
    except Exception as e:
        print(f"Error : {e}")


#===============================Checking Tables in DataBase===========================

def check_tables():
    db_gen = get_db()
    db = next(db_gen)
    inspector = inspect(db.get_bind())
    tables = inspector.get_table_names()
    print("Current tables in database:", tables)

# update_user_role("ehtishamexp@gmail.com", "admin")




if __name__ == "__main__":
    drop_tables()
    
