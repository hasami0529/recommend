import pytest
from flask import url_for
import simplejson as json


class APITestMixin(object):
    """
    Automatically load in a session and client, this is common for a lot of
    tests that work with views.
    """

    admin_client_id = None
    admin_secret = None
    admin_token = None

    member_client_id = None
    member_secret = None
    member_token = None

    @pytest.fixture(autouse=True)
    def set_common_fixtures(self, session, client):
        self.session = session
        self.client = client

    def login(self, email='admin@gmail.com', password='adminPassword'):
        """
        Login a specific user.

        :return: Flask response
        """
        return login(self.client, email, password)

    def login_member(self, email='member@gmail.com',
                     password='memberPassword'):
        return login(self.client, email, password)

    def logout(self):
        """
        Logout a specific user.

        :return: Flask response
        """
        return logout(self.client)

    @pytest.fixture
    def member_secret(self):
        res = self.login_member()
        res = json.loads(res.data)

        res = res['payLoad']
        self.member_client_id = res['client_id']
        self.member_secret = res['client_secret']

        return res

    @pytest.fixture
    def admin_secret(self):
        res = self.login()
        res = json.loads(res.data)

        res = res['payLoad']
        self.admin_client_id = res['client_id']
        self.admin_secret = res['client_secret']

        return res

    @pytest.fixture
    def admin_token(self, admin_secret):
        res = self.client.post(url_for('user.issue_token'),
                               data={
                                   'grant_type': 'client_credentials',
                                   **admin_secret
                               })
        res = json.loads(res.data)
        self.admin_token = res['token_type'] + ' ' + res['access_token']

        return self.admin_token

    @pytest.fixture
    def member_token(self, member_secret):
        res = self.client.post(url_for('user.issue_token'),
                               data={
                                   'grant_type': 'client_credentials',
                                   **member_secret
                               })
        res = json.loads(res.data)
        self.member_token = res['token_type'] + ' ' + res['access_token']

        return self.member_token


def login(client, email='', password=''):
    """
    Log a specific user in.

    :param client: Flask client
    :param username: The username
    :type username: str
    :param password: The password
    :type password: str
    :return: Flask response
    """
    user = dict(email=email, password=password)

    response = client.post(url_for('user.login'), data=user)

    return response


def logout(client):
    """
    Log a specific user out.

    :param client: Flask client
    :return: Flask response
    """
    return client.post(url_for('user.logout'), follow_redirects=True)
