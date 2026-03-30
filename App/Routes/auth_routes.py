from fastapi import HTTPException,Depends,APIRouter,status
from sqlalchemy.orm import Session
from App.Database.database import get_db
from App.Schemas.signup import SignUpModel
from App.Database.data_models.user_model import User
from App.Security.authentication import get_password_hash,verify_password
from App.Security.jwt import create_access_token
from fastapi.security import OAuth2PasswordRequestForm
from dotenv import load_dotenv
from datetime import timedelta
import os

load_dotenv()

admin_name=os.getenv("admin_name")
admin_password=os.getenv("admin_password")

#----------------------Sign Up---------------------------
auth_router=APIRouter()
@auth_router.post('/signup')
def signup(user: SignUpModel, db: Session = Depends(get_db)):
    # Check karein user pehle se toh nahi hai
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already exists")
    h_password=get_password_hash(user.password)
    new_user = User(
        username=user.username,
        email=user.email,
        password=h_password,
        is_staff=False,
        is_active=False
    )
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return {"message": "User created successfully", "user_id": new_user.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database Error during signup")

#----------------------Login-------------------------------

@auth_router.post("/login")
def login(
    db: Session = Depends(get_db), 
    form_data: OAuth2PasswordRequestForm = Depends()
):
    #Find user in database
    db_user = db.query(User).filter(User.username == form_data.username).first()

    # 2. Hardcoded Admin check 
    is_hardcoded_admin = (form_data.username == admin_name.lower() and form_data.password == admin_password)

    # 3. Validation Logic
    if is_hardcoded_admin:
        token_data = {"sub": admin_name, "is_staff": True}

    elif db_user and verify_password(form_data.password, db_user.password):
        token_data = {"sub": db_user.username, "is_staff": db_user.is_staff}
    
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 4. Token Creation (Ab admin aur user dono ko token milega)
    access_token = create_access_token(data=token_data)
    
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "user_role": "admin" if token_data["is_staff"] else "customer"
    }