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
   
    return generate_password_hash(password)


def verify_password(password_hash, password):
 
    return check_password_hash(password_hash, password)


# =============================================================================
# JWT TOKEN FUNCTIONS
# =============================================================================

def create_token(user_id, is_admin=False):

    payload = {
        'user_id': user_id,
        'is_admin': is_admin,
        'exp': datetime.utcnow() + timedelta(hours=TOKEN_EXPIRATION_HOURS),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')


def decode_token(token):
   
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return None  # Token expired
    except jwt.InvalidTokenError:
        return None  # Token invalid
