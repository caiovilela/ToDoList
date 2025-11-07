from app.extensions import db
from datetime import datetime
from flask_login import UserMixin


class Client(db.Model):
    __tablename__ = 'client' 
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(50), nullable=True) 
    address = db.Column(db.String(200), nullable=True) 
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    tasks = db.relationship('Task', backref='client', lazy=True)

    def __repr__(self):
        return f'<Client {self.name}>'



class Task(db.Model):
    __tablename__ = 'todo' 
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=True)
    date = db.Column(db.DateTime, nullable=True) 
    status = db.Column(db.String(50), nullable=False, default='Agendado')
    done_comment = db.Column(db.String(300), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=True) 

    
    
    technician_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    

    

    def __repr__(self):
        return f'<Task {self.title}>'
 

class User(db.Model, UserMixin): 
    __tablename__ = 'user' 
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    
    
    name = db.Column(db.String(100), nullable=True) 
    role = db.Column(db.String(50), nullable=False, default='tecnico') 

    # Tarefas que este usuário (admin) criou
    tasks = db.relationship('Task', backref='author', lazy=True, foreign_keys='[Task.user_id]')
    
    #  Clientes que este usuário (admin) criou
    clients = db.relationship('Client', backref='owner', lazy=True)

    
    # Tarefas que foram ATRIBUÍDAS a este usuário (técnico)
    assigned_tasks = db.relationship('Task', backref='technician', lazy=True, foreign_keys='[Task.technician_id]')
    