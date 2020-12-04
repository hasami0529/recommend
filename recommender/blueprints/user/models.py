from collections import OrderedDict
from flask import current_app
from lib.utils_sqlalchemy import ResourceMixin, tzware_datetime
from recommender.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash, gen_salt
from authlib.flask.oauth2.sqla import OAuth2ClientMixin
from authlib.flask.oauth2.sqla import OAuth2TokenMixin
from flask_login import UserMixin
from werkzeug.exceptions import BadRequest

#TODO user to refer client clss doesn't work


class User(ResourceMixin, db.Model, UserMixin):
    ROLE = OrderedDict([('member', 'Member'), ('admin', 'Admin')])

    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)

    # Authentication.
    role = db.Column(db.Enum(*ROLE, name='role_types', native_enum=False),
                     index=True,
                     nullable=False,
                     server_default='member')
    active = db.Column('is_active',
                       db.Boolean(),
                       nullable=False,
                       server_default='1')
    username = db.Column(db.String(24), index=True)
    email = db.Column(db.String(255),
                      unique=True,
                      index=True,
                      nullable=False,
                      server_default='')
    password = db.Column(db.String(128), nullable=False, server_default='')

    #relationship
    client = db.relationship('Client', backref='users', uselist=False)

    # Activity tracking.
    current_sign_in_on = db.Column(db.DateTime())
    last_sign_in_on = db.Column(db.DateTime())

    def __init__(self, email, password, username=None, role='member'):
        self.username = username
        if role in self.ROLE.keys():
            self.role = role
        else:
            raise BadRequest(
                description='Only accept admin or member in role parameter ')
        self.email = email
        self.password = User.encrypt_password(password)
        c = Client()
        c.signup_client(self)
        self.client = c

    @classmethod
    def find_by_identity(cls, identity):
        """
        Find a user by their e-mail or username.

        :param identity: Email or username
        :type identity: str
        :return: User instance
        """
        return User.query.filter((User.email == identity)
                                 | (User.username == identity)).first()

    @classmethod
    def find_by_uid(cls, uid):
        return User.query.filter(User.id == uid).first()

    @classmethod
    def encrypt_password(cls, plaintext_password):
        """
        Hash a plaintext string using PBKDF2. This is good enough according
        to the NIST (National Institute of Standards and Technology).

        In other words while bcrypt might be superior in practice, if you use
        PBKDF2 properly (which we are), then your passwords are safe.

        :param plaintext_password: Password in plain text
        :type plaintext_password: str
        :return: str
        """
        if plaintext_password:
            return generate_password_hash(plaintext_password)

        return None

    def is_active(self):
        """
        Return whether or not the user account is active, this satisfies
        Flask-Login by overwriting the default value.

        :return: bool
        """
        return self.active

    def authenticated(self, password):
        return check_password_hash(self.password, password)

    def update_activity_tracking(self, ip_address):
        """
        Update various fields on the user that's related to meta data on their
        account, such as the sign in count and ip address, etc..

        :param ip_address: IP address
        :type ip_address: str
        :return: SQLAlchemy commit results
        """
        self.sign_in_count += 1

        self.last_sign_in_on = self.current_sign_in_on
        self.last_sign_in_ip = self.current_sign_in_ip

        self.current_sign_in_on = tzware_datetime()

        return self.save()

    def get_user_id(self):
        return self.id


class Client(db.Model, OAuth2ClientMixin):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer,
                        db.ForeignKey('users.id', ondelete='CASCADE'))
    user = db.relationship('User')

    #overide
    token_endpoint_auth_method = db.Column(db.String(48),
                                           default='client_secret_post')
    grant_type = db.Column(db.Text,
                           nullable=False,
                           default='client_credentials')
    client_id = db.Column(db.String(24), index=True, default=gen_salt(24))
    client_secret = db.Column(db.String(48), default=gen_salt(48))

    def signup_client(self, u):

        self.user_id = u.id
        self.client_name = u.username
        self.scope = u.role
        db.session.add(self)
        db.session.commit()

    def make_secret_response(self):
        return {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
        }


class Token(db.Model, OAuth2TokenMixin):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer,
                        db.ForeignKey('users.id', ondelete='CASCADE'))
    user = db.relationship('User')
