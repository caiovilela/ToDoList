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
    from app.models.task import Task, Client, User 
    db_instance = get_db()
    
    
    
    if current_user.role == 'admin':
        
        
        stmt_tasks = db_instance.select(Task).filter_by(user_id=current_user.id)
        tasks = db_instance.session.scalars(stmt_tasks).all() 

        stmt_clients = db_instance.select(Client).filter_by(owner=current_user).order_by(Client.name)
        clients = db_instance.session.scalars(stmt_clients).all()
        
        stmt_techs = db_instance.select(User).filter_by(role='tecnico').order_by(User.name)
        technicians = db_instance.session.scalars(stmt_techs).all()

        return render_template('home.html', tasks=tasks, clients=clients, technicians=technicians)
    
    else:
        
        stmt_tasks = db_instance.select(Task).filter(
            Task.technician_id == current_user.id,
            not_(Task.status.in_(['Concluído', 'Cancelado'])) 
        ).order_by(Task.date)
        
        tasks = db_instance.session.scalars(stmt_tasks).all()

        
        return render_template('technician_dashboard.html', tasks=tasks)
    


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
    
    if current_user.role != 'admin':
        flash('Acesso não autorizado.', 'danger')
        return redirect(url_for('home.homepage'))
    

    from app.models.task import Task
    db_instance = get_db()
    
    title = request.form.get('title')
    description = request.form.get('description')
    date_str = request.form.get('date')
    client_id = request.form.get('client_id')
    technician_id = request.form.get('technician_id')

    if client_id == "":
        client_id = None
        
    if technician_id == "":
        technician_id = None
    

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
                    client_id=client_id,
                    technician_id=technician_id) 
    
    db_instance.session.add(new_task) 
    db_instance.session.commit()

    flash('Serviço adicionado com sucesso.', 'success')
    return redirect(url_for('home.homepage'))

@home_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required 
def edit_task(id):
    from app.models.task import Task, User
    
    from app.utils.email_utils import send_status_update_email
    
    
    db_instance = get_db()
    
    
    stmt = db_instance.select(Task).filter_by(id=id) 
    task = db_instance.session.scalar(stmt)

    if not task:
        return "Tarefa não encontrada", 404
        
    if current_user.role == 'admin' and task.user_id != current_user.id:
        flash('Acesso não autorizado (Admin).', 'danger')
        return redirect(url_for('home.homepage'))
    elif current_user.role == 'tecnico' and task.technician_id != current_user.id:
        flash('Acesso não autorizado (Técnico).', 'danger')
        return redirect(url_for('home.homepage'))


    if request.method == 'POST':
        
        
        old_status = task.status
        
        if current_user.role == 'admin':
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
            
            technician_id = request.form.get('technician_id')
            if technician_id == "":
                technician_id = None
            task.technician_id = technician_id

        task.status = request.form.get('status')
        new_status = task.status

        db_instance.session.commit() 
        
        
        if new_status != old_status and (new_status == 'Em Andamento' or new_status == 'Concluído'):
            try:
                
                send_status_update_email(task)
            except Exception as e:
                print(f"Falha ao tentar enviar e-mail de mudança de status: {e}")
                

        flash('Serviço atualizado com sucesso.', 'success')
        return redirect(url_for('home.homepage'))
    
    technicians = []
    if current_user.role == 'admin':
        stmt_techs = db_instance.select(User).filter_by(role='tecnico').order_by(User.name)
        technicians = db_instance.session.scalars(stmt_techs).all()
    return render_template('edit.html', task=task, technicians=technicians)

   
   

@home_bp.route('/delete/<int:id>', methods=['GET'])
@login_required 
def delete_task(id):
    
    if current_user.role != 'admin':
        flash('Acesso não autorizado.', 'danger')
        return redirect(url_for('home.homepage'))
    

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
    
  
    if current_user.role == 'admin':
        stmt = db_instance.select(Task).filter_by(user_id=current_user.id, status='Concluído')
    else:
        stmt = db_instance.select(Task).filter_by(technician_id=current_user.id, status='Concluído')
    
    
    done_tasks = db_instance.session.scalars(stmt).all()
    
    return render_template('done_tasks.html', tasks=done_tasks)



@home_bp.route('/calendar')
@login_required 
def calendar():
    from app.models.task import Task
    db_instance = get_db()
    
    
    if current_user.role == 'admin':
        stmt = db_instance.select(Task).filter(
            Task.user_id == current_user.id,
            not_(Task.status.in_(['Concluído', 'Cancelado'])), 
            Task.date.isnot(None) 
        )
    else:
        stmt = db_instance.select(Task).filter(
            Task.technician_id == current_user.id,
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
    
    if current_user.role != 'admin':
        flash('Acesso não autorizado.', 'danger')
        return redirect(url_for('home.homepage'))
    
    
    from app.models.task import Client
    db_instance = get_db()
    stmt = db_instance.select(Client).filter_by(owner=current_user)
    clients = db_instance.session.scalars(stmt).all()

    return render_template('clients.html', clients=clients)


@home_bp.route('/client/<int:client_id>')
@login_required
def client_detail(client_id):
    
    if current_user.role != 'admin':
        flash('Acesso não autorizado.', 'danger')
        return redirect(url_for('home.homepage'))
   

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
    
    if current_user.role != 'admin':
        flash('Acesso não autorizado.', 'danger')
        return redirect(url_for('home.homepage'))
    
    
    from app.models.task import Client
    db_instance = get_db()
    
    if request.method == 'POST':
        
        name = request.form.get('name')
        phone = request.form.get('phone')
        address = request.form.get('address')


        email = request.form.get('email')
      
        new_client = Client(name=name, 
                            phone=phone, 
                            address=address,
                            email=email, 
                            owner=current_user) 
        
        db_instance.session.add(new_client)
        db_instance.session.commit()
        flash('Cliente adicionado com sucesso.', 'success')
        return redirect(url_for('home.list_clients'))
    return render_template('add_client.html')




@home_bp.route('/equipe', methods=['GET'])
@login_required
def equipe():
    
    if current_user.role != 'admin':
        flash('Acesso não autorizado.', 'danger')
        return redirect(url_for('home.homepage'))

    from app.models.task import User
    db_instance = get_db()
    
    
    stmt = db_instance.select(User).filter_by(role='tecnico')
    technicians = db_instance.session.scalars(stmt).all()
    
    return render_template('equipe.html', technicians=technicians)


@home_bp.route('/add_tecnico', methods=['POST'])
@login_required
def add_tecnico():
    
    if current_user.role != 'admin':
        flash('Acesso não autorizado.', 'danger')
        return redirect(url_for('home.homepage'))

    from app.models.task import User 
    from app import bcrypt 
    db_instance = get_db() 

    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        
        
        stmt = db_instance.select(User).filter_by(email=email)
        user_exists = db_instance.session.scalar(stmt)
        
        if user_exists:
            flash('Já existe um usuário com esse e-mail.', 'danger')
            return redirect(url_for('home.equipe'))

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        
        new_user = User(email=email, 
                        password=hashed_password, 
                        name=name,
                        role='tecnico') 
        
        db_instance.session.add(new_user) 
        db_instance.session.commit()
        
        flash('Técnico cadastrado com sucesso.', 'success')
        return redirect(url_for('home.equipe'))






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


@home_bp.route('/delete_user/<int:user_id>', methods=['GET'])
@login_required
def delete_user(user_id):
    if current_user.role != 'admin':
        flash('Acesso não autorizado', 'danger')
        return redirect(url_for('home.homepage'))
    
    from app.models.task import User, Task
    db_instance = get_db()

    user_to_delete = db_instance.session.get(User, user_id)

    if not user_to_delete:
        flash('Usuário não encontrado.','danger')
        return redirect(url_for('home.equipe'))
    if user_to_delete.role == 'admin':
        flash('Não é possível excluir um administrador','danger')
        return redirect(url_for('home.equipe'))
    

    stmt_task = db_instance.select(Task).filter_by(technician_id=user_id)
    tasks_assigned = db_instance.session.scalars(stmt_task).all()

    for task in tasks_assigned:
        task.technician_id = None

    db_instance.session.delete(user_to_delete)
    db_instance.session.commit()

    flash(f'Técnico {user_to_delete.name} removido!','sucess')
    return redirect(url_for('home.equipe'))