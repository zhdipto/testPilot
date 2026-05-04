"""Sample authentication module for testing AI generation."""

import hashlib
import os

def hash_password(password: str, salt: str = None) -> tuple[str, str]:
    """Hash a password with an optional salt."""
    if salt is None:
        salt = os.urandom(16).hex()
    hashed = hashlib.sha256((password + salt).encode('utf-8')).hexdigest()
    return hashed, salt

def verify_password(password: str, hashed: str, salt: str) -> bool:
    """Verify a password matches the hash and salt."""
    new_hash, _ = hash_password(password, salt)
    return new_hash == hashed
