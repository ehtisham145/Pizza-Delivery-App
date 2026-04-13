from App.Database.database import get_db 
from App.DataModels.Auth_Users.user_model import User 
from sqlalchemy.orm import Session

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

# --- Execution ---
# Admin banane ke liye
update_user_role("ehtisham2406@gmail.com", "admin")

# Staff banane ke liye
update_user_role("some_staff@gmail.com", "staff")