from app import create_app
from celery import Celery, schedules
from models import db

app = create_app()
celery = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(
    broker_url=app.config['CELERY_BROKER_URL'],
    result_backend=app.config['CELERY_RESULT_BACKEND'],
    timezone=app.config.get('CELERY_TIMEZONE', 'UTC'),
    task_serializer='json',
    accept_content=['json'],
    include=['tasks']
)
celery.conf.beat_schedule = {
    'delete-expired-tokens-every-day': {
        'task': 'tasks.delete_expired_tokens',
        'schedule': schedules.crontab(minute=0, hour=0),
    },
}
app.celery = celery

if __name__ == '__main__':
    # with app.app_context():
    #     db.create_all()
    app.run(debug=True)
