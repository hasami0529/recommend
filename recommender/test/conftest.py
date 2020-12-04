import pytest

from config import settings
from recommender.app import create_app
from recommender.extensions import db as _db
from recommender.blueprints.user.models import User


@pytest.yield_fixture(scope='session')
def app():
    """
    Setup our flask test app, this only gets executed once.

    :return: Flask app
    """
    db_uri = 'mysql+mysqldb://root:rootPassword@db:3306/Recommender_test?charset=utf8'
    params = {
        'DEBUG': False,
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': db_uri
    }

    _app = create_app(settings_override=params)

    # Establish an application context before running the tests.
    ctx = _app.app_context()
    ctx.push()

    yield _app

    ctx.pop()


@pytest.yield_fixture(scope='function')
def client(app):
    """
    Setup an app client, this gets executed for each test function.

    :param app: Pytest fixture
    :return: Flask app client
    """
    yield app.test_client()


@pytest.fixture(scope='session')
def db(app):
    """
    Setup our database, this only gets executed once per session.

    :param app: Pytest fixture
    :return: SQLAlchemy database session
    """
    _db.drop_all()
    _db.create_all()

    # Create a single user because a lot of tests do not mutate this user.
    # It will result in faster tests.
    admin_info = {
        'role': 'admin',
        'email': 'admin@gmail.com',
        'password': 'adminPassword'
    }

    admin = User(**admin_info)
    admin.save()

    member_info = {'email': 'member@gmail.com', 'password': 'memberPassword'}

    member = User(**member_info)
    member.save()

    return _db


@pytest.yield_fixture(scope='function')
def session(db):
    """
    Allow very fast tests by using rollbacks and nested sessions. This does
    require that your database supports SQL savepoints, and Postgres does.

    Read more about this at:
    http://stackoverflow.com/a/26624146

    :param db: Pytest fixture
    :return: None
    """
    db.session.begin_nested()

    yield db.session

    db.session.rollback()


# @pytest.fixture(scope='session')
# def token(db):
#     """
#     Serialize a JWS token.

#     :param db: Pytest fixture
#     :return: JWS token
#     """
#     user = User.find_by_identity('admin@local.host')
#     return user.serialize_token()

# @pytest.fixture(scope='function')
# def users(db):
#     """
#     Create user fixtures. They reset per test.

#     :param db: Pytest fixture
#     :return: SQLAlchemy database session
#     """
#     db.session.query(User).delete()

#     users = [{
#         'role': 'admin',
#         'email': 'admin@local.host',
#         'password': 'password'
#     }, {
#         'active': False,
#         'email': 'disabled@local.host',
#         'password': 'password'
#     }]

#     for user in users:
#         db.session.add(User(**user))

#     db.session.commit()

#     return db
