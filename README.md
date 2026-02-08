# Todo App - Learn Flask Step by Step

A complete Todo application built in 8 parts to learn Flask, databases, authentication, and more.

---

## Project Structure (8 Parts)

```
todo-app/
├── part-1-hello-flask/        # Flask basics
├── part-2-database-setup/     # SQLAlchemy database
├── part-3-user-registration/  # Registration form
├── part-4-user-login/         # Login with JWT
├── part-5-todo-crud/          # CRUD operations
├── part-6-protected-routes/   # Authentication decorator
├── part-7-admin-panel/        # Admin features
└── part-8-homework/           # Practice assignment
```

---

## Learning Path

| Part | Topic | What You Learn |
|------|-------|----------------|
| 1 | Hello Flask | Routes, templates, render_template() |
| 2 | Database Setup | SQLAlchemy, models, queries |
| 3 | User Registration | POST requests, JSON, form validation |
| 4 | User Login | Password hashing, JWT tokens |
| 5 | Todo CRUD | Create, Read, Update, Delete |
| 6 | Protected Routes | @token_required decorator |
| 7 | Admin Panel | @admin_required, user management |
| 8 | Homework | Add priority feature yourself |

---

## How to Run Any Part

```bash
# Go to the part you want to run
cd part-1-hello-flask

# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py
```

Open: http://127.0.0.1:5000

---

## Admin Login (Part 7)

When you run Part 7, default admin is created:
```
Email:    admin@example.com
Password: admin123
```

---

## Technology Stack

| Component | Technology |
|-----------|------------|
| Backend | Flask 3.0 |
| Database | SQLite + SQLAlchemy |
| Auth | JWT (PyJWT) |
| Password | Werkzeug |
| Frontend | Bootstrap 5 |

---

## Database Tables

**User**
| Field | Type |
|-------|------|
| id | Integer (Primary Key) |
| username | String (Unique) |
| email | String (Unique) |
| password_hash | String |
| is_admin | Boolean |

**Todo**
| Field | Type |
|-------|------|
| id | Integer (Primary Key) |
| task_content | String |
| is_completed | Boolean |
| user_id | Foreign Key → User |

---

## API Endpoints

### Auth
| Method | URL | Description |
|--------|-----|-------------|
| POST | /api/register | Create account |
| POST | /api/login | Login |

### Todos (Protected)
| Method | URL | Description |
|--------|-----|-------------|
| GET | /api/todos | Get todos |
| POST | /api/todos | Create todo |
| PUT | /api/todos/:id | Update todo |
| DELETE | /api/todos/:id | Delete todo |

### Admin (Part 7)
| Method | URL | Description |
|--------|-----|-------------|
| GET | /api/admin/users | Get all users |
| DELETE | /api/admin/users/:id | Delete user |
| GET | /api/admin/stats | Get statistics |

---

## Self-Study

Each `app.py` file contains:
- **Self-Study Questions** - Test your understanding
- **Activities** - Hands-on exercises to try

Look at the bottom of each `app.py` file!

---

## Tips for Students

1. **Follow the order** - Part 1 → Part 2 → ... → Part 8
2. **Read the code** - Don't just copy, understand it
3. **Try activities** - Practice makes perfect
4. **Break things** - Change code and see what happens
5. **Use browser console** - F12 to see errors and test APIs

---

Happy Learning!
