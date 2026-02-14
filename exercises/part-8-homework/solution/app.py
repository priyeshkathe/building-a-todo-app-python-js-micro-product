# SOLUTION - app.py (completed)

from flask import Flask, request, jsonify, render_template
from models import db, User, Todo
from auth import hash_password, verify_password, create_token, token_required

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()


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
        password_hash=hash_password(data['password'])
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
            'email': user.email
        }
    })


# ============================================
# TODO API (Protected)
# ============================================

@app.route('/api/todos', methods=['GET'])
@token_required
def get_todos(current_user):
    todos = Todo.query.filter_by(user_id=current_user.id).all()
    return jsonify({'todos': [todo.to_dict() for todo in todos]})


@app.route('/api/todos', methods=['POST'])
@token_required
def create_todo(current_user):
    data = request.get_json()

    todo = Todo(
        task_content=data['task_content'],
        user_id=current_user.id,
        # STEP 3: Added priority
        priority=data.get('priority', 'medium')
    )

    db.session.add(todo)
    db.session.commit()

    return jsonify(todo.to_dict()), 201


@app.route('/api/todos/<int:todo_id>', methods=['PUT'])
@token_required
def update_todo(current_user, todo_id):
    todo = Todo.query.get_or_404(todo_id)

    if todo.user_id != current_user.id:
        return jsonify({'error': 'Not authorized'}), 403

    data = request.get_json()
    if 'task_content' in data:
        todo.task_content = data['task_content']
    if 'is_completed' in data:
        todo.is_completed = data['is_completed']

    db.session.commit()
    return jsonify(todo.to_dict())


@app.route('/api/todos/<int:todo_id>', methods=['DELETE'])
@token_required
def delete_todo(current_user, todo_id):
    todo = Todo.query.get_or_404(todo_id)

    if todo.user_id != current_user.id:
        return jsonify({'error': 'Not authorized'}), 403

    db.session.delete(todo)
    db.session.commit()

    return jsonify({'message': 'Todo deleted'})


if __name__ == '__main__':
    print("\n" + "="*50)
    print("  Part 8: SOLUTION")
    print("  Open: http://127.0.0.1:5000")
    print("="*50 + "\n")
    app.run(debug=True)
