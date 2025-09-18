from app import create_app
from app.utils.email_utils import email_reminder

app = create_app()
with app.app_context():
    email_reminder()