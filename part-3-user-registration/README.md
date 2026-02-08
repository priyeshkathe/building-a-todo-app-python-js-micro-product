# Part 3: User Registration

In this chapter, we build our first real user interaction feature.

Up until now, our app could only display static pages. In this part, users can finally **do something** — register an account that gets saved to the database.

However, this chapter **intentionally** stores passwords insecurely to demonstrate why password hashing is critical. We fix this in Part 4.

---

## What You Will Learn

By the end of this chapter, you will understand:

- How HTML forms send data to the backend
- How POST requests differ from GET requests
- How to receive and parse JSON data in Flask
- How to validate user input on the server
- How to save data to a database
- Why storing plain text passwords is dangerous

---

## Why This Chapter Matters

Registration is the gateway to any user-based application:

- Users need accounts to have personalized experiences
- Understanding form submission is fundamental to web development
- Server-side validation protects your database from bad data
- This chapter reveals a common security mistake (plain text passwords)

---

## Project Structure

```
part-3-user-registration/
├── app.py              # Flask app with registration endpoint
├── models.py           # Database models (User, Todo)
├── requirements.txt    # Python dependencies
├── templates/
│   ├── index.html      # Home page
│   ├── register.html   # Registration form
│   └── users.html      # Display all users (shows security flaw)
```

---

## How to Run

```bash
cd part-3-user-registration
pip install -r requirements.txt
python app.py
```

Open in browser: http://127.0.0.1:5000/register

---

## Key Concepts

### 1. GET vs POST Requests

| GET | POST |
|-----|------|
| Retrieves data | Sends data |
| Parameters in URL | Data in request body |
| Cached by browser | Not cached |
| Bookmarkable | Not bookmarkable |
| Used for reading | Used for creating |

**Example:**
```
GET  /users           → "Give me the list of users"
POST /api/register    → "Create a new user with this data"
```

---

### 2. HTML Form Structure

```html
<form id="register-form">
    <input type="text" id="username" placeholder="Username" required>
    <input type="email" id="email" placeholder="Email" required>
    <input type="password" id="password" placeholder="Password" required>
    <button type="submit">Register</button>
</form>
```

Key attributes:
- `type="email"` — Browser validates email format
- `type="password"` — Hides characters as dots
- `required` — Browser prevents empty submission

---

### 3. JavaScript Form Submission

Instead of traditional form submission, we use JavaScript to send data as JSON:

```javascript
document.getElementById('register-form').addEventListener('submit', async function(e) {
    e.preventDefault();  // Stop default form submission

    // Get form values
    const username = document.getElementById('username').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    // Send POST request with JSON
    const response = await fetch('/api/register', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            username: username,
            email: email,
            password: password
        })
    });

    const data = await response.json();

    if (response.ok) {
        showAlert('Registration successful!', 'success');
        document.getElementById('register-form').reset();
    } else {
        showAlert(data.error, 'danger');
    }
});
```

**Why use JavaScript instead of regular form submission?**
- We can handle the response without page reload
- We can show success/error messages dynamically
- We send JSON (standard for APIs) instead of form-encoded data

---

### 4. Flask Registration Endpoint

```python
@app.route('/api/register', methods=['POST'])
def api_register():
    # Step 1: Get JSON data from request
    data = request.get_json()

    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    # Step 2: Validate required fields
    if not username or not email or not password:
        return jsonify({'error': 'All fields are required'}), 400

    # Step 3: Check for duplicates
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered'}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already taken'}), 400

    # Step 4: Create and save user
    new_user = User(
        username=username,
        email=email,
        password_hash=password  # WARNING: Plain text! Fixed in Part 4
    )
    db.session.add(new_user)
    db.session.commit()

    # Step 5: Return success response
    return jsonify({
        'message': 'Registration successful!',
        'user': {
            'id': new_user.id,
            'username': new_user.username,
            'email': new_user.email
        }
    }), 201
```

---

### 5. Understanding request.get_json()

```python
data = request.get_json()
```

This parses the JSON body sent from the frontend:

```
Frontend sends:
{
    "username": "john",
    "email": "john@example.com",
    "password": "secret123"
}

Backend receives:
data = {
    'username': 'john',
    'email': 'john@example.com',
    'password': 'secret123'
}
```

---

### 6. Server-Side Validation

**Why validate on the server?**
- Frontend validation can be bypassed (using DevTools or API tools)
- The server is the last line of defense
- Database constraints alone give poor error messages

```python
# Check required fields
if not username or not email or not password:
    return jsonify({'error': 'All fields are required'}), 400

# Check uniqueness
if User.query.filter_by(email=email).first():
    return jsonify({'error': 'Email already registered'}), 400
```

---

### 7. HTTP Response Codes

| Code | Name | When to Use |
|------|------|-------------|
| 200 | OK | Successful request |
| 201 | Created | Successfully created a resource |
| 400 | Bad Request | Invalid data or validation failed |
| 500 | Internal Server Error | Something went wrong on the server |

```python
# Success - resource created
return jsonify({'message': 'Success!'}), 201

# Error - bad input
return jsonify({'error': 'Email already exists'}), 400
```

---

### 8. Database Model

```python
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    # Relationship to todos
    todos = db.relationship('Todo', backref='user', lazy=True)
```

Key constraints:
- `unique=True` — No duplicate usernames or emails
- `nullable=False` — Field is required

---

## Security Warning: Plain Text Passwords

This chapter **intentionally** stores passwords in plain text to demonstrate the problem.

### See the Problem Yourself

1. Register a new account at `/register`
2. Go to `/users` page
3. You can see everyone's passwords!

```
┌─────┬──────────┬─────────────────────┬────────────┐
│ ID  │ Username │ Email               │ Password   │
├─────┼──────────┼─────────────────────┼────────────┤
│ 1   │ alice    │ alice@example.com   │ secret123  │  ← Visible!
│ 2   │ bob      │ bob@example.com     │ password   │  ← Visible!
└─────┴──────────┴─────────────────────┴────────────┘
```

### Why This is Dangerous

1. **Database breaches** — If hackers access your database, they get all passwords
2. **Insider threats** — Developers and admins can see user passwords
3. **Password reuse** — Users often use the same password everywhere
4. **Legal liability** — Storing plain text passwords may violate regulations

### The Solution (Part 4)

In Part 4, we will:
- Hash passwords before storing
- Never store the actual password
- Verify passwords by comparing hashes

```
Part 3 (INSECURE):
User enters: "secret123"
Database stores: "secret123"  ← Anyone can read this!

Part 4 (SECURE):
User enters: "secret123"
Database stores: "pbkdf2:sha256:260000$abc..."  ← Cannot reverse this!
```

---

## The Complete Flow

```
┌─────────────────┐
│   User fills    │
│   form and      │
│   clicks Submit │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   JavaScript    │
│   intercepts    │
│   form submit   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  fetch() sends  │
│  POST request   │
│  with JSON body │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Flask route   │
│   receives and  │
│   validates     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Database      │
│   stores new    │
│   user record   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   JSON response │
│   sent back to  │
│   JavaScript    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   UI shows      │
│   success or    │
│   error message │
└─────────────────┘
```

---

## Try It Yourself

### Activity 1: Test Validation
1. Try registering with an empty username
2. Try registering with an invalid email
3. Try registering with the same email twice
4. Observe the error messages

### Activity 2: Inspect the Request
1. Open DevTools (F12) → Network tab
2. Register a new user
3. Click on the request to `/api/register`
4. Look at the Request Payload — you'll see the JSON you sent
5. Look at the Response — you'll see the JSON returned

### Activity 3: See the Security Flaw
1. Register a few accounts with different passwords
2. Visit `/users`
3. Notice how all passwords are visible
4. Think: What would happen if this was a real application?

---

## Self-Study Questions

1. What's the difference between `request.form` and `request.get_json()`?
2. Why do we use `e.preventDefault()` in the form submit handler?
3. What happens if you try to insert a duplicate email?
4. Why is 201 used instead of 200 for successful registration?
5. Why is server-side validation important even if we validate on the frontend?

---

## Common Errors

### "Email already registered"
- The email is already in the database
- Use a different email or check `/users`

### "Missing required fields"
- One of the fields is empty
- Check all inputs have values

### "Method Not Allowed" (405)
- You're using GET instead of POST
- Make sure you're submitting the form, not visiting the URL directly

---

## Next Part

In **Part 4: User Login**, we will:
- Fix the password security issue with hashing
- Add a login form
- Create JWT tokens for authentication
- Introduce localStorage for session management
