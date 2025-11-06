from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import datetime
from flask_login import login_user, login_required, logout_user, current_user
from flask import current_app 
from sqlalchemy import not_

home_bp = Blueprint('home', __name__)


def get_db():
   
    return current_app.extensions['sqlalchemy']



@home_bp.route('/')
@login_required 
def homepage():
    from app.models.task import Task, Client 
    db_instance = get_db()
    
  
    stmt_tasks = db_instance.select(Task).filter_by(user_id=current_user.id)
    tasks = db_instance.session.scalars(stmt_tasks).all() 

    stmt_clients = db_instance.select(Client).filter_by(owner=current_user).order_by(Client.name)
    clients = db_instance.session.scalars(stmt_clients).all()
    

    return render_template('home.html', tasks=tasks, clients=clients)


@home_bp.route('/tasks')
@login_required 
def list_tasks():
    from app.models.task import Task
    db_instance = get_db()
    from sqlalchemy import not_
    stmt = db_instance.select(Task).filter(
        Task.user_id == current_user.id,
        not_(Task.status.in_(['Concluído', 'Cancelado']))
    )
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
    client_id = request.form.get('client_id')

    if client_id == "":
        client_id = None
    

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
                    user_id=current_user.id,
                    client_id=client_id) 
    
    db_instance.session.add(new_task) 
    db_instance.session.commit()

    flash('Serviço adicionado com sucesso.', 'success')
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

        task.status=request.form.get('status')

        db_instance.session.commit()
        flash('Serviço atualizado com sucesso.', 'success')
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
    flash('Serviço removido com sucesso.', 'success')
    return redirect(url_for('home.list_tasks'))




@home_bp.route('/tasks/done')
@login_required 
def list_done_tasks():
    from app.models.task import Task
    db_instance = get_db()
    
    
    stmt = db_instance.select(Task).filter_by(user_id=current_user.id, status='Concluído')
    done_tasks = db_instance.session.scalars(stmt).all()
    
    return render_template('done_tasks.html', tasks=done_tasks)



@home_bp.route('/calendar')
@login_required 
def calendar():
    from app.models.task import Task
    db_instance = get_db()
    
    stmt = db_instance.select(Task).filter(
        Task.user_id == current_user.id,
        not_(Task.status.in_(['Concluído', 'Cancelado'])), 
        Task.date.isnot(None) 
    )
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


@home_bp.route('/clients')
@login_required
def list_clients():
    from app.models.task import Client
    db_instance = get_db()
    stmt = db_instance.select(Client).filter_by(owner=current_user)
    clients = db_instance.session.scalars(stmt).all()

    return render_template('clients.html', clients=clients)


@home_bp.route('/client/<int:client_id>')
@login_required
def client_detail(client_id):

    from app.models.task import Client 
    db_instance = get_db()
    
    stmt = db_instance.select(Client).filter_by(id=client_id, owner=current_user)
    client = db_instance.session.scalar(stmt)
    
    if not client:
        flash('Cliente não encontrado ou acesso não autorizado.', 'danger')
        return redirect(url_for('home.list_clients'))

    return render_template('client_detail.html', client=client)




@home_bp.route('/add_client', methods=['GET', 'POST'])
@login_required
def add_client():
    from app.models.task import Client
    db_instance = get_db()
    
    if request.method == 'POST':
        
        name = request.form.get('name')
        phone = request.form.get('phone')
        address = request.form.get('address')
        
      
        new_client = Client(name=name, 
                            phone=phone, 
                            address=address, 
                            owner=current_user) 
        
        db_instance.session.add(new_client)
        db_instance.session.commit()
        flash('Cliente adicionado com sucesso.', 'success')
        return redirect(url_for('home.list_clients'))
    return render_template('add_client.html')


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
            flash('Já existe um usuário com esse e-mail.', 'danger')
            return redirect(url_for('home.register'))

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        new_user = User(email=email, password=hashed_password)
        db_instance.session.add(new_user) 
        db_instance.session.commit()
        flash('Cadastro realizado com sucesso. Faça login.', 'success')
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
            flash('Login realizado com sucesso.', 'success')
            return redirect(url_for('home.homepage')) 
        else:
            flash('E-mail ou senha inválidos.', 'danger')
            return render_template('login.html')

    return render_template('login.html')

@home_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você saiu do sistema.', 'info')
    return redirect(url_for('home.login'))