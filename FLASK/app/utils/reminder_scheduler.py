from apscheduler.schedulers.background import BackgroundScheduler
from app.models.task import Task
from app.utils.email_utils import send_email
from app import db
from datetime import datetime
import os

def send_daily_reminders():
    today = datetime.utcnow().date()
    tasks = Task.query.filter(Task.date == today, Task.done == False).all()
    for task in tasks:
        print(f"enviando para: {task.user_email}")
       
        subject = f"Lembrete: {task.title}"
        body = f"Você tem uma tarefa marcada para hoje:\n\n{task.title}\n{task.description}"
        to_email = task.user_email
        from_email = "contatestebomar@gmail.com"
        smtp_user = "contatestebomar@gmail.com"
        smtp_password = "sdtj ynlh trby wara"
        send_email(
            subject, body, to_email, from_email,
            smtp_server="smtp.gmail.com",
            smtp_port=465,
            smtp_user=smtp_user,
            smtp_password=smtp_password
        )

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(send_daily_reminders, 'cron', hour=8)  # Executa todo dia às 8h UTC
    scheduler.start()