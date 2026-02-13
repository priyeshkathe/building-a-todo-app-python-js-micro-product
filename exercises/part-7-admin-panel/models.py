from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)  # NEW: Admin flag
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    todos = db.relationship('Todo', backref='user', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'is_admin': self.is_admin,
            'created_at': self.created_at.isoformat()
        }

    # NEW: For admin panel - include user statistics
    def to_dict_with_stats(self):
        total_todos = len(self.todos)
        completed_todos = len([t for t in self.todos if t.is_completed])
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'is_admin': self.is_admin,
            'created_at': self.created_at.isoformat(),
            'total_todos': total_todos,
            'completed_todos': completed_todos
        }


class Todo(db.Model):
    __tablename__ = 'todos'

    id = db.Column(db.Integer, primary_key=True)
    task_content = db.Column(db.String(200), nullable=False)
    is_completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'task_content': self.task_content,
            'is_completed': self.is_completed,
            'created_at': self.created_at.isoformat(),
            'user_id': self.user_id
        }
