from app.core.celery_app import celery_app
from app.services.email import send_email


@celery_app.task(bind=True, autoretry_for=(Exception,), retry_kwargs={"max_retries": 5, "countdown": 60})
def send_event_email(self, to: str, subject: str, body: str):
    send_email(to, subject, body)
