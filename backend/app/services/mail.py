"""Transactional password recovery mail. Never log tokens or SMTP credentials."""
import smtplib
import ssl
from email.message import EmailMessage
from urllib.parse import quote

from app.config import get_settings


def send_password_reset(email: str, token: str) -> None:
    settings = get_settings()
    if not settings.smtp_host:
        if settings.environment == "testing" or settings.expose_reset_tokens:
            return
        raise RuntimeError("Password recovery delivery is not configured.")
    message = EmailMessage()
    message["Subject"] = "Reset your Nashaa password"
    message["From"] = settings.smtp_from
    message["To"] = email
    # Fragment keeps the secret out of HTTP request/access logs.
    link = f"{settings.reset_url}#token={quote(token, safe='')}"
    message.set_content(
        f"Use this single-use link to reset your Nashaa password:\n{link}\n\n"
        f"It expires in {settings.reset_expire_seconds // 60} minutes. "
        "If you did not request this, ignore this message."
    )
    with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=15) as smtp:
        if settings.smtp_starttls:
            smtp.starttls(context=ssl.create_default_context())
        if settings.smtp_username:
            smtp.login(settings.smtp_username, settings.smtp_password)
        smtp.send_message(message)
