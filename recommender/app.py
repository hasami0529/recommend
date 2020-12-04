from authlib.oauth2.rfc6749 import grants
from flask import Flask
from recommender.blueprints.article import article
from recommender.blueprints.user import user

from recommender.blueprints.user.models import Client, Token, User
from recommender.extensions import auth_server, db, login_manager, celery_app
import redis
from celery.schedules import crontab

login_manager.login_view = '/user/login/error'


def query_client(client_id):
    return Client.query.filter_by(client_id=client_id).first()


def save_token(token, request):
    #TODO user id is not in token table
    if request.user:
        user_id = request.user.get_user_id()
    else:
        user_id = request.client.user_id
        user_id = None
    item = Token(client_id=request.client.client_id,
                 user_id=user_id,
                 scope=request.client.scope,
                 **token)
    db.session.add(item)
    db.session.commit()


def setup_auth():
    class myClientCredentialsGrant(grants.ClientCredentialsGrant):
        TOKEN_ENDPOINT_AUTH_METHODS = ['client_secret_post']

    auth_server.register_grant(myClientCredentialsGrant)


def create_app(settings_override=None):
    """
    Create a Flask application using the app factory pattern.

    :param settings_override: Override settings
    :return: Flask app
    """
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_object('config.settings')
    # app.config.from_pyfile('settings.py', silent=True)

    if settings_override:
        app.config.update(settings_override)

    #blueprints
    app.register_blueprint(user)
    app.register_blueprint(article)

    #extensions init
    db.init_app(app)
    login_manager.init_app(app)
    celery_app.init_app(app)
    setup_auth()

    auth_server.init_app(app, query_client=query_client, save_token=save_token)

    return app


app = create_app()


@login_manager.user_loader
def load_user(uid):
    return User.find_by_uid(uid)


def create_redis_app():
    pool = redis.ConnectionPool(host=app.config['REDIS_HOST'],
                                port=app.config['REDIS_PORT'],
                                decode_responses=True,
                                password=app.config['REDIS_PASSWORD'])
    r = redis.Redis(connection_pool=pool)
    return r
