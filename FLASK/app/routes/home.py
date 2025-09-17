from flask import Blueprint, render_template, request, redirect, url_for
from app import db  
from app.models.task import Task 
from datetime import datetime

home_bp = Blueprint('home', __name__)

@home_bp.route('/')
def homepage():
    task = Task.query.all()  
    return render_template('home.html', task=task)




@home_bp.route('/tasks')
def list_tasks():
    tasks = Task.query.all()  
    return render_template('tasks.html', tasks=tasks) 



@home_bp.route('/add', methods=['POST'])
def add_task():
    title = request.form.get('title')
    description = request.form.get('description')
    date_str = request.form.get('date') 
    user_email = request.form.get("user_email") 

    
    if date_str:
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d')  
        except ValueError:
            date = datetime.utcnow()  
    else:
        date = datetime.utcnow()  

    new_task = Task(title=title, description=description, date=date, user_email=user_email)
    db.session.add(new_task)
    db.session.commit()

    return redirect(url_for('home.homepage'))

@home_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_task(id):
    task = Task.query.get(id)

    if request.method == 'POST':
        task.title = request.form.get('title')
        task.description = request.form.get('description')
        date_str = request.form.get('date')

        
        if date_str:
            try:
                task.date = datetime.strptime(date_str, '%Y-%m-%d')
            except ValueError:
                task.date = None  

        db.session.commit()
        return redirect(url_for('home.homepage'))

    return render_template('edit.html', task=task)

@home_bp.route('/delete/<int:id>', methods=['GET'])
def delete_task(id):
    task = Task.query.get(id)
    if not task:
        return "Tarefa não encontrada", 404
    db.session.delete(task)
    db.session.commit()

    
    return redirect(url_for('home.list_tasks'))


@home_bp.route('/done/<int:id>', methods=['GET', 'POST'])
def mark_task_done(id):
    task = Task.query.get(id)  

    if not task:
        return "Tarefa não encontrada", 404  

    if request.method == 'POST':
        task.done = True
        task.done_comment = request.form.get('done_comment')  
        db.session.commit()
        return redirect(url_for('home.list_tasks'))

    return render_template('done.html', task=task)

@home_bp.route('/tasks/done')
def list_done_tasks():
    done_tasks = Task.query.filter_by(done=True).all()
    return render_template('done_tasks.html', tasks=done_tasks)


# esta com problemas. preciso ver isso depois
@home_bp.route('/calendar')
def calendar():
    tasks = Task.query.all()  
    events = [
        {
            "title": task.title,
            "start": task.date.strftime('%Y-%m-%d') if task.date else None,
            "description": task.description
        }
        for task in tasks if task.date  
    ]
    return render_template('calendar.html', events=events)