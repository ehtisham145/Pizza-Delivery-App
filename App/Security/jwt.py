from jose import jwt, JWTError, ExpiredSignatureError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from App.Database.database import get_db
from sqlalchemy.orm import Session
from App.DataModels.user_model import User
from datetime import datetime, timedelta, timezone
from typing import Optional
from App.Utils.tokens import create_access_token,create_refresh_token



# Specifies that the token will be extracted from 'Authorization: Bearer <token>' header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# -------------------------------------------------------------------------
# FUNCTION 2: Verify Token (Used in all Protected Routes)
# -------------------------------------------------------------------------
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        # Step A: Attempt to decode the token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Step B: Log the token payload for debugging purposes
        print(f"✅ DEBUG SUCCESS: Token Payload found -> {payload}")
        
        username: str = payload.get("sub")
        
        if username is None:
            print("❌ DEBUG ERROR: 'sub' key not found in token!")
            raise HTTPException(status_code=401, detail="Token missing user identity")
            
    except ExpiredSignatureError:
        print("❌ DEBUG ERROR: Token has expired!")
        raise HTTPException(status_code=401, detail="Token has expired. Please login again.")
        
    except JWTError as e:
        print(f"❌ DEBUG ERROR: Token decoding failed! Reason: {str(e)}")
        print(f"Advice: Verify that SECRET_KEY is identical in all files.")
        raise HTTPException(status_code=401, detail="Invalid token signature")

    # Step C: Admin User Validation
    if username == ADMIN_USERNAME:
        print(f"👑 DEBUG: Admin User detected: {username}")
        return User(username=ADMIN_USERNAME, is_staff=True)

    # Step D: Database User Validation
    user = db.query(User).filter(User.username == username).first()
    
    if user is None:
        print(f"❌ DEBUG ERROR: User '{username}' exists in token but not in Database!")
        raise HTTPException(status_code=401, detail="User not found in system")
        
    print(f"👤 DEBUG: Normal User authenticated: {username}")
    return user