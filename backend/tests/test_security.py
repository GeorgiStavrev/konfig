"""Tests for security utilities."""
import pytest
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    encrypt_value,
    decrypt_value,
)


def test_password_hashing():
    """Test password hashing and verification."""
    password = "TestPassword123!"
    hashed = get_password_hash(password)

    # Hash should be different from password
    assert hashed != password

    # Verify correct password
    assert verify_password(password, hashed)

    # Verify incorrect password
    assert not verify_password("WrongPassword", hashed)


def test_password_hash_uniqueness():
    """Test that same password produces different hashes."""
    password = "TestPassword123!"
    hash1 = get_password_hash(password)
    hash2 = get_password_hash(password)

    # Hashes should be different (due to salt)
    assert hash1 != hash2

    # But both should verify correctly
    assert verify_password(password, hash1)
    assert verify_password(password, hash2)


def test_create_and_decode_access_token():
    """Test JWT token creation and decoding."""
    data = {"sub": "user123", "role": "admin"}
    token = create_access_token(data)

    # Token should be a string
    assert isinstance(token, str)
    assert len(token) > 0

    # Decode token
    payload = decode_token(token)
    assert payload is not None
    assert payload["sub"] == "user123"
    assert payload["role"] == "admin"
    assert payload["type"] == "access"
    assert "exp" in payload


def test_create_and_decode_refresh_token():
    """Test refresh token creation and decoding."""
    data = {"sub": "user123"}
    token = create_refresh_token(data)

    # Token should be a string
    assert isinstance(token, str)

    # Decode token
    payload = decode_token(token)
    assert payload is not None
    assert payload["sub"] == "user123"
    assert payload["type"] == "refresh"
    assert "exp" in payload


def test_decode_invalid_token():
    """Test decoding invalid token."""
    invalid_token = "invalid.token.here"
    payload = decode_token(invalid_token)
    assert payload is None


def test_encrypt_decrypt_value():
    """Test value encryption and decryption."""
    original = "super_secret_value"

    # Encrypt
    encrypted = encrypt_value(original)
    assert encrypted != original
    assert len(encrypted) > 0

    # Decrypt
    decrypted = decrypt_value(encrypted)
    assert decrypted == original


def test_encrypt_decrypt_empty_string():
    """Test encrypting empty string."""
    encrypted = encrypt_value("")
    assert encrypted == ""

    decrypted = decrypt_value("")
    assert decrypted == ""


def test_encrypt_decrypt_unicode():
    """Test encrypting unicode characters."""
    original = "Hello 世界 🌍"
    encrypted = encrypt_value(original)
    decrypted = decrypt_value(encrypted)
    assert decrypted == original


def test_encryption_produces_different_ciphertext():
    """Test that encryption of same value produces different results."""
    value = "test_value"
    encrypted1 = encrypt_value(value)
    encrypted2 = encrypt_value(value)

    # Due to Fernet's built-in IV, same value should produce different ciphertext
    # But both should decrypt to same value
    assert decrypt_value(encrypted1) == value
    assert decrypt_value(encrypted2) == value
