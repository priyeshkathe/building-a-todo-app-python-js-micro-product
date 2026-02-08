# =============================================================================
# Part 3: User Registratioerrorn
# =============================================================================
# Now we add user registration.
# We will learn:
#   1. How to create a registration form
#   2. How to receive form data with POST request
#   3. How to save user to database
# =============================================================================

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
    if not email:
        print('email is missing')
        return jsonify({'error': 'Email is required'}), 400
    if not password:
        print('password is missing')
        return jsonify({'error': 'Password is required'}), 400

    # Check if user already exists
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered'}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already taken'}), 400

    # Create new user
    # NOTE: We're storing password directly here (NOT secure!)
    # We'll add proper password hashing in Part 4
    new_user = User(
        username=username,
        email=email,
        password_hash=password  # This will be fixed in Part 4
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'Registration successful!'}), 201


# =============================================================================
# RUN THE SERVER
# =============================================================================
if __name__ == '__main__':
    print("\n" + "="*50)
    print("  Part 3: User Registration")
    print("  Open: http://127.0.0.1:5000")
    print("="*50 + "\n")
    app.run(debug=True)


# ============================================
# SELF-STUDY QUESTIONS
# ============================================
# 1. What is the difference between GET and POST request?
# 2. What does request.get_json() return?
# 3. Why do we check if email already exists before creating user?
# 4. What does status code 201 mean? What about 400?
# 5. Why is storing plain password dangerous? (Check /users page to see!)
#
# ============================================
# ACTIVITIES - Try These!
# ============================================
# Activity 1: Add password validation
#   - Before creating user, check if password length < 6
#   - Return error if password is too short
#   - Hint: if len(password) < 6: return jsonify({'error': '...'}), 400
#
# Activity 2: Add username validation
#   - Check if username contains only letters and numbers
#   - Hint: use username.isalnum()
#
# Activity 3: See the security problem
#   - Register a new user with password "secret123"
#   - Go to /users page
#   - Notice how you can see the password! (This is bad!)
#   - We'll fix this in Part 4
#
# Activity 4: Add email format check
#   - Check if email contains '@' symbol
#   - Return error if email format is invalid
# ============================================
