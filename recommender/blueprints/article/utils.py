from werkzeug.exceptions import BadRequest, NotFound
from recommender.blueprints.article.models import Article

def assert_valid_amount(amount, recommend_list):
    if amount > len(recommend_list):
        raise BadRequest(description='amount is too large')

    i = 0
    result = []
    while (i < amount):
        try:
            recommend_article = Article.query.get(recommend_list.pop(0))
        except IndexError:
            raise BadRequest(description='amount is too large')
        if not recommend_article.is_delete:
            i += 1
            result.append(recommend_article.info)

    return result


def check_valid(article_id):
    article = Article.query.get(article_id)
    if article is None:
        raise NotFound(description='This id is invalid')
    elif article.is_delete:
        raise NotFound(description='This article has been deleted')

    return article
