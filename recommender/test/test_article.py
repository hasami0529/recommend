from lib.tests import APITestMixin
from flask import url_for


class TestLogin(APITestMixin):
    # def test_create_article(self):
    #     data = {
    #         "title": "test1",
    #         "ask": "ask",
    #         "answer": "answer",
    #         "type": "type",
    #         "division": "division"
    #     }
    #     res = self.client.post(url_for('article.handle_article'), data=data)
    #     assert res.status_code == 200

    def test_get_articles(self, admin_token):
        headers = {'Authorization': admin_token}
        res = self.client.get(url_for('article.get_article_with_page', page=1),
                              headers=headers)
        assert res.status_code == 200

    def test_edit_aticle(self):
        pass

    def test_delete_aticle(self):
        pass

    def test_wrong_page(self):
        pass

    def test_wrong_id(self):
        pass
