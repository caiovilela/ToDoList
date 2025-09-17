from app import create_app
from app.utils.reminder_scheduler import send_daily_reminders

app = create_app()
with app.app_context():
    send_daily_reminders()