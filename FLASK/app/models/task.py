from app import db
from datetime import datetime

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=True)
    date = db.Column(db.DateTime, nullable=True)  
    done = db.Column(db.Boolean, default=False)
    done_comment = db.Column(db.String(300), nullable=True)

    def __repr__(self):
        return f'<Task {self.title}>'
