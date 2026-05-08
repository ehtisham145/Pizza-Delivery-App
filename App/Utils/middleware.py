from jose import jwt, JWTError, ExpiredSignatureError
from passlib.context import CryptContext
from fastapi import HTTPException,status,Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from datetime import datetime,timedelta,timezone
from typing import Optional
import os

from App.Database.database import get_db
from App.DataModels.Auth_Users.user_model import User
from App.DataModels.Auth_Users.black_list_token_model import BlackListTokens
from dotenv import load_dotenv
load_dotenv()


# ──-------------------------------------------Config------------------------------------------------------------

SECRET_KEY : str = os.getenv("SECRET_KEY")
REFRESH_SECRET_KEY :str  = os.getenv("REFRESH_SECRET_KEY")
ALGORITHM :str = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES :int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
REFRESH_TOKEN_EXPIRE_DAYS :int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS"))

# ── Shared exception (single source of truth) ───────────────────────────────
CREDENTIALS_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials.",
    headers={"WWW-Authenticate": "Bearer"},
)

# ── OAuth2 scheme ────────────────────────────────────────────────────────────
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# ── Password hashing ─────────────────────────────────────────────────────────
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

#----------------Hash User Password-----------------------
def get_password_hash(password):
    return pwd_context.hash(password)

#----------------Verify Hash Password---------------------
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


#------------ Create Access Token (Used during Login)-------------------

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Short-lived JWT Access Token."""
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    payload = {**data, "exp": expire, "type": "access"}  # ← type claim added
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

#------------- Create Refresh Token (Used for Long Term)-----------------------

def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Long-lived JWT Refresh Token."""
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    )
    payload = {**data, "exp": expire, "type": "refresh"}  # ← type claim added
    return jwt.encode(payload, REFRESH_SECRET_KEY, algorithm=ALGORITHM)



#-------------------Verify User Refresh Token----------------
def verify_refresh_token(token: str):
    try:        
        payload = jwt.decode(token, REFRESH_SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type")!="refresh":
            return None
        return payload

    except (ExpiredSignatureError, JWTError):
        return None


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    # Strip Bearer prefix if client sends it (OAuth2PasswordBearer usually doesn't, but defensive)
    clean_token = token.removeprefix("Bearer ").strip()

    # Reject blacklisted (logged-out) tokens early
    if db.query(BlackListTokens).filter(BlackListTokens.token == clean_token).first():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been invalidated. Please log in again.",
        )

    # Decode and validate
    try:
        payload = jwt.decode(clean_token, SECRET_KEY, algorithms=[ALGORITHM])  # ← was `token`, now `clean_token`
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired. Please authenticate again.",
        )
    except JWTError:
        raise CREDENTIALS_EXCEPTION

    # Ensure this is actually an access token, not a refresh token
    if payload.get("type") != "access":
        raise CREDENTIALS_EXCEPTION

    email: str | None = payload.get("sub")
    if not email:
        raise CREDENTIALS_EXCEPTION

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise CREDENTIALS_EXCEPTION

    return user

# ── Role guard ───────────────────────────────────────────────────────────────
def require_admin(user: User = Depends(get_current_user)):
    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Admin privileges required."
        )
    return user

# ── Role admin or staff ───────────────────────────────────────────────────────────────
def require_admin_or_staff(user: User = Depends(get_current_user)) -> User:
    if user.role not in ("admin", "staff"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: admin or staff role required.",
        )
    return user

def get_user_or_404(user_id: int, db: Session) -> User:
    """Reusable helper — fetch a user or raise 404."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    return user