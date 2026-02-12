# =============================================================================
# Part 2: Database Setup
# =============================================================================
# Now we add a database to store data permanently.
# We will learn:
#   1. What is SQLAlchemy (database toolkit)
#   2. How to create database models (tables)
#   3. How to query the database
# =============================================================================

from flask import Flask, render_template
from models import db, User, Todo, init_db

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'connect_args': {'timeout': 10},  # 10 second timeout for database locks
    'pool_pre_ping': True,  # Test connections before using them
}

# Initialize the database
init_db(app)

# ROUTES

@app.route('/')
def home():
    """Home page"""
    return render_template('index.html')


@app.route('/test-db')
def test_db():
    """
    Test route to verify database is working.
    ACTIVITY 4: Creates 3 users with multiple todos each.
    """
    try:
        # ACTIVITY 4: Create 3 Users with Different Todos
        users_data = [
            {
                'username': 'testuser',
                'email': 'test@example.com',
                'phone': '+1-234-567-8900',
                'todos': ['Learn SQLAlchemy', 'Build a Todo App']
            },
            {
                'username': 'john',
                'email': 'john@example.com',
                'phone': '+1-555-1111',
                'todos': ['Study Python', 'Learn Flask', 'Practice Databases']
            },
            {
                'username': 'priyesh',
                'email': 'priyesh@example.com',
                'phone': '+1-555-2222',
                'todos': ['Plan Project', 'Write Tests', 'Deploy App']
            }
        ]
        
        # Create all users and todos in ONE transaction
        for user_data in users_data:
            # Check if user exists
            user = User.query.filter_by(username=user_data['username']).first()
            
            if not user:
                # Create user
                user = User(
                    username=user_data['username'],
                    email=user_data['email'],
                    password_hash='temporary',
                    phone=user_data['phone']
                )
                db.session.add(user)
                db.session.flush()  # Get the ID without committing
                
                # Create todos for this user
                for todo_content in user_data['todos']:
                    todo = Todo(
                        task_content=todo_content,
                        user_id=user.id
                    )
                    db.session.add(todo)
        
        # Commit ONCE after adding everything
        db.session.commit()
        
    except Exception as e:
        db.session.rollback()  # Rollback on error
        print(f"Error creating test data: {e}")
   
    # Get all users and todos for display
    all_users = User.query.all()
    all_todos = Todo.query.all()
    
    # Query 1: User.query.all() - Gets ALL users from database
    query_all_users = User.query.all()
    
    # Query 2: User.query.first() - Gets FIRST user from database
    first_user = User.query.first()
    
    # Query 3: User.query.count() - Counts total number of users
    total_users = User.query.count()

    return render_template('test_db.html', 
                         users=all_users, 
                         todos=all_todos,
                         query_all_users=query_all_users,
                         first_user=first_user,
                         total_users=total_users)

# RUN THE SERVER

if __name__ == '__main__':
    print("\n" + "="*50)
    print("  Part 2: Database Setup")
    print("  Open: http://127.0.0.1:5000")
    print("  Test DB: http://127.0.0.1:5000/test-db")
    print("="*50 + "\n")
    app.run(debug=True)
