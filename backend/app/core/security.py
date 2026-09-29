"""Security helpers: password hashing and opaque token generation/hashing.

Sessions and password-reset tokens are *opaque* random tokens. The plaintext
token is handed to the client; the server stores only a SHA-256 hash so that a
database leak does not expose usable tokens (rule: "Reset secrets are not
stored as readable text").
"""

from __future__ import annotations

import hashlib
import secrets

from passlib.context import CryptContext

# passlib 1.7.4 + bcrypt 4.x: pin bcrypt at 4.0.1 to avoid the
# "attribute 'bcrypt' has no attribute '__about__'" runtime issue.
_pwd_context = CryptContext(schemes=["bcrypt_sha256", "bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return _pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return _pwd_context.verify(plain_password, hashed_password)
    except (ValueError, TypeError):
        return False


def generate_token() -> str:
    """Generate a URL-safe random token (>= 43 chars of entropy)."""
    return secrets.token_urlsafe(32)


def hash_token(token: str) -> str:
    """One-way hash of a token for storage. The plaintext is never stored."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def constant_time_eq(a: str, b: str) -> bool:
    return secrets.compare_digest(a, b)
