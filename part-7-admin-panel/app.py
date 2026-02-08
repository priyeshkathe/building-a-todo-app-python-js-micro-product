# =============================================================================
# Part 7: Admin Panel
# =============================================================================

from flask import Flask, request, jsonify, render_template
from models import db, User, Todo
from auth import hash_password, verify_password, create_token, get_current_user, get_admin_user

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo_part7.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

    admin = User.query.filter_by(email='admin@example.com').first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@example.com',
            password_hash=hash_password('admin123'),
            is_admin=True  # This makes user an admin
        )
        db.session.add(admin)
        db.session.commit()
        print('\n' + '='*50)
        print('DEFAULT ADMIN USER CREATED:')
        print('Email:    admin@example.com')
        print('Password: admin123')
        print('='*50 + '\n')
    else:
        print('\n' + '='*50)
        print('ADMIN LOGIN:')
        print('Email:    admin@example.com')
        print('Password: admin123')
        print('='*50 + '\n')


# ============================================
# PAGE ROUTES
# ============================================

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register')
def register_page():
    return render_template('register.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/dashboard')
def dashboard_page():
    return render_template('dashboard.html')

@app.route('/admin')
def admin_page():
    return render_template('admin.html')


# ============================================
# AUTH API
# ============================================

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()

    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 400

    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already taken'}), 400

    user = User(
        username=data['username'],
        email=data['email'],
        password_hash=hash_password(data['password'])  # is_admin defaults to False
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({'message': 'Registration successful'}), 201


@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()

    user = User.query.filter_by(email=data['email']).first()

    if not user or not verify_password(data['password'], user.password_hash):
        return jsonify({'error': 'Invalid email or password'}), 401

    token = create_token(user.id)

    return jsonify({
        'message': 'Login successful',
        'token': token,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'is_admin': user.is_admin  # Frontend shows admin link if True
        }
    })


# ============================================
# TODO API (Protected - any logged in user)
# ============================================
# NOTE: In real projects, this repeated check would use a @decorator.
# We write it explicitly here for learning purposes.

@app.route('/api/todos', methods=['GET'])
def get_todos():
    # Step 1: Check if user is logged in
    current_user, error = get_current_user()
    if error:
        return error

    # Step 2: Get user's todos
    todos = Todo.query.filter_by(user_id=current_user.id).all()
    return jsonify({'todos': [todo.to_dict() for todo in todos]})


@app.route('/api/todos', methods=['POST'])
def create_todo():
    # Step 1: Check if user is logged in
    current_user, error = get_current_user()
    if error:
        return error

    # Step 2: Create todo
    data = request.get_json()
    todo = Todo(
        task_content=data['task_content'],
        user_id=current_user.id
    )

    db.session.add(todo)
    db.session.commit()

    return jsonify(todo.to_dict()), 201


@app.route('/api/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    # Step 1: Check if user is logged in
    current_user, error = get_current_user()
    if error:
        return error

    # Step 2: Find todo
    todo = Todo.query.get_or_404(todo_id)

    # Step 3: Check ownership
    if todo.user_id != current_user.id:
        return jsonify({'error': 'Not authorized'}), 403

    # Step 4: Update todo
    data = request.get_json()
    if 'task_content' in data:
        todo.task_content = data['task_content']
    if 'is_completed' in data:
        todo.is_completed = data['is_completed']

    db.session.commit()
    return jsonify(todo.to_dict())


@app.route('/api/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    # Step 1: Check if user is logged in
    current_user, error = get_current_user()
    if error:
        return error

    # Step 2: Find todo
    todo = Todo.query.get_or_404(todo_id)

    # Step 3: Check ownership
    if todo.user_id != current_user.id:
        return jsonify({'error': 'Not authorized'}), 403

    # Step 4: Delete todo
    db.session.delete(todo)
    db.session.commit()

    return jsonify({'message': 'Todo deleted'})


# ============================================
# ADMIN API (Only users with is_admin=True)
# ============================================
# These routes check: 1) Is user logged in? 2) Is user an admin?

@app.route('/api/admin/users', methods=['GET'])
def get_all_users():
    # Step 1: Check if user is logged in AND is admin
    current_user, error = get_admin_user()
    if error:
        return error  # Returns 401 if not logged in, 403 if not admin

    # Step 2: Get all users
    users = User.query.all()
    return jsonify({'users': [user.to_dict_with_stats() for user in users]})


@app.route('/api/admin/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    # Step 1: Check if user is admin
    current_user, error = get_admin_user()
    if error:
        return error

    # Step 2: Can't delete yourself
    if user_id == current_user.id:
        return jsonify({'error': 'Cannot delete yourself'}), 400

    # Step 3: Find and delete user
    user = User.query.get_or_404(user_id)
    Todo.query.filter_by(user_id=user_id).delete()  # Delete user's todos first
    db.session.delete(user)
    db.session.commit()

    return jsonify({'message': f'User {user.username} deleted'})


@app.route('/api/admin/stats', methods=['GET'])
def get_stats():
    # Step 1: Check if user is admin
    current_user, error = get_admin_user()
    if error:
        return error

    # Step 2: Calculate stats
    total_users = User.query.count()
    total_todos = Todo.query.count()
    completed_todos = Todo.query.filter_by(is_completed=True).count()

    return jsonify({
        'total_users': total_users,
        'total_todos': total_todos,
        'completed_todos': completed_todos,
        'pending_todos': total_todos - completed_todos
    })


@app.route('/api/admin/todos', methods=['GET'])
def get_all_todos():
    # Step 1: Check if user is admin
    current_user, error = get_admin_user()
    if error:
        return error

    # Step 2: Get ALL todos (not just admin's)
    todos = Todo.query.all()
    result = []
    for todo in todos:
        todo_data = todo.to_dict()
        todo_data['username'] = todo.user.username  # Add owner's username
        result.append(todo_data)
    return jsonify({'todos': result})


if __name__ == '__main__':
    app.run(debug=True)
