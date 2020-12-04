from flask_sqlalchemy import SQLAlchemy
from authlib.flask.oauth2 import AuthorizationServer
from flask_login import LoginManager
import redis
from celery import Celery
from config.settings import CELERY_BROKER_URL
import flask


class FlaskCelery(Celery):
    def __init__(self, *args, **kwargs):

        super(FlaskCelery, self).__init__(*args, **kwargs)
        self.patch_task()

        if 'app' in kwargs:
            self.init_app(kwargs['app'])

    def patch_task(self):
        TaskBase = self.Task
        _celery = self

        class ContextTask(TaskBase):
            abstract = True

            def __call__(self, *args, **kwargs):
                if flask.has_app_context():
                    return TaskBase.__call__(self, *args, **kwargs)
                else:
                    with _celery.app.app_context():
                        return TaskBase.__call__(self, *args, **kwargs)

        self.Task = ContextTask

    def init_app(self, app):
        self.app = app
        self.config_from_object(app.config)


CELERY_TASK_LIST = ['recommender.blueprints.article.tasks']

celery_app = FlaskCelery('recommender',
                         broker=CELERY_BROKER_URL,
                         include=CELERY_TASK_LIST)
db = SQLAlchemy()
auth_server = AuthorizationServer()
login_manager = LoginManager()
