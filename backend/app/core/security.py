"""Security utilities for authentication and encryption."""

import base64
import hashlib
from datetime import datetime, timedelta
from typing import Optional

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _prehash_password(password: str) -> str:
    """
    Pre-hash password with SHA256 to handle long passwords.

    Bcrypt has a 72-byte limit. To handle longer passwords securely,
    we first hash with SHA256, then use bcrypt on the result.
    """
    # Hash the password with SHA256 and encode as base64
    password_bytes = password.encode("utf-8")
    sha256_hash = hashlib.sha256(password_bytes).digest()
    # Encode as base64 to get a string that bcrypt can work with
    return base64.b64encode(sha256_hash).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    # Pre-hash the password before verification
    prehashed = _prehash_password(plain_password)
    return pwd_context.verify(prehashed, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a password using SHA256 + bcrypt.

    This prevents bcrypt's 72-byte limit from being an issue.
    """
    # Pre-hash the password with SHA256 before bcrypt
    prehashed = _prehash_password(password)
    return pwd_context.hash(prehashed)


# JWT token handling
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.access_token_expire_minutes
        )
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(
        to_encode, settings.secret_key, algorithm=settings.algorithm
    )
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """Create a JWT refresh token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(
        to_encode, settings.secret_key, algorithm=settings.algorithm
    )
    return encoded_jwt


def decode_token(token: str) -> Optional[dict]:
    """Decode and verify a JWT token."""
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        return payload
    except JWTError:
        return None


# Data encryption at rest
class EncryptionService:
    """Service for encrypting and decrypting data at rest."""

    def __init__(self):
        """Initialize encryption service with the configured key."""
        # Derive a valid Fernet key from the encryption key
        self.fernet = self._get_fernet()

    def _get_fernet(self) -> Fernet:
        """Get Fernet cipher instance."""
        # If the encryption key is already a valid base64-encoded 32-byte key, use it
        # Otherwise, derive one using PBKDF2
        try:
            # Try to use it directly if it's already valid
            return Fernet(settings.encryption_key.encode())
        except Exception:
            # Derive a key using PBKDF2
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=b"konfig_salt_change_in_production",  # Should be random per deployment
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(settings.encryption_key.encode()))
            return Fernet(key)

    def encrypt(self, data: str) -> str:
        """Encrypt data."""
        if not data:
            return data
        encrypted = self.fernet.encrypt(data.encode())
        return base64.urlsafe_b64encode(encrypted).decode()

    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt data."""
        if not encrypted_data:
            return encrypted_data
        try:
            decoded = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted = self.fernet.decrypt(decoded)
            return decrypted.decode()
        except Exception:
            # If decryption fails, return empty string
            return ""


# Singleton instance
encryption_service = EncryptionService()


def encrypt_value(value: str) -> str:
    """Encrypt a configuration value."""
    return encryption_service.encrypt(value)


def decrypt_value(encrypted_value: str) -> str:
    """Decrypt a configuration value."""
    return encryption_service.decrypt(encrypted_value)
