from celery import Celery
from config import CELERY_CONFIG
app = Celery('celery_app',
             broker=CELERY_CONFIG['broker'],
             backend=CELERY_CONFIG['backend'],
             include=['celery_app.tasks'])

# Optional configuration, see the application user guide.
app.conf.update(
    result_expires=3600,
)

if __name__ == '__main__':
    app.start()
