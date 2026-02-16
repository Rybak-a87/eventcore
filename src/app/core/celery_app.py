from celery import Celery


celery_app = Celery(
    "worker",
    broker="amqp://guest:guest@rabbitmq:5672//",
    backend="rpc://"
)

celery_app.autodiscover_tasks(["app.tasks"])
