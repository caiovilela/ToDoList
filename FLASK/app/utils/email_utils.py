import smtplib
from email.mime.text import MIMEText

def send_email(subject, body, to_email, from_email, smtp_server, smtp_port, smtp_user, smtp_password):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = from_email
    msg ['To'] = to_email

    with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
        server.login(smtp_user, smtp_password)
        server.sendmail(from_email, [to_email], msg.as_string())