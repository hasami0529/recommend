from authlib.flask.oauth2 import ResourceProtector
from authlib.flask.oauth2.sqla import create_bearer_token_validator
from recommender.extensions import db
from recommender.blueprints.user.models import Token

BearerTokenValidator = create_bearer_token_validator(db.session, Token)
auth_required = ResourceProtector()
auth_required.register_token_validator(BearerTokenValidator())
