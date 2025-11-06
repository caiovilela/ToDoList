import smtplib
from email.message import EmailMessage
import mimetypes
from app.models.task import Task
from app import db
import os
from datetime import datetime
from sqlalchemy import func  # Adicione este import



def email_reminder():
    # Usando datetime.now() em vez de utcnow() para usar o horário local
    today = datetime.now().date()
    print(f"Buscando tarefas para a data: {today}")
    # Compara apenas a data, ignorando a hora
    tasks = Task.query.filter(
        func.date(Task.date) == today,
        Task.done == False
    ).all()
    print(f"Encontradas {len(tasks)} tarefas para hoje")
    
    remetente = "contatestebomar@gmail.com"
    senha = "sdtj ynlh trby wara"
    
    # Lista de emails dos proprietários que receberão as notificações
    owner_emails = [
        "pokemongamer197@gmail.com",
        "caiovilelam2004@gmail.com"
        # Adicione aqui os emails dos proprietários
    ]
    
    for task in tasks:
        # Mensagem para o cliente
        client_subject = "Você tem um serviço agendado para hoje!"
        client_message = f"Olá!\n\nVocê tem um serviço agendado para hoje:\n\nTítulo: {task.title}\nDescrição: {task.description}"
        
        # Enviando para o cliente
        if task.user_email:
            msg = EmailMessage()
            msg['From'] = remetente
            msg['To'] = task.user_email
            msg['Subject'] = client_subject
            msg.set_content(client_message)

            try:
                with smtplib.SMTP_SSL("smtp.gmail.com", 465) as email:
                    print(f"Tentando enviar email para o cliente: {task.user_email}")
                    email.login(remetente, senha)
                    print("Login realizado com sucesso")
                    email.send_message(msg)
                    print(f"E-mail enviado para o cliente: {task.user_email}")
            except Exception as e:
                print(f"Erro ao enviar email para o cliente: {str(e)}")
        
        # Mensagem para os proprietários
        owner_subject = f"Serviço agendado para hoje - {task.title}"
        owner_message = f"""Existe um serviço agendado para hoje:

Título: {task.title}
Descrição: {task.description}
Cliente: {task.user_email}"""

        # Enviando para os proprietários
        for owner_email in owner_emails:
            msg = EmailMessage()
            msg['From'] = remetente
            msg['To'] = owner_email
            msg['Subject'] = owner_subject
            msg.set_content(owner_message)

            try:
                with smtplib.SMTP_SSL("smtp.gmail.com", 465) as email:
                    print(f"Tentando enviar email para o proprietário: {owner_email}")
                    email.login(remetente, senha)
                    print("Login realizado com sucesso")
                    email.send_message(msg)
                    print(f"E-mail enviado para o proprietário: {owner_email}")
            except Exception as e:
                print(f"Erro ao enviar email para o proprietário: {str(e)}")




