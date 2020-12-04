from flask import url_for
from lib.tests import APITestMixin


class TestLogin(APITestMixin):
    def test_login(self):
        """ Login successfully. """
        response = self.login()
        assert response.status_code == 200

    def test_signup(self):
        member_user = {
            'email': 'member2@gmail.com',
            'password': 'member2Password'
        }
        res = self.client.post(url_for('user.signup'), data=member_user)
        assert res.status_code == 200

    def test_get_token(self, admin_secret):
        res = self.client.post(url_for('user.issue_token'),
                               data={
                                   'grant_type': 'client_credentials',
                                   **admin_secret
                               })
        assert res.status_code == 200

    def test_signup_dup(self):
        member_user = {
            'email': 'member@gmail.com',
            'password': 'memberPassword'
        }
        res = self.client.post(url_for('user.signup'), data=member_user)
        assert res.status_code == 400

    def test_member_signup_admin(self):
        u = {
            'email': 'member3@gmail.com',
            'password': 'member3Password',
            'role': 'admin'
        }

        res = self.client.post(url_for('user.signup'), data=u)
        assert res.status_code == 403

    def test_logout(self):
        self.login()
        res = self.logout()
        assert res.status_code == 200
