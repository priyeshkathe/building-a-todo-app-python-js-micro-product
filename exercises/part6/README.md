# Part 6: Protected Routes

In this chapter, we move from basic authentication to real authorization.

Up until now, users could log in — but the backend had no reliable way to know who was making each request.
In this part, we solve that problem by introducing protected routes, JWT validation, and user ownership checks.

This chapter lays the foundation for secure APIs and prepares us for admin-only access in the next part.

---

## What You Will Learn

By the end of this chapter, you will understand:

- How to identify the logged-in user on every API request
- How JWT tokens are sent using the Authorization header
- How to protect routes using a `get_current_user()` helper function
- How to enforce user ownership (authorization)
- When to return 401 Unauthorized vs 403 Forbidden

---

## Why This Chapter Matters

HTTP is stateless.

This means:

- The server does not remember users between requests
- Each API call must prove identity again
- "Being logged in" is not a backend concept by default

To build real applications, the backend must:

- **Know** who is making the request (Authentication)
- **Decide** what they are allowed to access (Authorization)
- **Protect** private data from other users

This chapter solves all of that.

---

## Core Idea: JWT-Based Identity Per Request

We use JSON Web Tokens (JWTs) to identify users on every request.

### Authentication Flow

```
1. User logs in
2. Backend generates a JWT containing the user ID
3. Frontend stores the token (localStorage)
4. Every protected request sends the token
5. Backend decodes the token and identifies the user
```

```
Frontend ── Authorization: Bearer <JWT> ──> Backend
```

Each request is authenticated independently.

---

## Project Structure

```
part-6-protected-routes/
├── app.py              # Flask app with protected routes
├── models.py           # Database models
├── auth.py             # Auth helpers (JWT + user validation)
├── requirements.txt    # Python dependencies
├── templates/
│   ├── index.html      # Home page
│   ├── register.html   # Registration form
│   ├── login.html      # Login form
│   └── dashboard.html  # Protected dashboard
```

---

## How to Run

```bash
cd part-6-protected-routes
pip install -r requirements.txt
python app.py
```

Open in browser: http://127.0.0.1:5000

---

## Key Concepts

### 1. Authorization Header

JWT tokens are sent using the standard HTTP header:

```
Authorization: Bearer <token>
```

**Frontend example:**

```javascript
fetch('/api/todos', {
    headers: {
        'Authorization': 'Bearer ' + token
    }
})
```

This approach:

- Is industry-standard (used by most APIs)
- Works with APIs, SPAs, and mobile apps
- Keeps authentication separate from request data

---

### 2. get_current_user() Helper Function

This helper function is the heart of protected routes.

It:
1. Validates the JWT
2. Extracts the user ID
3. Loads the user from the database
4. Returns proper error responses when authentication fails

**Usage inside a route:**

```python
@app.route('/api/todos', methods=['GET'])
def get_todos():
    current_user, error = get_current_user()
    if error:
        return error  # Returns 401 if not authenticated

    # Only authenticated users reach here
    todos = Todo.query.filter_by(user_id=current_user.id).all()
    return jsonify({'todos': [...]})
```

Only authenticated users reach the protected logic.

---

### 3. How get_current_user() Works

```python
def get_current_user():
    """
    Validates JWT token and returns current user.
    Returns: (user, None) if valid, or (None, error_response) if invalid
    """

    # Step 1: Check if Authorization header exists
    if 'Authorization' not in request.headers:
        return None, (jsonify({'error': 'Token is missing'}), 401)

    # Step 2: Extract token from "Bearer <token>"
    auth_header = request.headers['Authorization']
    if not auth_header.startswith('Bearer '):
        return None, (jsonify({'error': 'Invalid token format'}), 401)

    token = auth_header.split(' ')[1]

    # Step 3: Decode and validate token
    data = decode_token(token)
    if not data:
        return None, (jsonify({'error': 'Token is invalid or expired'}), 401)

    # Step 4: Load user from database
    current_user = User.query.get(data['user_id'])
    if not current_user:
        return None, (jsonify({'error': 'User not found'}), 401)

    # Step 5: Return user (success!)
    return current_user, None
```

This ensures:

- Tokens are required
- Tokens are valid and not expired
- Users actually exist in the database

---

### 4. Ownership Verification (Authorization)

Authentication alone is not enough.

We must ensure users can only access **their own data**:

```python
@app.route('/api/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    # Step 1: Authenticate
    current_user, error = get_current_user()
    if error:
        return error

    # Step 2: Find the todo
    todo = Todo.query.get(todo_id)
    if not todo:
        return jsonify({'error': 'Todo not found'}), 404

    # Step 3: Authorize - check ownership
    if todo.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    # Step 4: Safe to update
    data = request.get_json()
    if 'is_completed' in data:
        todo.is_completed = data['is_completed']

    db.session.commit()
    return jsonify({'message': 'Todo updated!'})
```

This prevents:

- User A from viewing User B's todos
- User A from modifying User B's todos
- User A from deleting User B's todos

---

### 5. 401 vs 403: When to Use Each

| Code | Name | When to Use |
|------|------|-------------|
| **401** | Unauthorized | User is not logged in (no token, invalid token) |
| **403** | Forbidden | User is logged in but not allowed to access this resource |

**Think of it this way:**

- **401**: "Who are you?" (Identity problem)
- **403**: "I know who you are, but you can't do that." (Permission problem)

**Examples:**

```python
# 401 - No token provided
if 'Authorization' not in request.headers:
    return jsonify({'error': 'Token is missing'}), 401

# 403 - Token valid, but not authorized
if todo.user_id != current_user.id:
    return jsonify({'error': 'Unauthorized'}), 403
```

---

## Comparison: Part 5 vs Part 6

### Part 5 (Insecure)

```javascript
// Frontend sends user_id explicitly
fetch('/api/todos', {
    method: 'POST',
    body: JSON.stringify({
        task_content: 'Buy milk',
        user_id: user.id  // Anyone could change this!
    })
})
```

```python
# Backend trusts whatever user_id is sent
user_id = data.get('user_id')  # From request body
```

### Part 6 (Secure)

```javascript
// Frontend sends JWT token in header
fetch('/api/todos', {
    method: 'POST',
    headers: {
        'Authorization': 'Bearer ' + token  // Cryptographically signed
    },
    body: JSON.stringify({
        task_content: 'Buy milk'
        // No user_id sent - backend gets it from token
    })
})
```

```python
# Backend extracts user_id from validated token
current_user, error = get_current_user()  # From JWT
user_id = current_user.id  # Cannot be forged
```

---

## Visual: The Security Improvement

```
Part 5 (Vulnerable):
┌─────────┐        user_id=2 (forged!)       ┌─────────┐
│ User A  │ ────────────────────────────────>│ Backend │
│ (id=1)  │                                  │ TRUSTS  │
└─────────┘                                  └─────────┘
                                                  │
                                                  ▼
                                          Returns User B's data!

Part 6 (Secure):
┌─────────┐        JWT with user_id=1        ┌─────────┐
│ User A  │ ────────────────────────────────>│ Backend │
│ (id=1)  │                                  │ VALIDATES│
└─────────┘                                  └─────────┘
                                                  │
                                                  ▼
                                          Only returns User A's data
```

---

## Complete Protected Route Examples

### GET Todos (Protected)

```python
@app.route('/api/todos', methods=['GET'])
def get_todos():
    # Authenticate
    current_user, error = get_current_user()
    if error:
        return error

    # Get only this user's todos
    todos = Todo.query.filter_by(user_id=current_user.id).all()

    return jsonify({
        'todos': [{
            'id': t.id,
            'task_content': t.task_content,
            'is_completed': t.is_completed
        } for t in todos]
    })
```

### POST Create Todo (Protected)

```python
@app.route('/api/todos', methods=['POST'])
def create_todo():
    # Authenticate
    current_user, error = get_current_user()
    if error:
        return error

    # Validate request
    data = request.get_json()
    if not data or not data.get('task_content'):
        return jsonify({'error': 'task_content required'}), 400

    # Create todo for authenticated user
    todo = Todo(
        task_content=data['task_content'],
        is_completed=False,
        user_id=current_user.id  # From token, not request!
    )
    db.session.add(todo)
    db.session.commit()

    return jsonify({'message': 'Todo created!'}), 201
```

### DELETE Todo (Protected + Ownership)

```python
@app.route('/api/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    # Authenticate
    current_user, error = get_current_user()
    if error:
        return error

    # Find todo
    todo = Todo.query.get(todo_id)
    if not todo:
        return jsonify({'error': 'Todo not found'}), 404

    # Authorize - check ownership
    if todo.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    # Delete
    db.session.delete(todo)
    db.session.commit()

    return jsonify({'message': 'Todo deleted!'})
```

---

## Frontend: Sending the Authorization Header

The dashboard JavaScript now sends the token with every request:

```javascript
const token = localStorage.getItem('token');

// Helper function for authenticated requests
async function apiRequest(url, method = 'GET', body = null) {
    const options = {
        method,
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        }
    };

    if (body) {
        options.body = JSON.stringify(body);
    }

    const response = await fetch(url, options);

    // Handle expired/invalid token
    if (response.status === 401) {
        localStorage.clear();
        window.location.href = '/login';
        return null;
    }

    return await response.json();
}

// Usage
async function loadTodos() {
    const data = await apiRequest('/api/todos');
    // No user_id needed - backend knows who we are from token
}

async function createTodo(taskContent) {
    await apiRequest('/api/todos', 'POST', {
        task_content: taskContent
        // No user_id - backend gets it from token
    });
}
```

---

## Why Helper Function Instead of Decorator?

We use a helper function instead of a decorator for easier learning:

| Helper Function | Decorator |
|-----------------|-----------|
| You see exactly what happens step-by-step | Logic is hidden behind `@decorator` |
| No "magic" - explicit and clear | More concise, but harder to understand |
| Easy to debug with print statements | Debugging requires understanding decorators |
| Great for learning | Better for production code |

**In real projects**, decorators like `@token_required` are cleaner:

```python
# Production style (we don't use this for learning)
@app.route('/api/todos')
@token_required
def get_todos(current_user):
    # current_user is injected by decorator
    todos = Todo.query.filter_by(user_id=current_user.id).all()
```

But for learning, the explicit helper is more transparent.

---

## HTTP Response Codes Summary

| Code | Name | When Used |
|------|------|-----------|
| 200 | OK | Successful GET, PUT, DELETE |
| 201 | Created | Successful POST |
| 400 | Bad Request | Missing required fields |
| 401 | Unauthorized | No token, invalid token, expired token |
| 403 | Forbidden | Valid token, but accessing another user's data |
| 404 | Not Found | Todo doesn't exist |

---

## Try It Yourself

### Activity 1: Test Authentication
1. Log in and copy your token from localStorage (F12 → Application → Local Storage)
2. Use curl or Postman to make a request without the token
3. Observe the 401 response

### Activity 2: Test Authorization
1. Create two accounts (User A and User B)
2. Create a todo as User A
3. Try to delete User A's todo using User B's token
4. Observe the 403 response

### Activity 3: Inspect the Token
1. Copy your JWT token
2. Go to https://jwt.io
3. Paste your token to see what's inside
4. Note: The payload is NOT encrypted, only signed!

---

## Self-Study Questions

1. Why do we use the Authorization header instead of sending the token in the request body?
2. What would happen if we only checked authentication but not ownership?
3. Why is the JWT payload not encrypted? Is this a security problem?
4. What's the difference between authentication and authorization?
5. Why do we return 404 before checking ownership (not 403)?

---

## Security Best Practices Learned

1. **Never trust the frontend** - Always validate on the backend
2. **Extract user identity from tokens** - Not from request parameters
3. **Check ownership** - Users should only access their own data
4. **Use proper status codes** - 401 for auth, 403 for permission
5. **Validate tokens on every request** - HTTP is stateless

---

## Next Part

In **Part 7: Admin Panel**, we will:
- Add admin-only routes
- Create an admin check helper
- Build user management features
- Learn the difference between user-level and admin-level authorization
