from celery import Celery

celery_app = Celery("backend_workers", broker="redis://localhost:6379/0")

@celery_app.task
def ping():
    return "pong"
