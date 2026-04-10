from App.Database.database import get_db 
from App.DataModels.Auth_Users.user_model import User 
from sqlalchemy.orm import Session

def make_user_admin(user_email: str):
    # 1. get_db() ek generator hai, is se session nikalne ke liye next() use karein
    db_gen = get_db()
    db = next(db_gen) 
    
    try:
        # 2. Ab 'db' aik asli Session hai, .query() kaam karega
        user = db.query(User).filter(User.email == user_email).first()
        
        if user:
            user.role = "admin"
            db.commit()
            print(f"✅ Success: {user_email} is now an Admin!")
        else:
            print(f"❌ Error: User with email {user_email} not found.")
            
    except Exception as e:
        db.rollback()
        print(f"🔥 Database Error: {e}")
    finally:
        db.close()

make_user_admin("")