# =============================================================================
# Part 4: Authentication Helpers
# =============================================================================
# This file contains functions for:
#   1. Password hashing (secure storage)
#   2. Password verification (checking login)
#   3. JWT token creation (for staying logged in)
# =============================================================================

import jwt
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash

# Secret key for JWT - change this in production!
SECRET_KEY = "your-secret-key-change-in-production"

# Token expires after 24 hours
TOKEN_EXPIRATION_HOURS = 24


# =============================================================================
# PASSWORD FUNCTIONS
# =============================================================================

def hash_password(password):
    """
    Convert plain password to secure hash.

    Example:
        "mypassword" -> "pbkdf2:sha256:260000$abc123..."

    The hash cannot be reversed to get the original password.
    """
    return generate_password_hash(password)


def verify_password(password_hash, password):
    """
    Check if plain password matches the stored hash.

    Returns True if password is correct, False otherwise.
    """
    return check_password_hash(password_hash, password)


# =============================================================================
# JWT TOKEN FUNCTIONS
# =============================================================================

def create_token(user_id, is_admin=False):
    """
    Create a JWT token for authenticated user.

    The token contains:
        - user_id: Who this token belongs to
        - is_admin: Whether user is admin
        - exp: When the token expires

    The token is sent to the client and stored in localStorage.
    """
    payload = {
        'user_id': user_id,
        'is_admin': is_admin,
        'exp': datetime.utcnow() + timedelta(hours=TOKEN_EXPIRATION_HOURS),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')


def decode_token(token):
    """
    Decode and verify a JWT token.

    Returns the payload if valid, None if invalid or expired.
    """
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return None  # Token expired
    except jwt.InvalidTokenError:
        return None  # Token invalid
