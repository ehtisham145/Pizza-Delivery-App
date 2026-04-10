from passlib.context import CryptContext
import jwt
from jose import jwt, JWTError, ExpiredSignatureError
import os
from typing import Optional
from datetime import datetime,timedelta,timezone
from fastapi import HTTPException,status,Depends
from sqlalchemy.orm import Session
from App.Database.database import get_db
from App.DataModels.Auth_Users.user_model import User
from App.DataModels.Auth_Users.black_list_token_model import BlackListTokens
from fastapi.security import OAuth2PasswordBearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/Login")
from dotenv import load_dotenv 
load_dotenv()
#The main purpose of this script is to check whether user has the token or not

SECRET_KEY = os.getenv("SECRET_KEY")
REFRESH_SECRET_KEY =os.getenv("REFRESH_SECRET_KEY")
ALGORITHM =os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES =int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
REFRESH_TOKEN_EXPIRE_DAYS =int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS"))

print(SECRET_KEY)
print(REFRESH_SECRET_KEY)
print(ALGORITHM)
print(ACCESS_TOKEN_EXPIRE_MINUTES)
print(REFRESH_TOKEN_EXPIRE_DAYS)
# 1. Setup the hashing engine
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

#----------------Hash User Password-----------------------
def get_password_hash(password):
#This function will hash user password
    return pwd_context.hash(password)
hash_password=get_password_hash(password="Ehtisham7863")
print(hash_password)


#--------------Function to verify password---------------------
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


#------------ Create Access Token (Used during Login)-------------------

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Generates a short-lived JWT Access Token.
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Add expiration time to the payload
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt




#------------- Create Refresh Token (Used for Long Term)-----------------------

def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Generates a long-lived JWT Refresh Token.
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({"exp": expire})
    
    # Use a different secret key for Refresh Tokens
    encoded_jwt = jwt.encode(to_encode, REFRESH_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt



#-------------------Verify User Refresh Token----------------
def verify_refresh_token(token: str):
    try:
        # 1. Print current key being used (first 5 chars only for security)
        print(f"DEBUG: Using SECRET_KEY starting with: {SECRET_KEY[:5]}")
        
        payload = jwt.decode(token, REFRESH_SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        print("DEBUG: Token has expired")
        return None
    except jwt.JWTError as e:
        print(f"DEBUG: JWT Error: {e}") # Yahan 'Signature verification failed' likha ayega
        return None


#-----------Function for checking user token----------------------
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    clean_token = token.replace("Bearer ", "").strip()
    #Checking whether the user token is in black list table of your database or not
    is_black_list_token=db.query(BlackListTokens).filter(BlackListTokens.token==clean_token).first()
    if is_black_list_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Token has been Logout Please Log in Again !")
    else:
        try:
            # Decode the JWT token using the secret key and specified algorithm
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            
            # Extract the 'sub' (subject) claim which represents the email
            email: str = payload.get("sub")
            
            if email is None:
                # Raise exception if the identity claim is missing from the payload
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, 
                    detail="Token is missing user identity information"
                )
                
        except ExpiredSignatureError:
            # Specifically handle cases where the token's validity period has passed
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Token has expired. Please authenticate again."
            )
            
        except JWTError:
            # Handle cases where the token is malformed or the signature is invalid
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Could not validate credentials due to invalid token signature"
            )

        # Validate that the user identified in the token still exists in the database
        user = db.query(User).filter(User.email == email).first()
        
        if user is None:
            # Security measure: reject access if the user was deleted but holds a valid token
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="User identity found in token does not exist in the system"
            )
            
        # Return the authenticated user object to be used by the endpoint
        return user
    

