# Part 4: User Login & Authentication

In this chapter, we fix the critical security flaw from Part 3 and build a complete login system.

Part 3 stored passwords in plain text — anyone with database access could see them. In this part, we introduce **password hashing** to store passwords securely and **JWT tokens** to manage user sessions.

This chapter transforms our app from "anyone can see passwords" to "industry-standard secure authentication."

---

## What You Will Learn

By the end of this chapter, you will understand:

- Why and how to hash passwords (never store plain text!)
- How password verification works without storing the actual password
- What JWT tokens are and why we use them
- How to create and decode JWT tokens
- How localStorage works for client-side storage
- How to build a complete login/logout flow

---

## Why This Chapter Matters

Authentication is the foundation of secure applications:

- **Password hashing** protects users even if your database is breached
- **JWT tokens** let the server identify users without storing session data
- **localStorage** provides persistent client-side storage for the browser
- These concepts apply to virtually every web application you'll build

---

## Project Structure

```
part-4-user-login/
├── app.py              # Flask app with login & register endpoints
├── auth.py             # Authentication helpers (hashing, JWT)
├── models.py           # Database models
├── requirements.txt    # Python dependencies
├── templates/
│   ├── index.html      # Home page (explains JWT flow)
│   ├── register.html   # Registration form (now with hashing)
│   ├── login.html      # Login form (NEW)
│   └── dashboard.html  # Protected user dashboard (NEW)
```

---

## How to Run

```bash
cd part-4-user-login
pip install -r requirements.txt
python app.py
```

Open in browser: http://127.0.0.1:5000

---

## Key Concepts

### 1. Password Hashing: The Security Fix

**The Problem (Part 3):**
```
User enters: "secret123"
Database stores: "secret123"  ← Anyone can read this!
```

**The Solution (Part 4):**
```
User enters: "secret123"
Database stores: "pbkdf2:sha256:260000$xyz...abc"  ← Cannot reverse!
```

**What is Hashing?**
- A one-way transformation of the password
- Same input always produces same output
- Cannot reverse the hash to get the original password
- Includes "salt" (random data) to prevent rainbow table attacks

```python
from werkzeug.security import generate_password_hash, check_password_hash

# Hash a password (during registration)
hash = generate_password_hash("secret123")
# Result: "pbkdf2:sha256:260000$abc123...xyz789"

# Verify a password (during login)
is_valid = check_password_hash(hash, "secret123")  # True
is_valid = check_password_hash(hash, "wrongpass")  # False
```

---

### 2. The auth.py Module

This file contains all authentication-related functions:

```python
# auth.py

from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from datetime import datetime, timedelta

SECRET_KEY = 'your-secret-key-here'
TOKEN_EXPIRATION_HOURS = 24

def hash_password(password):
    """Convert plain password to secure hash"""
    return generate_password_hash(password)

def verify_password(password_hash, password):
    """Check if password matches the stored hash"""
    return check_password_hash(password_hash, password)

def create_token(user_id, is_admin=False):
    """Create a JWT token for the user"""
    payload = {
        'user_id': user_id,
        'is_admin': is_admin,
        'exp': datetime.utcnow() + timedelta(hours=TOKEN_EXPIRATION_HOURS),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def decode_token(token):
    """Decode and verify a JWT token"""
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return None  # Token has expired
    except jwt.InvalidTokenError:
        return None  # Token is invalid
```

---

### 3. Registration with Password Hashing

The registration endpoint now hashes passwords before storing:

```python
@app.route('/api/register', methods=['POST'])
def api_register():
    data = request.get_json()

    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    # Validate password length
    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400

    # Check for duplicates...

    # Create user with HASHED password
    new_user = User(
        username=username,
        email=email,
        password_hash=hash_password(password)  # NOW SECURE!
    )
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'Registration successful!'}), 201
```

---

### 4. The Login Endpoint

```python
@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()

    email = data.get('email')
    password = data.get('password')

    # Step 1: Find user by email
    user = User.query.filter_by(email=email).first()

    # Step 2: Verify password (using hash comparison)
    if not user or not verify_password(user.password_hash, password):
        return jsonify({'error': 'Invalid email or password'}), 401

    # Step 3: Create JWT token
    token = create_token(user.id, user.is_admin)

    # Step 4: Return token and user info
    return jsonify({
        'message': 'Login successful!',
        'token': token,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'is_admin': user.is_admin
        }
    }), 200
```

**Security Note:** We return the same error message for both "user not found" and "wrong password" to prevent attackers from knowing which emails are registered.

---

### 5. JWT Tokens Explained

**What is a JWT?**

JWT (JSON Web Token) is a compact, URL-safe way to represent claims between two parties.

**Structure:**
```
eyJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoxfQ.signature
└─────── Header ───────┘└───── Payload ─────┘└── Sig ──┘
```

Three parts separated by dots:
1. **Header**: Algorithm and token type
2. **Payload**: The data (claims)
3. **Signature**: Verification hash

**Our Payload Contains:**
```python
{
    'user_id': 1,           # Which user this token belongs to
    'is_admin': False,      # Admin status
    'exp': 1679675600,      # Expiration timestamp
    'iat': 1679589200       # Issued at timestamp
}
```

**Why JWT?**
- **Stateless**: Server doesn't need to store sessions
- **Self-contained**: Contains all needed user info
- **Secure**: Signed with secret key, tamper-proof
- **Portable**: Can be used across different servers

---

### 6. localStorage: Browser Storage

localStorage is a browser API for storing data on the client side.

```javascript
// Store data (survives browser restart)
localStorage.setItem('token', 'eyJhbGc...');
localStorage.setItem('user', JSON.stringify({id: 1, username: 'john'}));

// Retrieve data
const token = localStorage.getItem('token');
const user = JSON.parse(localStorage.getItem('user'));

// Remove specific item
localStorage.removeItem('token');

// Clear all data
localStorage.clear();
```

**Characteristics:**
| Feature | localStorage |
|---------|--------------|
| Persistence | Survives browser close |
| Capacity | ~5-10 MB |
| Scope | Same origin (domain) only |
| Sent with requests | No (must add manually) |
| Access | JavaScript only |

---

### 7. Login Form (login.html)

```html
<form id="login-form">
    <input type="email" id="email" placeholder="Email" required>
    <input type="password" id="password" placeholder="Password" required>
    <button type="submit">Login</button>
</form>
```

```javascript
document.getElementById('login-form').addEventListener('submit', async function(e) {
    e.preventDefault();

    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    const response = await fetch('/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
    });

    const data = await response.json();

    if (response.ok) {
        // Store token and user in localStorage
        localStorage.setItem('token', data.token);
        localStorage.setItem('user', JSON.stringify(data.user));

        // Redirect to dashboard
        window.location.href = '/dashboard';
    } else {
        showAlert(data.error, 'danger');
    }
});
```

---

### 8. The Dashboard (Protected Page)

The dashboard checks if the user is logged in:

```javascript
// Check authentication on page load
const token = localStorage.getItem('token');
const user = JSON.parse(localStorage.getItem('user') || 'null');

if (!token || !user) {
    // Not logged in - redirect to login page
    window.location.href = '/login';
} else {
    // Logged in - show user info
    document.getElementById('user-info').textContent = `Hello, ${user.username}`;
    document.getElementById('user-id').textContent = user.id;
    document.getElementById('user-email').textContent = user.email;
    document.getElementById('token-display').textContent = token;
}

// Logout function
function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    window.location.href = '/';
}
```

**Note:** This protection is frontend-only! The server still serves the dashboard page. True protection requires checking the token on API calls (Part 6).

---

## The Complete Authentication Flow

```
┌──────────────────────────────────────────────────────────────────┐
│                        REGISTRATION                               │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│   User                     Frontend                  Backend      │
│    │                          │                         │        │
│    │── fills form ──────────>│                         │        │
│    │                          │── POST /api/register ─>│        │
│    │                          │   {email, password}    │        │
│    │                          │                         │        │
│    │                          │                    hash_password()│
│    │                          │                    save to DB     │
│    │                          │                         │        │
│    │                          │<── 201 Created ────────│        │
│    │<── "Success!" ──────────│                         │        │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                           LOGIN                                   │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│   User                     Frontend                  Backend      │
│    │                          │                         │        │
│    │── enters credentials ──>│                         │        │
│    │                          │── POST /api/login ────>│        │
│    │                          │   {email, password}    │        │
│    │                          │                         │        │
│    │                          │                verify_password()  │
│    │                          │                create_token()     │
│    │                          │                         │        │
│    │                          │<── {token, user} ──────│        │
│    │                          │                         │        │
│    │               localStorage.setItem('token', ...)  │        │
│    │               localStorage.setItem('user', ...)   │        │
│    │                          │                         │        │
│    │<── redirect to dashboard │                         │        │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                      DASHBOARD ACCESS                             │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│   User                     Frontend                  Backend      │
│    │                          │                         │        │
│    │── visits /dashboard ───>│                         │        │
│    │                          │                         │        │
│    │               check localStorage:                  │        │
│    │               - token exists?                      │        │
│    │               - user exists?                       │        │
│    │                          │                         │        │
│    │   if NO: redirect to /login                        │        │
│    │   if YES: display dashboard                        │        │
│    │                          │                         │        │
│    │<── shows user info ─────│                         │        │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## Password Security: Before and After

### Part 3 (INSECURE)

```
Registration:
password = "secret123"
database.store("secret123")  ← Plain text!

Login:
input = "secret123"
if input == database.password:  ← Direct comparison
    login_success()
```

### Part 4 (SECURE)

```
Registration:
password = "secret123"
hash = "pbkdf2:sha256:260000$salt$abc123..."
database.store(hash)  ← Only hash stored

Login:
input = "secret123"
if verify_hash(database.hash, input):  ← Hash comparison
    login_success()
```

**Even if the database is stolen:**
- Part 3: Attacker gets all passwords immediately
- Part 4: Attacker gets hashes that are computationally expensive to crack

---

## What the Token Looks Like

You can decode your JWT at https://jwt.io:

```
Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJpc19hZG1pbiI6ZmFsc2UsImV4cCI6MTY3OTY3NTYwMCwiaWF0IjoxNjc5NTg5MjAwfQ.signature

Decoded:
{
  "alg": "HS256",      ← Header: Algorithm
  "typ": "JWT"
}
{
  "user_id": 1,        ← Payload: Our data
  "is_admin": false,
  "exp": 1679675600,   ← Expiration time
  "iat": 1679589200    ← Issued at time
}
```

**Important:** The payload is NOT encrypted, only signed! Don't put sensitive data in JWTs.

---

## HTTP Response Codes

| Code | Name | When Used |
|------|------|-----------|
| 200 | OK | Login successful |
| 201 | Created | Registration successful |
| 400 | Bad Request | Validation failed (short password, etc.) |
| 401 | Unauthorized | Invalid credentials |

---

## Comparison: Part 3 vs Part 4

| Feature | Part 3 | Part 4 |
|---------|--------|--------|
| Password Storage | Plain text | Hashed (PBKDF2-SHA256) |
| Password Validation | None | Minimum 6 characters |
| Login | No | Yes |
| Token | No | JWT with 24h expiry |
| Session Storage | No | localStorage |
| Dashboard | No | Yes (protected page) |
| Logout | No | Yes |

---

## Try It Yourself

### Activity 1: Compare Password Storage
1. Register a user in Part 3 (`cd part-3-user-registration && python app.py`)
2. Visit `/users` — see the plain text password
3. Register a user in Part 4 (`cd part-4-user-login && python app.py`)
4. Check the database — password is now hashed!

### Activity 2: Decode Your Token
1. Log in and go to the dashboard
2. Copy the token displayed
3. Go to https://jwt.io
4. Paste your token
5. See the decoded payload (user_id, exp, etc.)

### Activity 3: Test Token Expiration
1. In `auth.py`, change `TOKEN_EXPIRATION_HOURS = 24` to `TOKEN_EXPIRATION_HOURS = 0.001` (about 3.6 seconds)
2. Log in
3. Wait 5 seconds
4. The token is now expired (you'd see this in Part 6 when validating)

### Activity 4: Inspect localStorage
1. Log in to the app
2. Open DevTools (F12) → Application tab → Local Storage
3. See the `token` and `user` entries
4. Try modifying the user object — what happens?

---

## Self-Study Questions

1. Why can't we reverse a hashed password to get the original?
2. What would happen if two users have the same password? Would their hashes be the same?
3. Why do we use `exp` claim in JWT instead of storing session data on the server?
4. What's the difference between localStorage and sessionStorage?
5. Why do we return "Invalid email or password" instead of "User not found" or "Wrong password"?

---

## Security Notes

### What We've Fixed
- Passwords are now hashed (cannot be reversed)
- Login creates a signed token (cannot be forged)
- Token has expiration (limits damage if stolen)

### What's Still Missing (Fixed in Parts 5-6)
- Backend doesn't validate tokens on API calls yet
- Dashboard protection is frontend-only
- Anyone can access `/dashboard` directly (though they won't have data)

---

## Next Part

In **Part 5: Todo CRUD**, we will:
- Add create, read, update, delete operations for todos
- Use the user info from localStorage to associate todos with users
- **Note:** Part 5 has a security flaw (user_id sent from frontend) that Part 6 fixes
