from celery import Celery 
from dotenv import load_dotenv
import os
from .config import Settings

settings = Settings()

user = settings.rabbitmqdefaultuser
password = settings.rabbitmqdefaultpassword

print(f"connecting with user {user}")

celery_worker = Celery(
    "notification_worker",
    broker=f"pyamqp://{user}:{password}@rabbitmq/",
    backend="redis://redis:6379/0"
)

celery_worker.conf.task_routes = {
    "notification.tasks.send_email_notification": {"queue": "email"},
    "notification.tasks.send_sms_task": {"queue":"sms"}
}

import notification.tasks

