from fastapi import HTTPException, Depends, APIRouter, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import os
import logging
from App.Database.database import get_db
from App.DataModels.Auth_Users.refresh_token_model import RefreshTokenModel
from App.DataModels.Auth_Users.user_model import User
from App.DataModels.Auth_Users.black_list_token_model import BlackListTokens
from App.Schemas.Auth_Users.Token_Schema.refresh_token_schema import RefreshTokenRequest
from App.Schemas.Auth_Users.User_Schema.register_schema import UserRegisterSchema, UserResponseSchema
from App.Schemas.Auth_Users.User_Schema.login_schema import UserLoginResponseSchema
from App.Utils.middleware import (
    get_current_user,
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_refresh_token,
)
from App.Utils.db_helper import safe_commit
from dotenv import load_dotenv
load_dotenv()

# ------------------------------------------------------------------ #
#  Logger
# ------------------------------------------------------------------ #
logger = logging.getLogger(__name__)

# ------------------------------------------------------------------ #
#  Config
# ------------------------------------------------------------------ #
ALGORITHM  = os.getenv("ALGORITHM")
SECRET_KEY = os.getenv("SECRET_KEY")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# FIX #1 ✅ — Define _DUMMY_HASH so timing-safe comparison works even
#             when the supplied e-mail does not exist in the database.
_DUMMY_HASH = get_password_hash("dummy_placeholder_to_prevent_timing_attack")

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

auth_router = APIRouter()


# ================================================================== #
# 1. REGISTER
# ================================================================== #
@auth_router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=UserResponseSchema,
    summary="Register a new user",
)
def register_user(user: UserRegisterSchema, db: Session = Depends(get_db)):
    """
    Handles new user registration: checks for existing email,
    hashes password, and persists user to the database.
    """
    # 1. Check if a user with the provided email already exists
    existing_user = db.query(User).filter(User.email == user.email).first()

    # 2. Raise error if user already exists
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email address is already registered.",
        )

    # 3. Securely hash the plain-text password
    hashed_password = get_password_hash(user.password)

    # 4. Build the ORM object
    new_user = User(
        full_name=user.full_name,
        email=user.email,
        password=hashed_password,
        phone_number=user.phone_number,
        role="customer",
    )

    # 5. Persist with robust error handling
    try:
        db.add(new_user)
        safe_commit(db)
        db.refresh(new_user)
        return new_user   # ✅ return ORM object (matches UserResponseSchema)

    except IntegrityError as e:
        db.rollback()
        logger.error(f"Integrity error during registration: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Registration failed: possible duplicate data detected.",
        )

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error during registration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal database error occurred. Please try again later.",
        )

    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error during registration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected server error occurred.",
        )

    # FIX #2 ✅ — Dead / wrong-object return block has been removed entirely.


# ================================================================== #
# 2. LOGIN
# ================================================================== #
@auth_router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    response_model=UserLoginResponseSchema,
    summary="Login to your account",
)
def login(data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # 1. Find user in database
    db_user = db.query(User).filter(User.email == data.username).first()

    # 2. Timing-safe password check
    #    FIX #1 ✅ — _DUMMY_HASH is now defined; no NameError on bad e-mail.
    password_to_check = db_user.password if db_user else _DUMMY_HASH
    password_valid = verify_password(data.password, password_to_check)

    # 3. Validate credentials
    if not db_user or not password_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 4. Check account status
    if not db_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This account is disabled. Please contact Admin.",
        )

    # 5. Create tokens
    token_data = {"sub": db_user.email, "Role": db_user.role}
    access_token    = create_access_token(data=token_data)
    refresh_token_jwt = create_refresh_token(data=token_data)

    now        = datetime.utcnow()
    expires_at = now + timedelta(days=7)

    # 6. Persist refresh token
    new_db_refresh_token = RefreshTokenModel(
        token=refresh_token_jwt,
        user_id=db_user.id,
        created_at=now,
        expires_at=expires_at,
        is_revoked=False,
    )

    try:
        db.add(new_db_refresh_token)
        safe_commit(db)
        db.refresh(new_db_refresh_token)
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to persist refresh token during login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed — could not save session. Please try again.",
        )

    # 7. Return response
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "email": db_user.email,
        "full_name": db_user.full_name,
        "refresh_token": {
            "refresh_token": refresh_token_jwt,
            "user_id": db_user.id,
            "created_at": now,
            "expires_at": expires_at,
            "is_revoked": False,
        },
    }


# ================================================================== #
# 3. LOGOUT
# ================================================================== #
@auth_router.post("/logout", status_code=status.HTTP_200_OK)
def logout(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # 1. Strip any accidental "Bearer " prefix
    clean_token = token.replace("Bearer ", "").strip()

    # 2. Idempotent: already blacklisted?
    already_blacklisted = (
        db.query(BlackListTokens)
        .filter(BlackListTokens.token == clean_token)
        .first()
    )
    if already_blacklisted:
        return {"message": "Already logged out."}

    # 3. Blacklist the token
    db.add(BlackListTokens(token=clean_token))
    safe_commit(db)

    return {"message": "Logout successful!"}


# ================================================================== #
# 4. REFRESH TOKEN
# ================================================================== #
@auth_router.post("/refresh-token", status_code=status.HTTP_200_OK)
def refresh_access_token(payload: RefreshTokenRequest, db: Session = Depends(get_db)):
    # 1. Verify JWT signature + expiry
    decoded_data = verify_refresh_token(payload.refresh_token)
    if not decoded_data:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    username = decoded_data.get("sub")

    # 2. Confirm token exists in DB
    db_token = (
        db.query(RefreshTokenModel)
        .filter(RefreshTokenModel.token == payload.refresh_token)
        .first()
    )

    # FIX #3 ✅ — Also reject tokens that are flagged as revoked.
    if not db_token or db_token.is_revoked:
        raise HTTPException(status_code=401, detail="Token revoked or already used")

    # 3. Generate a fresh token pair
    token_data  = {"sub": username}
    new_access  = create_access_token(data=token_data)
    new_refresh = create_refresh_token(data=token_data)

    now = datetime.utcnow()

    # 4. Atomic swap: delete old, insert new
    try:
        db.delete(db_token)
        db.add(
            RefreshTokenModel(
                token=new_refresh,
                user_id=db_token.user_id,
                created_at=now,                          # FIX #6 ✅ — set explicitly
                expires_at=now + timedelta(days=7),
                is_revoked=False,
            )
        )
        safe_commit(db)
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to rotate refresh token: {e}")
        raise HTTPException(status_code=500, detail="Could not update security tokens")

    return {
        "access_token": new_access,
        "refresh_token": new_refresh,
        "token_type": "bearer",
    }