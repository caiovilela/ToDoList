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
        
        if task.client and task.client.email:
            client_subject = f"Lembrete de Serviço Agendado: {task.title}"
            client_message = f"""Olá, {task.client.name}!

Este é um lembrete de que seu serviço está agendado para hoje:

Título: {task.title}
Status: {task.status}
Técnico: {task.technician.name if task.technician else 'A definir'}
"""
            
            msg_client = EmailMessage()
            msg_client['From'] = remetente
            msg_client['To'] = task.client.email
            msg_client['Subject'] = client_subject
            msg_client.set_content(client_message)

            try:
                with smtplib.SMTP_SSL("smtp.gmail.com", 465) as email:
                    print(f"Tentando enviar email para o CLIENTE: {task.client.email}")
                    email.login(remetente, senha)
                    print("Login realizado com sucesso")
                    email.send_message(msg_client)
                    print(f"E-mail enviado para o CLIENTE: {task.client.email}")
            except Exception as e:
                print(f"Erro ao enviar email para o CLIENTE: {str(e)}")




def send_status_update_email(task):
      
   if not (task.client and task.client.email):
       print(f"Tarefa {task.id} sem cliente ou sem e-mail de cliente. E-mail não enviado.")
       return

   remetente = "contatestebomar@gmail.com"
   senha = "sdtj ynlh trby wara"

   subject = ""
   message_body = ""

   if task.status == "Em Andamento":
       subject = f"Serviço a caminho: {task.title}"
       message_body = f"""Olá, {task.client.name}!

Nosso técnico, {task.technician.name if task.technician else 'Nossa equipe'}, está a caminho do seu local para o serviço:

Título: {task.title}

Até breve!
"""
   elif task.status == "Concluído":
       subject = f"Serviço Concluído: {task.title}"
       message_body = f"""Olá, {task.client.name}!

Seu serviço foi marcado como concluído:

Título: {task.title}
Comentários: {task.done_comment if task.done_comment else 'Nenhum'}

Obrigado por estar com a Bom Ar!
"""
   else:
       
       return

   
   msg = EmailMessage()
   msg['From'] = remetente
   msg['To'] = task.client.email
   msg['Subject'] = subject
   msg.set_content(message_body)

   try:
       with smtplib.SMTP_SSL("smtp.gmail.com", 465) as email:
           print(f"Disparando e-mail de status '{task.status}' para CLIENTE: {task.client.email}")
           email.login(remetente, senha)
           email.send_message(msg)
           print(f"E-mail de status enviado para: {task.client.email}")
   except Exception as e:
       print(f"Erro ao disparar e-mail de status: {str(e)}")
