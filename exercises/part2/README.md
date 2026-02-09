# Part 2: Database Setup

## What You Will Learn
- What is SQLAlchemy (database toolkit)
- How to create database models (tables)
- How to query the database

## Files in This Part
```
part-2-database-setup/
├── app.py              # Flask app with database
├── models.py           # Database models (User, Todo)
├── requirements.txt    # Python dependencies
├── templates/
│   ├── index.html      # Home page
│   └── test_db.html    # Database test page
```

## How to Run
```bash
cd part-2-database-setup
pip install -r requirements.txt
python app.py
```
Open: http://127.0.0.1:5000/test-db

## Key Concepts

### 1. Database Configuration
```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
```

### 2. Creating a Model
```python
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True)
```

### 3. Database Operations
```python
# Create
user = User(username='john', email='john@example.com')
db.session.add(user)
db.session.commit()

# Read
users = User.query.all()
user = User.query.filter_by(username='john').first()

# Delete
db.session.delete(user)
db.session.commit()
```

## Next Part
In Part 3, we will add user registration with forms.
