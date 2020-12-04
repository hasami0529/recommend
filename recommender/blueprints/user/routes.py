from flask import Blueprint
from recommender.blueprints.user.models import User, Client
from recommender.extensions import db, auth_server
from flask_restplus import reqparse
from lib.util_error_respense import format_response
from flask_login import login_user, current_user, login_required, logout_user
from werkzeug.exceptions import Forbidden, BadRequest
import sqlalchemy

user = Blueprint('user', __name__, url_prefix='/user')

account_parser = reqparse.RequestParser()

account_parser.add_argument('email', type=str, required=True)
account_parser.add_argument('password', type=str, required=True)

signup_parser = account_parser.copy()
signup_parser.add_argument('username', type=str)
signup_parser.add_argument('role', type=str, default='member')


@user.route('/signup', methods=['POST'])
@format_response
def signup():

    args = signup_parser.parse_args()

    if (args.get('role', '') == 'admin'):
        if (not isinstance(current_user,
                           User)) or (current_user.role != 'admin'):
            return 'Only admin can sign up admin account', 403
    u = User(**args)
    try:
        u.save()
    except sqlalchemy.exc.IntegrityError:
        return 'This email is already used. Please try another one', 400

    login_user(u)

    return u.client.make_secret_response(), 200


@user.route('/oauth/token', methods=['POST'])
@login_required
@format_response
def issue_token():
    return auth_server.create_token_response(), 200


@user.route('/login', methods=['POST'])
@format_response
def login():
    args = account_parser.parse_args()
    u = User.find_by_identity(args['email'])
    if u and u.authenticated(args['password']) and login_user(u):
        return u.client.make_secret_response(), 200
    else:
        raise BadRequest(description="wrong password or email")


@user.route('/logout', methods=['POST'])
@login_required
@format_response
def logout():

    if logout_user():
        return 'logout success', 200


@user.route('/login/error', methods=['GET'])
@format_response
def login_error():

    return 'please log in', 401
