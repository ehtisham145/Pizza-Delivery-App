"""Forgot / reset password.

POST /auth/forgot-password  {email}
    Always answers the same way, whether or not the e-mail exists, so the
    endpoint can't be used to discover registered accounts. If the account
    exists and is active, a one-time link is e-mailed (valid 30 min by default).

POST /auth/reset-password   {token, new_password, confirm_password}
    Sets the new password, marks the token used, and signs the user out of
    every device by deleting their refresh tokens.
"""
import hashlib
import logging
import os
import secrets
from datetime import datetime, timedelta
from html import escape
from typing import Annotated

from dotenv import load_dotenv
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from pydantic import AfterValidator, BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.datamodels.Auth_Users.password_reset_model import PasswordResetToken
from app.datamodels.Auth_Users.refresh_token_model import RefreshTokenModel
from app.datamodels.Auth_Users.user_model import User
from app.utils.db_helper import safe_commit
from app.utils.mailer import send_email
from app.utils.middleware import get_password_hash
from app.utils.validator import validate_password_strength

load_dotenv()
logger = logging.getLogger(__name__)

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173").rstrip("/")
EXPIRE_MINUTES = int(os.getenv("PASSWORD_RESET_EXPIRE_MINUTES", "30") or 30)
RESEND_COOLDOWN_SECONDS = 60
BRAND = os.getenv("BRAND_NAME", "Ehtisham Pizza Services")

GENERIC_REPLY = {
    "message": "If an account exists for that e-mail, we've sent a link to reset the password. Check your inbox (and spam folder)."
}

reset_router = APIRouter()

PasswordStr = Annotated[str, AfterValidator(validate_password_strength)]


class ForgotPasswordRequest(BaseModel):
    email: EmailStr = Field(..., description="Account e-mail")


class ResetPasswordRequest(BaseModel):
    token: str = Field(..., min_length=20, max_length=200, description="Token from the e-mailed link")
    new_password: PasswordStr = Field(..., description="New password")
    confirm_password: str = Field(..., description="Repeat the new password")


def _hash(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _send_reset_email(to: str, name: str, link: str) -> None:
    text = (
        f"Hi {name},\n\n"
        f"We received a request to reset your {BRAND} password.\n"
        f"Open this link to choose a new one (valid for {EXPIRE_MINUTES} minutes):\n\n{link}\n\n"
        "If you didn't ask for this, you can ignore this e-mail. Your password won't change.\n"
    )
    html = f"""\
<div style="font-family:Arial,sans-serif;max-width:480px;margin:auto;color:#1F2937">
  <h2 style="color:#D92B2B;margin-bottom:4px">{escape(BRAND)}</h2>
  <p>Hi {escape(name)},</p>
  <p>We received a request to reset your password. This link is valid for {EXPIRE_MINUTES} minutes.</p>
  <p style="margin:28px 0">
    <a href="{escape(link)}" style="background:#D92B2B;color:#fff;padding:12px 22px;border-radius:10px;text-decoration:none;font-weight:bold">Reset my password</a>
  </p>
  <p style="font-size:13px;color:#6B7280">If the button doesn't work, copy this link:<br>{escape(link)}</p>
  <p style="font-size:13px;color:#6B7280">Didn't ask for this? Ignore this e-mail. Your password won't change.</p>
</div>"""
    send_email(to, f"Reset your {BRAND} password", text, html)


@reset_router.post("/forgot-password", status_code=status.HTTP_200_OK, summary="E-mail a password reset link")
def forgot_password(payload: ForgotPasswordRequest, background: BackgroundTasks, db: Session = Depends(get_db)):
    email = payload.email.strip().lower()
    user = db.query(User).filter(User.email.ilike(email)).first()

    if not user or not user.is_active:
        return GENERIC_REPLY

    now = datetime.utcnow()
    latest = (
        db.query(PasswordResetToken)
        .filter(PasswordResetToken.user_id == user.id)
        .order_by(PasswordResetToken.created_at.desc())
        .first()
    )
    if latest and not latest.used and (now - latest.created_at).total_seconds() < RESEND_COOLDOWN_SECONDS:
        return GENERIC_REPLY  # throttle repeated clicks; the earlier link still works

    # Only the newest link should work.
    db.query(PasswordResetToken).filter(
        PasswordResetToken.user_id == user.id, PasswordResetToken.used.is_(False)
    ).update({"used": True}, synchronize_session=False)

    token = secrets.token_urlsafe(32)
    db.add(PasswordResetToken(user_id=user.id, token_hash=_hash(token), created_at=now, expires_at=now + timedelta(minutes=EXPIRE_MINUTES)))
    safe_commit(db)

    link = f"{FRONTEND_URL}/reset-password?token={token}"
    # Send after the response so timing doesn't reveal whether the account exists.
    background.add_task(_send_reset_email, user.email, user.full_name, link)
    return GENERIC_REPLY


@reset_router.post("/reset-password", status_code=status.HTTP_200_OK, summary="Set a new password using a reset link")
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    if payload.new_password != payload.confirm_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords don't match.")

    record = db.query(PasswordResetToken).filter(PasswordResetToken.token_hash == _hash(payload.token)).first()
    if not record or record.used or record.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This reset link is invalid or has expired. Please request a new one.",
        )

    user = db.query(User).filter(User.id == record.user_id).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This account can't be reset. Please contact support.")

    user.password = get_password_hash(payload.new_password)
    record.used = True
    # Sign out everywhere: existing refresh tokens stop working.
    db.query(RefreshTokenModel).filter(RefreshTokenModel.user_id == user.id).delete(synchronize_session=False)
    safe_commit(db)

    return {"message": "Your password has been updated. You can log in now."}
