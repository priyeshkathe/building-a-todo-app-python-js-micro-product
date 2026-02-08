from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    todos = db.relationship('Todo', backref='user', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat()
        }


class Todo(db.Model):
    __tablename__ = 'todos'

    id = db.Column(db.Integer, primary_key=True)
    task_content = db.Column(db.String(200), nullable=False)
    is_completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # ===========================================
    # STEP 1: Add this line below
    # ===========================================
    # priority = db.Column(db.String(10), default='medium')
    # ===========================================

    def to_dict(self):
        return {
            'id': self.id,
            'task_content': self.task_content,
            'is_completed': self.is_completed,
            'created_at': self.created_at.isoformat(),
            'user_id': self.user_id,
            # ===========================================
            # STEP 2: Add this line below
            # ===========================================
            # 'priority': self.priority
            # ===========================================
        }
