from celery.schedules import crontab
DEBUG = True

SERVER_NAME = 'localhost:8000'
SECRET_KEY = 'insecurekeyfordev'

# SQLAlchemy.
SQLALCHEMY_DATABASE_URI = 'mysql+mysqldb://developer:developerPassword@db:3306/Recommender?charset=utf8'
SQLALCHEMY_TRACK_MODIFICATIONS = False

OAUTHLIB_INSECURE_TRANSPORT = 1

#redis
REDIS_HOST = 'redis'
REDIS_PORT = 6379
REDIS_PASSWORD = 'devpassword'

#celery
CELERY_BROKER_URL = 'redis://:devpassword@redis:6379/0'
CELERY_RESULT_BACKEND = 'redis://:devpassword@redis:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_REDIS_MAX_CONNECTIONS = 5
CELERYBEAT_SCHEDULE = {
    'compute_and_cache_result_every_hour': {
        'task': 'recommender.blueprints.article.tasks.compute_all',
        'schedule': crontab(minute=0, hour="*/1")
    }
}

#seed admin
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'adminPassword'
ADMIN_EMAIL = 'admin@gmail.com'