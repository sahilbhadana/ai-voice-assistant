import os
import threading
import time

from app.db.database import SessionLocal
from app.services.booking_service import send_upcoming_sms_reminders

_scheduler_thread = None


def start_reminder_scheduler():
    global _scheduler_thread

    enabled = os.getenv("ENABLE_REMINDER_SCHEDULER", "false").lower() == "true"
    if not enabled or _scheduler_thread:
        return

    interval_seconds = int(os.getenv("REMINDER_SCHEDULER_INTERVAL_SECONDS", "300"))
    minutes_ahead = int(os.getenv("REMINDER_WINDOW_MINUTES", "1440"))

    _scheduler_thread = threading.Thread(
        target=_run_scheduler,
        args=(interval_seconds, minutes_ahead),
        daemon=True,
    )
    _scheduler_thread.start()


def _run_scheduler(interval_seconds: int, minutes_ahead: int):
    while True:
        db = SessionLocal()
        try:
            send_upcoming_sms_reminders(db, minutes_ahead)
        finally:
            db.close()
        time.sleep(interval_seconds)
