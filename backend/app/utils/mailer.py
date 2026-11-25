"""Minimal SMTP mailer (standard library only).

Configure in backend/.env:
    SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, SMTP_FROM, SMTP_USE_TLS
If SMTP_HOST is empty, e-mails are not sent; the message is printed to the
server console instead (handy for local development).
"""
import logging
import os
import smtplib
import ssl
from email.message import EmailMessage

from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


def _cfg(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


def smtp_configured() -> bool:
    # A login user without a password can't send, so treat that as "not configured"
    # and fall back to printing the e-mail in the console.
    if _cfg("SMTP_USER") and not _cfg("SMTP_PASSWORD"):
        return False
    return bool(_cfg("SMTP_HOST"))


def send_email(to: str, subject: str, text: str, html: str | None = None) -> bool:
    """Send an e-mail. Returns True on success. Never raises."""
    if not smtp_configured():
        banner = "=" * 70
        print(f"\n{banner}\n[DEV MAIL — SMTP not configured]\nTo: {to}\nSubject: {subject}\n\n{text}\n{banner}\n", flush=True)
        logger.warning("SMTP not fully configured (SMTP_HOST / SMTP_PASSWORD); e-mail to %s printed to console instead of sent.", to)
        return False

    msg = EmailMessage()
    msg["From"] = _cfg("SMTP_FROM") or _cfg("SMTP_USER")
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(text)
    if html:
        msg.add_alternative(html, subtype="html")

    host, port = _cfg("SMTP_HOST"), int(_cfg("SMTP_PORT", "587") or 587)
    user, password = _cfg("SMTP_USER"), _cfg("SMTP_PASSWORD")
    use_tls = _cfg("SMTP_USE_TLS", "true").lower() in {"1", "true", "yes"}

    try:
        if port == 465:  # implicit TLS
            with smtplib.SMTP_SSL(host, port, context=ssl.create_default_context(), timeout=15) as s:
                if user:
                    s.login(user, password)
                s.send_message(msg)
        else:
            with smtplib.SMTP(host, port, timeout=15) as s:
                if use_tls:
                    s.starttls(context=ssl.create_default_context())
                if user:
                    s.login(user, password)
                s.send_message(msg)
        return True
    except Exception as e:  # never break the request because mail failed
        logger.error("Failed to send e-mail to %s: %s", to, e)
        return False
