import logging

from apscheduler.schedulers.background import BackgroundScheduler

from app.core.database import SessionLocal
from app.services.notification_service import NotificationService


logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()


def process_notification_jobs():
    db = SessionLocal()

    try:
        NotificationService.process_due_jobs(
            db
        )

    except Exception:
        logger.exception(
            "Unexpected notification worker failure"
        )

    finally:
        db.close()


def start_scheduler():
    scheduler.add_job(
        process_notification_jobs,
        trigger="interval",
        seconds=2,
        id="notification-worker",
        replace_existing=True
    )

    scheduler.start()


def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown()