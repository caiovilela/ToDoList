import smtplib
from email.message import EmailMessage
import mimetypes
from app.models.task import Task
from app import db
import os
from datetime import datetime
from sqlalchemy import func  # Adicione este import



def email_reminder():
    today = datetime.utcnow().date()
    # Compara apenas a data, ignorando a hora
    tasks = Task.query.filter(
        func.date(Task.date) == today,
        Task.done == False
    ).all()
    remetente = "contatestebomar@gmail.com"
    senha = "sdtj ynlh trby wara"
    
    for task in tasks:
        print(f"enviando para: {task.user_email}")
        destinatario = task.user_email
        assunto = "Você tem um serviço agendado para hoje!"
        mensagem = f"Título: {task.title}\nDescrição: {task.description}"

        msg = EmailMessage()
        msg['From'] = remetente
        msg['To'] = destinatario
        msg['Subject'] = assunto
        msg.set_content(mensagem)

        with smtplib.SMTP_SSL("smtp.gmail.com",465) as email:
            email.login(remetente, senha)
            email.send_message(msg)
            print(f"E-mail enviado para {destinatario}")




