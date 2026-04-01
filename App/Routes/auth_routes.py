from fastapi import HTTPException,Depends,APIRouter,status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from App.Database.database import get_db
from App.Schemas.user_schemas.register_schema import UserRegisterSchema,UserResponseSchema
from App.Schemas.user_schemas.login_schema import UserLoginSchema,UserLoginResponseSchema
from App.DataModels.user_model import User
from App.Security.authentication import get_password_hash,verify_password
from App.Security.jwt import create_access_token
from fastapi.security import OAuth2PasswordRequestForm
from dotenv import load_dotenv
from datetime import timedelta
import os
#----------------------Register---------------------------
auth_router=APIRouter()

@auth_router.post(
    '/Register', 
    status_code=status.HTTP_201_CREATED,response_class=UserResponseSchema,
    summary="Register a new user"
)

def register_user(user: UserRegisterSchema, db: Session = Depends(get_db)):
    """
    Registers a new user and filters the output through UserResponseSchema.
    """
    # 1. Check if user exists
    email_exists = db.query(User.id).filter(User.email == user.email).first()
    if email_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="A user with this email already exists."
        )

    # 2. Securely hash the password
    hashed_pwd = get_password_hash(user.password)

    # 3. Create Model Instance
    new_user = User(
        full_name=user.full_name,
        email=user.email,
        phone_number=user.phone_number, 
        role=user.role,
        password=hashed_pwd,
        is_active=False
    )
    # This only works if every field name in Schema matches the Model exactly
    # user=User(**user.model_dump())
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # 4. IMPORTANT: Return the model object directly.
        # FastAPI will automatically convert 'new_user' into 'UserResponseSchema'
        return new_user

    except SQLAlchemyError as e:
        db.rollback()
        print(f"Database Error: {e}") 
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal database error occurred."
        )

# #----------------------Login-------------------------------

@auth_router.post(
    "/Login",
    status_code=status.HTTP_201_CREATED
    ,response_class=UserLoginResponseSchema,
    summary="Login in to your Account"
)
def login(
    db: Session = Depends(get_db), 
    form_data: OAuth2PasswordRequestForm = Depends()
):
    #Find user in database
    db_user = db.query(User).filter(User.email == form_data.email).first()

    if db_user and verify_password(form_data.password, db_user.password):
        token_data = {"sub": db_user.email, "Role": db_user.role}
    
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 4. Token Creation 
    access_token = create_access_token(data=token_data)
    
    return {
        "access_token": access_token, 
        "token_type": "bearer",
    }