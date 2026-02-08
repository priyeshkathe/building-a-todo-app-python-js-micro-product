# =============================================================================
# Part 8: Authentication Helpers (with helper function instead of decorator)
# =============================================================================

import jwt
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
# Note: We don't need 'wraps' anymore since we're not using decorators
from flask import request, jsonify

SECRET_KEY = 'your-secret-key-change-in-production'


# =============================================================================
# PASSWORD FUNCTIONS
# =============================================================================

def hash_password(password):
    return generate_password_hash(password)

def verify_password(password, password_hash):
    return check_password_hash(password_hash, password)


# =============================================================================
# JWT TOKEN FUNCTIONS
# =============================================================================

def create_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def decode_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload['user_id']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


# =============================================================================
# GET CURRENT USER (Helper Function)
# =============================================================================
# Returns: (user, None) if valid, or (None, error_response) if invalid

def get_current_user():
    """
    Validates JWT token and returns current user.
    Returns: (user, None) on success, (None, error_response) on failure
    """
    from models import User

    # Step 1: Check if Authorization header exists
    if 'Authorization' not in request.headers:
        return None, (jsonify({'error': 'Token is missing'}), 401)

    # Step 2: Extract token from "Bearer <token>"
    auth_header = request.headers['Authorization']
    if not auth_header.startswith('Bearer '):
        return None, (jsonify({'error': 'Invalid token format'}), 401)

    token = auth_header.split(' ')[1]

    # Step 3: Decode and validate token
    user_id = decode_token(token)
    if not user_id:
        return None, (jsonify({'error': 'Token is invalid or expired'}), 401)

    # Step 4: Get user from database
    current_user = User.query.get(user_id)
    if not current_user:
        return None, (jsonify({'error': 'User not found'}), 401)

    return current_user, None
