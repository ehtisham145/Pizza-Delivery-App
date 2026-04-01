from typing import Optional
from datetime import datetime,timedelta,timezone
import jwt

SECRET_KEY = "your-very-secret-key-for-access"
REFRESH_SECRET_KEY = "your-different-secret-key-for-refresh"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

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