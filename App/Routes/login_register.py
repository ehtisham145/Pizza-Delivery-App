from fastapi import HTTPException,Depends,APIRouter,status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.exc import SQLAlchemyError,IntegrityError
from sqlalchemy.orm import Session
from App.Database.database import get_db
from App.DataModels.user_model import User
from App.Schemas.user_schemas.register_schema import UserRegisterSchema,UserResponseSchema
from App.Schemas.user_schemas.login_schema import UserLoginSchema,UserLoginResponseSchema
from App.Security.authentication import get_password_hash,verify_password
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from App.Utils.tokens import create_access_token,create_refresh_token
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime,timedelta
import os
load_dotenv()
import logging
# Set up basic logging to track internal errors
logger = logging.getLogger(__name__)

ALGORITHM=os.getenv("ALGORITHM")
SECRET_KEY=os.getenv("SECRET_KEY")
print(ALGORITHM)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Reusable constant for unauthorized errors
credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

#----------------------Register---------------------------
auth_router=APIRouter()

@auth_router.post(
    '/Register', 
    status_code=status.HTTP_201_CREATED,
    response_model=UserResponseSchema,
    summary="Register a new user"
)
def register_user(user:UserRegisterSchema,db: Session = Depends(get_db)):
    """
    Handles new user registration: checks for existing email, 
    hashes password, and persists user to the database.
    """
    
    # 1. Check if a user with the provided email already exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email address is already registered."
        )

    # 2. Securely hash the plain text password
    hashed_password = get_password_hash(user.password)

    # 3. Initialize the SQLAlchemy User model with provided data
    new_user = User(
        full_name=user.full_name,
        email=user.email,
        password=hashed_password,
        phone_number=user.phone_number,
        # Default fields (is_active, role, etc.) are handled by the DB model defaults
    )

    # 4. Transaction management with robust error handling
    try:
        db.add(new_user)
        db.commit()           # Save changes to the database
        db.refresh(new_user)  # Refresh to retrieve database-generated fields like ID
        return new_user
    except IntegrityError as e:
        # Catch database-level unique constraint violations
        db.rollback()
        logger.error(f"Integrity Error during registration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Registration failed: Possible duplicate data detected."
        )

    except SQLAlchemyError as e:
        # Catch general database-related issues
        db.rollback()
        logger.error(f"Database error during registration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal database error occurred. Please try again later."
        )

    except Exception as e:
        # Generic catch-all for unexpected code failures
        db.rollback()
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected server error occurred."
        )
    return {
        "id": user.id,
        "email":"user.email",
        "full_name": user.full_name, 
        "phone_number":user.phone_number, 
        "role": user.role,
        "is_active":user.is_active,
    }

#----------------------Login-------------------------------

@auth_router.post(
    "/Login",
    status_code=status.HTTP_201_CREATED
    ,response_model=UserLoginResponseSchema,
    summary="Login in to your Account"
)
def login(data:OAuth2PasswordRequestForm=Depends(),db: Session = Depends(get_db)):
    #Find user in database
    db_user = db.query(User).filter(User.email == data.username).first()

    if db_user and verify_password(data.password, db_user.password):

        token_data = {"sub": db_user.email, "Role": db_user.role}
    
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 4. Token Creation 
    access_token = create_access_token(data=token_data)
    refresh_token_jwt=create_refresh_token(data=token_data)

    return {
    "access_token": access_token,
    "token_type": "bearer",
    "email": db_user.email,
    "full_name": db_user.full_name,
    "refresh_token": {
        "token": refresh_token_jwt,
        "user_id": db_user.id,
        "created_at": datetime.now(),
        "expires_at": datetime.now() + timedelta(days=7), 
        "is_revoked": False
    }
}