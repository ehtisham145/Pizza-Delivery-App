from fastapi import HTTPException,Depends,APIRouter,status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.exc import SQLAlchemyError,IntegrityError
from sqlalchemy.orm import Session
from App.Utils.middleware import get_current_user,get_password_hash,verify_password,create_access_token,create_refresh_token 
from App.Database.database import get_db
from App.DataModels.Auth_Users.refresh_token_model import RefreshTokenModel
from App.DataModels.Auth_Users.user_model import User
from App.Schemas.Auth_Users.Token_Schema.refresh_token_schema import RefreshTokenRequest 
from App.Schemas.Auth_Users.User_Schema.register_schema import UserRegisterSchema,UserResponseSchema
from App.Schemas.Auth_Users.User_Schema.login_schema import UserLoginResponseSchema
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime,timedelta
from App.DataModels.Auth_Users.black_list_token_model import BlackListTokens
from App.Utils.middleware import verify_refresh_token
import os
from dotenv import load_dotenv
load_dotenv()
import logging

auth_router=APIRouter()
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
        role="customer"
        # Default fields (is_active, role, etc.) are handled by the DB model defaults
    )

    # 4. Transaction management with robust error handling
    db.add(new_user)
    db.commit()           # Save changes to the database
    db.refresh(new_user)  # Refresh to retrieve database-generated fields like ID

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
    # 5. CRITICAL STEP: Save Refresh Token to Database
    new_db_refresh_token = RefreshTokenModel(
        token=refresh_token_jwt,
        user_id=db_user.id,
        created_at=datetime.utcnow(), # Use UTC for consistency
        expires_at=datetime.utcnow() + timedelta(days=7),
        is_revoked=False
    )
    #6.Save your Refresh Token in Database
    db.add(new_db_refresh_token)
    db.commit()
    db.refresh(new_db_refresh_token)    
    return {
    "access_token": access_token,
    "token_type": "bearer",
    "email": db_user.email,
    "full_name": db_user.full_name,
    "refresh_token": {
        "refresh_token": refresh_token_jwt,
        "user_id": db_user.id,
        "created_at": datetime.now(),
        "expires_at": datetime.now() + timedelta(days=7), 
        "is_revoked": False
    }
}    


#-------------------Black List User Token------------------
@auth_router.post(
    "/Logout",
    status_code=status.HTTP_201_CREATED
    )
def Logout(token:str=Depends(oauth2_scheme),db:Session=Depends(get_db),current_user:User=Depends(get_current_user)):
    #1.Clean your Token 
    clean_token = token.replace("Bearer ", "").strip()
    #2.Check Token in database
    exists=db.query(BlackListTokens).filter(BlackListTokens.token ==clean_token).first()
    if exists:
        return {"message": "User is already logout dont need to check."}

    new_entry = BlackListTokens(token=clean_token)    
    db.add(new_entry)
    db.commit()
    
    return {"message": "Logout successful!"}


@auth_router.post("/Refresh-token", status_code=status.HTTP_201_CREATED)
def refresh_access_token(
    payload: RefreshTokenRequest, 
    db: Session = Depends(get_db)
):
    # 1. Verify token signature and expiration
    decoded_data = verify_refresh_token(payload.refresh_token)
    if not decoded_data:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    username = decoded_data.get("sub")

    # 2. Check if the token exists and belongs to the user
    # It's safer to join or check user_id here to ensure the account wasn't deleted
    db_token = db.query(RefreshTokenModel).filter(
        RefreshTokenModel.token == payload.refresh_token
    ).first()
    
    if not db_token:
        # Security Tip: This could mean the token was stolen and used already
        # (Automatic Reuse Detection)
        raise HTTPException(status_code=401, detail="Token revoked or already used")

    # 3. Token Rotation: Generate new pair
    new_access = create_access_token(data={"sub": username})
    new_refresh = create_refresh_token(data={"sub": username})

    try:
        # 4. Atomic Swap: Delete old, add new
        db.delete(db_token)
        # Calculate expiry time (matching your REFRESH_TOKEN_EXPIRE_DAYS)
        expiry_time = datetime.utcnow() + timedelta(days=7)
        new_db_token = RefreshTokenModel(
            token=new_refresh, 
            user_id=db_token.user_id, # Link to the same user
            expires_at=expiry_time,    # THIS WAS MISSING
            is_revoked=False
        )
        db.add(new_db_token)
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Could not update security tokens")

    return {
        "access_token": new_access,
        "refresh_token": new_refresh,
        "token_type": "bearer"
    }