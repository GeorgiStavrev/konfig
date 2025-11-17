"""Test long password handling."""

from app.core.security import get_password_hash, verify_password


def test_very_long_password():
    """Test that very long passwords (>72 bytes) work correctly."""
    # Create a password that's much longer than 72 bytes
    long_password = "a" * 200  # 200 characters

    # Hash the password (should not raise ValueError)
    hashed = get_password_hash(long_password)

    # Verify the password works
    assert verify_password(long_password, hashed)

    # Verify wrong password doesn't work
    assert not verify_password("wrong_password", hashed)


def test_unicode_long_password():
    """Test long passwords with unicode characters."""
    # Unicode characters can be multiple bytes
    long_password = "🔐" * 100  # Each emoji is 4 bytes, so 400 bytes total

    # Hash the password (should not raise ValueError)
    hashed = get_password_hash(long_password)

    # Verify the password works
    assert verify_password(long_password, hashed)

    # Verify wrong password doesn't work
    assert not verify_password("wrong", hashed)


def test_mixed_length_passwords():
    """Test that passwords of various lengths all work."""
    passwords = [
        "short",
        "a" * 50,  # Below bcrypt limit
        "a" * 72,  # At bcrypt limit
        "a" * 100,  # Above bcrypt limit
        "a" * 500,  # Well above bcrypt limit
    ]

    for password in passwords:
        hashed = get_password_hash(password)
        assert verify_password(password, hashed)
        assert not verify_password("wrong", hashed)
