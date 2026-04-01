from jose import jwt, JWTError, ExpiredSignatureError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from App.Database.database import get_db
from sqlalchemy.orm import Session
from App.DataModels.user_model import User
from App.Utils.tokens import create_access_token,create_refresh_token
import os
from dotenv import load_dotenv
load_dotenv()

#-----------------------Imp Server Details---------------
ADMIN_NAME=os.getenv("admin_name")
ADMIN_PASSWORD=os.getenv("admin_password")
SECRET_KEY = os.getenv("SECRET_KEY")
REFRESH_SECRET_KEY =os.getenv("REFRESH_SECRET_KEY")
ALGORITHM =os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES =os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
REFRESH_TOKEN_EXPIRE_DAYS =os.getenv("REFRESH_TOKEN_EXPIRE_DAYS")

print(ADMIN_NAME,ADMIN_PASSWORD,SECRET_KEY,REFRESH_SECRET_KEY,ALGORITHM,ACCESS_TOKEN_EXPIRE_MINUTES,REFRESH_TOKEN_EXPIRE_DAYS            )
# Specifies that the token will be extracted from 'Authorization: Bearer <token>' header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

#-----------Function for checking user token----------------------
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        # Decode the JWT token using the secret key and specified algorithm
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Extract the 'sub' (subject) claim which represents the username
        username: str = payload.get("sub")
        
        if username is None:
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
    user = db.query(User).filter(User.username == username).first()
    
    if user is None:
        # Security measure: reject access if the user was deleted but holds a valid token
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="User identity found in token does not exist in the system"
        )
        
    # Return the authenticated user object to be used by the endpoint
    return user