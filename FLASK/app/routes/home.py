from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import datetime
from flask_login import login_user, login_required, logout_user, current_user
from flask import current_app 

home_bp = Blueprint('home', __name__)


def get_db():
   
    return current_app.extensions['sqlalchemy']



@home_bp.route('/')
@login_required 
def homepage():
    from app.models.task import Task 
    db_instance = get_db()
    
    
    stmt = db_instance.select(Task).filter_by(user_id=current_user.id)
    task = db_instance.session.scalars(stmt).all() 
    
    return render_template('home.html', task=task)


@home_bp.route('/tasks')
@login_required 
def list_tasks():
    from app.models.task import Task
    db_instance = get_db()
    
    
    stmt = db_instance.select(Task).filter_by(user_id=current_user.id, done=False)
    tasks = db_instance.session.scalars(stmt).all() 
    
    return render_template('tasks.html', tasks=tasks) 


@home_bp.route('/add', methods=['POST'])
@login_required 
def add_task():
    from app.models.task import Task
    db_instance = get_db()
    
    
    title = request.form.get('title')
    description = request.form.get('description')
    date_str = request.form.get('date')
    user_email = request.form.get('user_email')
    
    if date_str: 
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d') 
        except ValueError:
            date = datetime.utcnow()
    else:
        date = datetime.utcnow()

    new_task = Task(title=title, 
                    description=description, 
                    date=date,
                    user_email=user_email,
                    user_id=current_user.id) 
    
    db_instance.session.add(new_task) 
    db_instance.session.commit()

    return redirect(url_for('home.homepage'))

@home_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required 
def edit_task(id):
    from app.models.task import Task
    db_instance = get_db()
    
    
    stmt = db_instance.select(Task).filter_by(id=id, user_id=current_user.id)
    task = db_instance.session.scalar(stmt)

    if not task:
        return "Tarefa não encontrada ou acesso não autorizado", 403 

    if request.method == 'POST':
        
        task.title = request.form.get('title')
        task.description = request.form.get('description')
        date_str = request.form.get('date')
        
        if date_str:
            try:
                task.date = datetime.strptime(date_str, '%Y-%m-%d')
            except ValueError:
                task.date = None 
        else:
            task.date = None

        db_instance.session.commit()
        return redirect(url_for('home.homepage'))

    return render_template('edit.html', task=task)

@home_bp.route('/delete/<int:id>', methods=['GET'])
@login_required 
def delete_task(id):
    from app.models.task import Task
    db_instance = get_db()
    
    
    stmt = db_instance.select(Task).filter_by(id=id, user_id=current_user.id)
    task = db_instance.session.scalar(stmt)
    
    if not task:
        return "Tarefa não encontrada ou acesso não autorizado", 403
        
    db_instance.session.delete(task)
    db_instance.session.commit()
    
    return redirect(url_for('home.list_tasks'))



@home_bp.route('/done/<int:id>', methods=['GET', 'POST'])
@login_required 
def mark_task_done(id):
    from app.models.task import Task
    db_instance = get_db()
    
    
    stmt = db_instance.select(Task).filter_by(id=id, user_id=current_user.id)
    task = db_instance.session.scalar(stmt) 

    if not task:
        return "Tarefa não encontrada ou acesso não autorizado", 403 

    if request.method == 'POST':
        task.done = True
        task.done_comment = request.form.get('done_comment') 
        db_instance.session.commit()
        return redirect(url_for('home.list_tasks'))

    return render_template('done.html', task=task)

@home_bp.route('/tasks/done')
@login_required 
def list_done_tasks():
    from app.models.task import Task
    db_instance = get_db()
    
    
    stmt = db_instance.select(Task).filter_by(user_id=current_user.id, done=True)
    done_tasks = db_instance.session.scalars(stmt).all()
    
    return render_template('done_tasks.html', tasks=done_tasks)

@home_bp.route('/calendar')
@login_required 
def calendar():
    from app.models.task import Task
    db_instance = get_db()
    
    
    stmt = db_instance.select(Task).filter_by(user_id=current_user.id, done=False).filter(Task.date.isnot(None))
    tasks = db_instance.session.scalars(stmt).all()
    
    events = [
        {
            "title": task.title,
            "start": task.date.strftime('%Y-%m-%d') if task.date else None,
            "description": task.description
        }
        for task in tasks 
    ]
    return render_template('calendar.html', events=events)




@home_bp.route('/register', methods=['GET', 'POST'])
def register():
    from app.models.task import User 
    from app import bcrypt 
    db_instance = get_db() 
    
    if current_user.is_authenticated:
        return redirect(url_for('home.homepage'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
      
        stmt = db_instance.select(User).filter_by(email=email)
        user_exists = db_instance.session.scalar(stmt)
        
        if user_exists: 
            return redirect(url_for('home.register')) 

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        new_user = User(email=email, password=hashed_password)
        db_instance.session.add(new_user) 
        db_instance.session.commit()

        return redirect(url_for('home.login')) 
        
    return render_template('register.html') 


@home_bp.route('/login', methods=['GET', 'POST'])
def login():
    from app.models.task import User
    from app import bcrypt 
    db_instance = get_db()

    if current_user.is_authenticated:
        return redirect(url_for('home.homepage'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

       
        stmt = db_instance.select(User).filter_by(email=email)
        user = db_instance.session.scalar(stmt)

        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('home.homepage')) 
        else:
            pass 

    return render_template('login.html')

@home_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home.login'))