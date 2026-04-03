from typing import Optional
from datetime import datetime,timedelta,timezone
import jwt
from dotenv import load_dotenv
#load the variable in dot env
load_dotenv()
import os
SECRET_KEY = os.getenv("SECRET_KEY")
REFRESH_SECRET_KEY =  os.getenv("REFRESH_SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES =int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS"))

# print(REFRESH_SECRET_KEY,ALGORITHM,ACCESS_TOKEN_EXPIRE_MINUTES,REFRESH_TOKEN_EXPIRE_DAYS) # for testing

# -------------------------------------------------------------------------
# FUNCTION 1: Create Access Token (Used during Login)
# -------------------------------------------------------------------------
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

# -------------------------------------------------------------------------
# FUNCTION 1: Create Refresh Token (Used for Long Term)
# -------------------------------------------------------------------------
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