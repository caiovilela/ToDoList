import smtplib
from email.message import EmailMessage
import mimetypes
from app.models.task import Task, User
from app import db
import os
from datetime import datetime
from sqlalchemy import func  
from sqlalchemy import not_
from sqlalchemy.orm import joinedload



def email_reminder():
    
    today = datetime.now().date()
    print(f"Buscando tarefas para a data: {today}")
   
  
    tasks = Task.query.options(
        joinedload(Task.author),
        joinedload(Task.technician),
        joinedload(Task.client) 
    ).filter(
        func.date(Task.date) == today,
        not_(Task.status.in_(['Concluído', 'Cancelado']))
    ).all()
    
    
    print(f"Encontradas {len(tasks)} tarefas para hoje")
    
    remetente = "contatestebomar@gmail.com"
    senha = "sdtj ynlh trby wara"
    
   
    
    
    for task in tasks:
        
       
        if task.technician:
            tec_subject = f"Lembrete de Serviço: {task.title}"
            tec_message = f"""Olá, {task.technician.name}!

Você tem um serviço agendado para hoje:

Título: {task.title}
Status: {task.status}
Cliente: {task.client.name if task.client else 'Serviço Avulso'}
Descrição: {task.description}
"""
            
            msg_tec = EmailMessage()
            msg_tec['From'] = remetente
            msg_tec['To'] = task.technician.email
            msg_tec['Subject'] = tec_subject
            msg_tec.set_content(tec_message)

            try:
                with smtplib.SMTP_SSL("smtp.gmail.com", 465) as email:
                    print(f"Tentando enviar email para o TÉCNICO: {task.technician.email}")
                    email.login(remetente, senha)
                    print("Login realizado com sucesso")
                    email.send_message(msg_tec)
                    print(f"E-mail enviado para o TÉCNICO: {task.technician.email}")
            except Exception as e:
                print(f"Erro ao enviar email para o TÉCNICO: {str(e)}")
        
        
   
        if task.author:
            admin_subject = f"Serviço Agendado para Hoje: {task.title}"
            admin_message = f"""Lembrete de Admin:
Existe um serviço agendado para hoje:

Título: {task.title}
Técnico: {task.technician.name if task.technician else 'Não atribuído'}
Cliente: {task.client.name if task.client else 'Serviço Avulso'}
Status: {task.status}
"""
            msg_admin = EmailMessage()
            msg_admin['From'] = remetente
            msg_admin['To'] = task.author.email
            msg_admin['Subject'] = admin_subject
            msg_admin.set_content(admin_message)

            try:
                with smtplib.SMTP_SSL("smtp.gmail.com", 465) as email:
                    print(f"Tentando enviar email para o ADMIN: {task.author.email}")
                    email.login(remetente, senha)
                    print("Login realizado com sucesso")
                    email.send_message(msg_admin)
                    print(f"E-mail enviado para o ADMIN: {task.author.email}")
            except Exception as e:
                print(f"Erro ao enviar email para o ADMIN: {str(e)}")

