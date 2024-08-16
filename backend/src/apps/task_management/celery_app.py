from celery import Celery
import os, sys
root_directory = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root_directory)
from config.settings import settings
current_directory = os.path.dirname(os.path.abspath(__file__))
celery = Celery(
    'tasks',
    broker=settings.BROKER_URL,
    backend=settings.BROKER_URL,
    include=["apps.task_management.newsletter.email"]
)
celery.conf.broker_connection_retry_on_startup = True