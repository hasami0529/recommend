import click
from recommender.app import create_app
from recommender.extensions import db
from recommender.blueprints.user.models import User, Client
from sqlalchemy_utils import database_exists, create_database

#TODO It loads jieba again everytime I use cli.
app = create_app()
db.app = app


@click.group()
def cli():
    """Example script."""


@cli.command()
@click.option('--with-testdb/--no-with-testdb',
              default=False,
              help='Create a test db too?')
def init_db(with_testdb):
    """
    Initialize the database.

    :param with_testdb: Create a test database
    :return: None
    """
    # db.drop_all()
    # db.create_all()

    if with_testdb:
        db_uri = 'mysql+mysqldb://root:rootPassword@db:3306/Recommender_test?charset=utf8'

        if not database_exists(db_uri):
            create_database(db_uri)

    return None


@cli.command()
def create_seed():
    seed_user = User(email=app.config['ADMIN_EMAIL'],
                     role='admin',
                     username=app.config['ADMIN_USERNAME'],
                     password=app.config['ADMIN_PASSWORD'])
    seed_user.save()

    c = Client()
    c.signup_client(seed_user)