from App.Database.database import get_db 
from App.DataModels.Auth_Users.user_model import User 
from sqlalchemy.orm import Session
from App.DataModels.Menu.menu_model import Category_Model
from sqlalchemy import text
from sqlalchemy import inspect

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

delete_table("pizzas")
def check_tables():
    db_gen = get_db()
    db = next(db_gen)
    inspector = inspect(db.get_bind())
    tables = inspector.get_table_names()
    print("Current tables in database:", tables)

if __name__ == "__main__":
    check_tables()