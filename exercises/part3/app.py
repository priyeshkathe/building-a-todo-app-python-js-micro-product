# =============================================================================
# Part 3: User Registratioerrorn
# =============================================================================
# Now we add user registration.
# We will learn:
#   1. How to create a registration form
#   2. How to receive form data with POST request
#   3. How to save user to database
# =============================================================================

import email
from flask import Flask, render_template, request, jsonify
from models import db, User, init_db

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

init_db(app)


# =============================================================================
# PAGE ROUTES
# =============================================================================

@app.route('/')
def home():
    """Home page"""
    return render_template('index.html')


@app.route('/register')
def register_page():
    """Registration form page"""
    return render_template('register.html')


@app.route('/users')
def users_page():
    """View all registered users"""
    users = User.query.all()
    return render_template('users.html', users=users)


# =============================================================================
# API ROUTES
# =============================================================================

@app.route('/api/register', methods=['POST'])
def api_register():
    """
    Register a new user.

    Receives JSON: { "username": "...", "email": "...", "password": "..." }
    """
    data = request.get_json()
    print(data)

    # Validate input
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    username = data.get('username',None)
    print(username)
    email = data.get('email', None)
    print(email)
    password = data.get('password', None)
    print(password)

    if not username:
        print('username is missing')
        return jsonify({'error': 'Username is required'}), 400
    
    # Username format validation
    if not username.isalnum():
        return jsonify({'error': 'Username must contain only letters and numbers'}), 400

    if not email:
        print('email is missing')
        return jsonify({'error': 'Email is required'}), 400
    
    # Email format validation
    if '@' not in email:
        return jsonify({'error': 'Invalid email format'}), 400

    if not password:
        print('password is missing')
        return jsonify({'error': 'Password is required'}), 400
    
    # Password length validation
    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters long'}), 400


    # Check if user already exists
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered'}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already taken'}), 400

    # Create new user
    new_user = User(
        username=username,
        email=email,
        password_hash=password   
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'Registration successful!'}), 201


# RUN THE SERVER
if __name__ == '__main__':
    print("\n" + "="*50)
    print("  Part 3: User Registration")
    print("  Open: http://127.0.0.1:5000")
    print("="*50 + "\n")
    app.run(debug=True)





