# =============================================================================
# Part 6: Protected Routes
# =============================================================================

from flask import Flask, render_template, request, jsonify
from models import db, User, Todo, init_db
from auth import hash_password, verify_password, create_token, get_current_user

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

init_db(app)


# =============================================================================
# PAGE ROUTES
# =============================================================================

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


# =============================================================================
# AUTH API ROUTES
# =============================================================================

@app.route('/api/register', methods=['POST'])
def api_register():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({'error': 'All fields required'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered'}), 400

    new_user = User(
        username=username,
        email=email,
        password_hash=hash_password(password)
    )
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'Registration successful!'}), 201


@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()
    if not user or not verify_password(user.password_hash, password):
        return jsonify({'error': 'Invalid credentials'}), 401

    token = create_token(user.id, user.is_admin)

    return jsonify({
        'token': token,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'is_admin': user.is_admin
        }
    }), 200


# =============================================================================
# PROTECTED TODO API ROUTES
# =============================================================================
# NOTE: In real projects, this repeated token check would use a @decorator.
# We write it explicitly here for learning purposes.

@app.route('/api/todos', methods=['GET'])
def get_todos():
    # Step 1: Check if user is logged in (validate token)
    current_user, error = get_current_user()
    if error:
        return error  # Returns 401 if token is missing/invalid

    # Step 2: Get only this user's todos
    todos = Todo.query.filter_by(user_id=current_user.id).all()

    return jsonify({
        'todos': [{
            'id': t.id,
            'task_content': t.task_content,
            'is_completed': t.is_completed
        } for t in todos]
    }), 200


@app.route('/api/todos', methods=['POST'])
def create_todo():
    # Step 1: Check if user is logged in
    current_user, error = get_current_user()
    if error:
        return error

    # Step 2: Validate request data
    data = request.get_json()
    if not data or not data.get('task_content'):
        return jsonify({'error': 'task_content required'}), 400

    # Step 3: Create todo for this user
    todo = Todo(
        task_content=data['task_content'],
        is_completed=False,
        user_id=current_user.id  # User ID from token (secure!)
    )
    db.session.add(todo)
    db.session.commit()

    return jsonify({
        'message': 'Todo created!',
        'todo': {
            'id': todo.id,
            'task_content': todo.task_content,
            'is_completed': todo.is_completed
        }
    }), 201


@app.route('/api/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    # Step 1: Check if user is logged in
    current_user, error = get_current_user()
    if error:
        return error

    # Step 2: Find the todo
    todo = Todo.query.get(todo_id)
    if not todo:
        return jsonify({'error': 'Todo not found'}), 404

    # Step 3: Check ownership - is this the user's todo?
    if todo.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403  # 403 = Forbidden

    # Step 4: Update the todo
    data = request.get_json()
    if 'task_content' in data:
        todo.task_content = data['task_content']
    if 'is_completed' in data:
        todo.is_completed = data['is_completed']

    db.session.commit()

    return jsonify({
        'message': 'Todo updated!',
        'todo': {
            'id': todo.id,
            'task_content': todo.task_content,
            'is_completed': todo.is_completed
        }
    }), 200


@app.route('/api/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    # Step 1: Check if user is logged in
    current_user, error = get_current_user()
    if error:
        return error

    # Step 2: Find the todo
    todo = Todo.query.get(todo_id)
    if not todo:
        return jsonify({'error': 'Todo not found'}), 404

    # Step 3: Check ownership
    if todo.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    # Step 4: Delete the todo
    db.session.delete(todo)
    db.session.commit()

    return jsonify({'message': 'Todo deleted!'}), 200


# =============================================================================
# RUN THE SERVER
# =============================================================================
if __name__ == '__main__':
    print("\n" + "="*50)
    print("  Part 6: Protected Routes")
    print("  Open: http://127.0.0.1:5000")
    print("="*50 + "\n")
    app.run(debug=True)
