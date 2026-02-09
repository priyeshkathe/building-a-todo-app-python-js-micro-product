# =============================================================================
# Part 5: Todo CRUD (Create, Read, Update, Delete)
# =============================================================================

from flask import Flask, render_template, request, jsonify
from models import db, User, Todo, init_db
from auth import hash_password, verify_password, create_token

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
# TODO CRUD API ROUTES
# =============================================================================

@app.route('/api/todos', methods=['GET'])  # READ operation
def get_todos():
    user_id = request.args.get('user_id')  # Get from URL: ?user_id=1 (NOT SECURE!)
    print('user_id:', user_id)
    if not user_id:
        return jsonify({'error': 'user_id required'}), 400

    todos = Todo.query.filter_by(user_id=user_id).all()  # Get all todos for user

    return jsonify({
        'todos': [{
            'id': t.id,
            'task_content': t.task_content,
            'is_completed': t.is_completed
        } for t in todos]  # List comprehension
    }), 200


@app.route('/api/todos', methods=['POST'])  # CREATE operation
def create_todo():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    task_content = data.get('task_content')
    user_id = data.get('user_id')

    if not task_content or not user_id:
        return jsonify({'error': 'task_content and user_id required'}), 400

    todo = Todo(
        task_content=task_content,
        is_completed=False,  # New todo = not completed
        user_id=user_id
    )
    db.session.add(todo)
    db.session.commit()  # ID is created after commit

    return jsonify({
        'message': 'Todo created!',
        'todo': {
            'id': todo.id,
            'task_content': todo.task_content,
            'is_completed': todo.is_completed
        }
    }), 201  # 201 = Created


@app.route('/api/todos/<int:todo_id>', methods=['PUT'])  # UPDATE operation
def update_todo(todo_id):  # todo_id comes from URL: /api/todos/5
    todo = Todo.query.get(todo_id)  # Find by ID
    print('modifying this todo:', todo)
    if not todo:
        return jsonify({'error': 'Todo not found'}), 404  # 404 = Not Found

    data = request.get_json()
    print()
    print(data)
    if 'task_content' in data:  # Only update if field is sent
        todo.task_content = data['task_content']
    if 'is_completed' in data:
        todo.is_completed = data['is_completed']

    db.session.commit()  # Save changes

    return jsonify({
        'message': 'Todo updated!',
        'todo': {
            'id': todo.id,
            'task_content': todo.task_content,
            'is_completed': todo.is_completed
        }
    }), 200


@app.route('/api/todos/<int:todo_id>', methods=['DELETE'])  # DELETE operation
def delete_todo(todo_id):
    todo = Todo.query.get(todo_id)
    if not todo:
        return jsonify({'error': 'Todo not found'}), 404

    db.session.delete(todo)  # Remove from database
    db.session.commit()

    return jsonify({'message': 'Todo deleted!'}), 200


# =============================================================================
# RUN THE SERVER
# =============================================================================
if __name__ == '__main__':
    print("\n" + "="*50)
    print("  Part 5: Todo CRUD")
    print("  Open: http://127.0.0.1:5000")
    print("="*50 + "\n")
    app.run(debug=True)
