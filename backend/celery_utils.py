from celery import Celery

# celery config
CELERY_BROKER_URL = 'redis://localhost:6379'
CELERY_RESULT_BACKEND = 'redis://localhost:6379'

# initialize celery app
def get_celery_app_instance(app):
    celery = Celery(
        app.import_name,
        backend=CELERY_BROKER_URL,
        broker=CELERY_BROKER_URL,
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        concurrency=2
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery