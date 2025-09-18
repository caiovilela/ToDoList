from apscheduler.schedulers.background import BackgroundScheduler
from flask import current_app


def start_scheduler(app):
    from app.utils.email_utils import email_reminder

    scheduler = BackgroundScheduler()
    scheduler.add_job(
        func=lambda:email_reminder_with_context(app),
        trigger='cron',
        hour=7,
        minute=0
    )
    scheduler.start()


def email_reminder_with_context(app):
    with app.app_context():
        from app.utils.email_utils import email_reminder
        email_reminder()