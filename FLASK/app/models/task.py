from app.extensions import db
from datetime import datetime
from flask_login import UserMixin

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=True)
    date = db.Column(db.DateTime, nullable=True)  
    done = db.Column(db.Boolean, default=False)
    done_comment = db.Column(db.String(300), nullable=True)
    user_email = db.Column(db.String(120), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


    def __repr__(self):
        return f'<Task {self.title}>'
    


class User(db.Model, UserMixin): 
    __tablename__ = 'user' 
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    
    
    tasks = db.relationship('Task', backref='author', lazy=True)