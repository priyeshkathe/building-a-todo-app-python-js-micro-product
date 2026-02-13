# Part 7: Admin Panel

In this chapter, we add role-based access control to our application.

Up until now, all logged-in users had the same privileges. In this part, we introduce **admin users** who can view all users, see system statistics, and manage (delete) users — while regular users remain restricted to their own todos.

This chapter teaches the critical difference between **authentication** (who are you?) and **authorization** (what are you allowed to do?).

---

## What You Will Learn

By the end of this chapter, you will understand:

- How to add role-based access control with an `is_admin` flag
- The difference between authentication and authorization
- How to create admin-only routes with a `get_admin_user()` helper
- How to build an admin dashboard with system statistics
- How to implement user management (view all users, delete users)
- How to protect sensitive operations on both frontend and backend

---

## Why This Chapter Matters

Real-world applications have different types of users:

| Role | Can Do |
|------|--------|
| Guest | View public pages |
| User | Manage their own data |
| Admin | Manage all users and data |
| Super Admin | Configure the system |

Understanding role-based access is essential for:
- **SaaS applications** — Free vs Pro vs Enterprise users
- **Content platforms** — Readers vs Writers vs Editors
- **E-commerce** — Customers vs Sellers vs Support staff
- **Internal tools** — Employees vs Managers vs Admins

---

## Project Structure

```
part-7-admin-panel/
├── app.py              # Flask app with admin routes
├── models.py           # User model with is_admin + stats methods
├── auth.py             # Auth helpers (get_current_user, get_admin_user)
├── requirements.txt    # Python dependencies
├── templates/
│   ├── index.html      # Home page
│   ├── register.html   # Registration form
│   ├── login.html      # Login form
│   ├── dashboard.html  # User dashboard (with admin link)
│   └── admin.html      # Admin panel (NEW)
```

---

## How to Run

```bash
cd part-7-admin-panel
pip install -r requirements.txt
python app.py
```

Open in browser: http://127.0.0.1:5000

---

## Default Admin Credentials

When the app starts, it automatically creates a default admin user:

```
Email:    admin@example.com
Password: admin123
```

Login with these credentials to access the admin panel.

---

## Key Concepts

### 1. Authentication vs Authorization

These are two different security concepts:

| Concept | Question | Example |
|---------|----------|---------|
| **Authentication** | "Who are you?" | Login with email/password |
| **Authorization** | "What can you do?" | Admin can delete users, regular users cannot |

**Part 6** handled authentication (JWT tokens).
**Part 7** adds authorization (admin vs regular user).

```
User logs in (Authentication)
    ↓
System checks token (Still Authentication)
    ↓
User tries to access /api/admin/users
    ↓
System checks is_admin flag (Authorization)
    ↓
Allow or Deny (403 Forbidden)
```

---

### 2. The is_admin Flag

The User model now includes an admin flag:

```python
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)  # NEW!
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Method to include statistics for admin panel
    def to_dict_with_stats(self):
        total_todos = len(self.todos)
        completed_todos = len([t for t in self.todos if t.is_completed])
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'is_admin': self.is_admin,
            'created_at': self.created_at.isoformat(),
            'total_todos': total_todos,
            'completed_todos': completed_todos
        }
```

By default, new users have `is_admin=False`. Only manually created admin accounts (or the default admin) have `is_admin=True`.

---

### 3. Two Helper Functions in auth.py

**get_current_user()** — For regular protected routes:
```python
def get_current_user():
    """Validates JWT and returns logged-in user"""
    # Check Authorization header
    # Decode and validate token
    # Return user from database
    # Returns: (user, None) or (None, error_response)
```

**get_admin_user()** — For admin-only routes:
```python
def get_admin_user():
    """Validates JWT AND checks admin status"""
    # First, check if user is logged in
    current_user, error = get_current_user()
    if error:
        return None, error  # Not logged in → 401

    # Then, check if user is admin
    if not current_user.is_admin:
        return None, (jsonify({'error': 'Admin access required'}), 403)

    return current_user, None
```

The key difference:
- `get_current_user()` returns 401 if not logged in
- `get_admin_user()` returns 401 if not logged in, OR 403 if logged in but not admin

---

### 4. Admin Route Pattern

All admin routes follow this pattern:

```python
@app.route('/api/admin/users', methods=['GET'])
def get_all_users():
    # Step 1: Check admin status (includes login check)
    current_user, error = get_admin_user()
    if error:
        return error  # 401 or 403

    # Step 2: Perform admin operation
    users = User.query.all()
    return jsonify({
        'users': [user.to_dict_with_stats() for user in users]
    })
```

---

### 5. Admin API Endpoints

| Endpoint | Method | Description | Protection |
|----------|--------|-------------|------------|
| `/api/admin/users` | GET | List all users with stats | Admin only |
| `/api/admin/users/:id` | DELETE | Delete a user and their todos | Admin only |
| `/api/admin/stats` | GET | Get system statistics | Admin only |
| `/api/admin/todos` | GET | View all todos in system | Admin only |

---

### 6. User Management: Delete User

The delete user endpoint includes safety checks:

```python
@app.route('/api/admin/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    # Check admin status
    current_user, error = get_admin_user()
    if error:
        return error

    # Prevent self-deletion
    if user_id == current_user.id:
        return jsonify({'error': 'Cannot delete yourself'}), 400

    # Find user or return 404
    user = User.query.get_or_404(user_id)

    # Cascade delete: remove user's todos first
    Todo.query.filter_by(user_id=user_id).delete()

    # Delete the user
    db.session.delete(user)
    db.session.commit()

    return jsonify({'message': f'User {user.username} deleted successfully'})
```

**Safety features:**
- Admin cannot delete themselves
- All user's todos are deleted automatically (cascade)
- Returns 404 if user doesn't exist

---

### 7. System Statistics Endpoint

```python
@app.route('/api/admin/stats', methods=['GET'])
def get_stats():
    current_user, error = get_admin_user()
    if error:
        return error

    return jsonify({
        'total_users': User.query.count(),
        'total_todos': Todo.query.count(),
        'completed_todos': Todo.query.filter_by(is_completed=True).count(),
        'pending_todos': Todo.query.filter_by(is_completed=False).count()
    })
```

---

### 8. Frontend Protection

The admin page has both client-side and server-side protection:

**Client-side (admin.html):**
```javascript
const token = localStorage.getItem('token');
const user = JSON.parse(localStorage.getItem('user') || 'null');

// Redirect if not admin
if (!token || !user || !user.is_admin) {
    alert('Admin access required!');
    window.location.href = '/';
}
```

**Dashboard shows admin link only for admins:**
```javascript
// In dashboard.html
if (user.is_admin) {
    document.getElementById('admin-link').style.display = 'block';
}
```

**Server-side (always enforced):**
Even if someone bypasses the frontend check, the API will return 403:
```python
if not current_user.is_admin:
    return jsonify({'error': 'Admin access required'}), 403
```

---

## The Admin Panel UI

The admin panel displays:

### 1. Statistics Cards
Four colored cards showing system overview:
- **Total Users** (Blue)
- **Total Todos** (Light Blue)
- **Completed Todos** (Green)
- **Pending Todos** (Yellow)

### 2. Users Table
| Column | Description |
|--------|-------------|
| ID | User's database ID |
| Username | User's display name |
| Email | User's email address |
| Admin | Badge showing admin status |
| Todos | Completion ratio (e.g., "3/5") |
| Joined | Registration date |
| Actions | Delete button (not shown for self) |

### 3. All Todos Table
| Column | Description |
|--------|-------------|
| ID | Todo's database ID |
| User | Which user owns this todo |
| Task | The todo content |
| Status | Completed/Pending badge |
| Created | Creation date |

---

## HTTP Response Codes

| Code | Name | When Used |
|------|------|-----------|
| 200 | OK | Successful admin operation |
| 400 | Bad Request | Trying to delete yourself |
| 401 | Unauthorized | Not logged in |
| 403 | Forbidden | Logged in but not admin |
| 404 | Not Found | User/resource doesn't exist |

---

## Visual: Authorization Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    REQUEST TO ADMIN API                      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │ Has JWT Token?  │
                    └────────┬────────┘
                             │
              ┌──────────────┴──────────────┐
              │ NO                          │ YES
              ▼                             ▼
    ┌─────────────────┐           ┌─────────────────┐
    │ Return 401      │           │ Token Valid?    │
    │ "Token missing" │           └────────┬────────┘
    └─────────────────┘                    │
                               ┌───────────┴───────────┐
                               │ NO                    │ YES
                               ▼                       ▼
                     ┌─────────────────┐     ┌─────────────────┐
                     │ Return 401      │     │ User is Admin?  │
                     │ "Invalid token" │     └────────┬────────┘
                     └─────────────────┘              │
                                          ┌──────────┴──────────┐
                                          │ NO                  │ YES
                                          ▼                     ▼
                                ┌─────────────────┐   ┌─────────────────┐
                                │ Return 403      │   │ Allow Access    │
                                │ "Admin required"│   │ (Process request)│
                                └─────────────────┘   └─────────────────┘
```

---

## Comparison: User vs Admin Access

| Feature | Regular User | Admin |
|---------|--------------|-------|
| View own todos | Yes | Yes |
| Create todos | Yes | Yes |
| Delete own todos | Yes | Yes |
| View all users | No (403) | Yes |
| Delete users | No (403) | Yes |
| View all todos | No (403) | Yes |
| See statistics | No (403) | Yes |
| Access admin panel | Redirected | Yes |

---

## Frontend JavaScript (admin.html)

```javascript
// API wrapper with admin error handling
async function api(url, method = 'GET', body = null) {
    const options = {
        method,
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        }
    };
    if (body) options.body = JSON.stringify(body);

    const res = await fetch(url, options);

    // Handle authentication/authorization errors
    if (res.status === 401) {
        localStorage.clear();
        window.location.href = '/login';
        return null;
    }
    if (res.status === 403) {
        alert('Admin access required');
        window.location.href = '/';
        return null;
    }

    return await res.json();
}

// Load and display statistics
async function loadStats() {
    const data = await api('/api/admin/stats');
    if (!data) return;

    document.getElementById('total-users').textContent = data.total_users;
    document.getElementById('total-todos').textContent = data.total_todos;
    document.getElementById('completed-todos').textContent = data.completed_todos;
    document.getElementById('pending-todos').textContent = data.pending_todos;
}

// Delete user with confirmation
async function deleteUser(userId, username) {
    if (!confirm(`Are you sure you want to delete user "${username}"?\n\nThis will also delete all their todos.`)) {
        return;
    }

    await api(`/api/admin/users/${userId}`, 'DELETE');

    // Refresh all data
    loadStats();
    loadUsers();
    loadTodos();
}
```

---

## Try It Yourself

### Activity 1: Test Authorization
1. Register a new regular user
2. Try to access `/admin` directly
3. You should be redirected (frontend protection)
4. Try calling `/api/admin/users` with the regular user's token
5. You should get a 403 Forbidden response

### Activity 2: Admin Operations
1. Login as admin (admin@example.com / admin123)
2. Create some todos as admin
3. Register another user in a different browser/incognito
4. Create some todos as the new user
5. Go to admin panel and see both users' data

### Activity 3: Delete a User
1. As admin, delete a user from the admin panel
2. Observe that their todos are also deleted
3. Check the statistics — numbers should update

### Activity 4: Try to Delete Yourself
1. As admin, try to delete your own account
2. You should see "Cannot delete yourself" error
3. This is a safety feature!

---

## Self-Study Questions

1. Why do we check `is_admin` on the server instead of just hiding the admin link?
2. What's the difference between 401 and 403 status codes?
3. Why do we delete a user's todos before deleting the user?
4. How could you add different admin levels (e.g., super admin, moderator)?
5. Why is the admin panel styled differently (red navbar)?

---

## Security Best Practices Learned

1. **Always authorize on the server** — Frontend checks can be bypassed
2. **Use appropriate status codes** — 401 for auth, 403 for permission
3. **Prevent dangerous self-actions** — Admin can't delete themselves
4. **Cascade deletes carefully** — Don't leave orphaned data
5. **Separate admin routes** — Clear `/api/admin/*` namespace

---

## Creating New Admins

To create additional admin users, you can:

1. **Manually in database:**
   ```sql
   UPDATE users SET is_admin = 1 WHERE email = 'newadmin@example.com';
   ```

2. **Add an admin creation endpoint (advanced):**
   ```python
   @app.route('/api/admin/users/<int:user_id>/make-admin', methods=['POST'])
   def make_admin(user_id):
       current_user, error = get_admin_user()
       if error:
           return error
       user = User.query.get_or_404(user_id)
       user.is_admin = True
       db.session.commit()
       return jsonify({'message': f'{user.username} is now an admin'})
   ```

---

### 401 vs 403 Error Codes
```
401 Unauthorized = Not logged in (no token or invalid token)
403 Forbidden    = Logged in but not allowed (not admin)
```

## Next Part

**Part 8: Homework** is your practice assignment!

You will add a **priority feature** (Low, Medium, High) to todos, practicing:
- Database schema changes
- API modifications
- Frontend updates
- Full-stack development
