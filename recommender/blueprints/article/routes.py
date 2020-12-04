import simplejson as json
import sqlalchemy
from flask import Blueprint, request
from flask_restplus import reqparse
from recommender.blueprints.article.models import Article
from recommender.blueprints.article.utils import (assert_valid_amount,
                                                  check_valid)
from recommender.extensions import db
from werkzeug.exceptions import BadRequest, NotFound

from lib.util_auth import auth_required
from lib.util_error_respense import format_response

article = Blueprint('article', __name__, url_prefix='/article')

article_parser = reqparse.RequestParser()
article_parser.add_argument('title', required=True)
article_parser.add_argument('ask', type=str)
article_parser.add_argument('answer', type=str)
article_parser.add_argument('type', type=str)
article_parser.add_argument('division', type=str)

article_parser.add_argument('tag', type=str)
article_parser.add_argument('content', type=str)

recommend_parser = reqparse.RequestParser()
recommend_parser.add_argument('amount',
                              type=int,
                              required=True,
                              location='args')

similarity_parser = reqparse.RequestParser()
similarity_parser.add_argument('text1',
                               type=str,
                               required=True,
                               location='args')
similarity_parser.add_argument('text2',
                               type=str,
                               required=True,
                               location='args')

text_parser = reqparse.RequestParser()
text_parser.add_argument('text', type=str, required=True, location='args')
text_parser.add_argument('amount', type=int, required=True, location='args')

backend_parser = reqparse.RequestParser()
backend_parser.add_argument('targets',
                            type=list,
                            required=True,
                            location='json')


@article.route('/<int:id>', methods=['DELETE', 'PATCH'])
@article.route('', methods=['POST'], defaults={'id': None})
@format_response
@auth_required('admin')
def handle_article(id=None):
    from recommender.blueprints.article.tasks import cache_vector, del_vector_and_similarity
    if request.method == 'POST':
        args = article_parser.parse_args()
        a = Article(**args)

        try:
            a.save()
        except sqlalchemy.exc.IntegrityError:
            return 'This article already exists', 400

        cache_vector(a)
        return a.info, 200

    article = check_valid(id)
    if request.method == 'DELETE':
        article.is_delete = True
        del_vector_and_similarity(article.id)
        article.save()
        return article.info, 200

    if request.method == 'PATCH':
        update_parser = article_parser.copy()
        update_parser.replace_argument('title', required=False)
        args = update_parser.parse_args()
        article.update(**args)
        return article.info, 200


@article.route('/page/<int:page>', methods=['GET'])
@auth_required('member admin', 'OR')
@format_response
def get_article_with_page(page):
    articles_page = Article.query\
    .filter(Article.is_delete == 0)\
    .order_by(Article.updated_on.desc())\
    .paginate(page, 10, True)

    return [i.info for i in articles_page.items], 200


@article.route('/recommend/<int:article_id>', methods=['GET'])
@auth_required('member admin', 'OR')
@format_response
def recommend(article_id, sim_type='similarity_doc'):
    from recommender.blueprints.article.tasks import get_recommend_list, compute_by

    args = recommend_parser.parse_args()
    amount = args['amount']
    article = check_valid(article_id)
    recommend_list = get_recommend_list(article_id, sim_type)

    if recommend_list is None:
        recommend_list = compute_by(article.content, omit_id=article.id)

    return assert_valid_amount(amount, recommend_list), 200


@article.route('/similarity', methods=['GET'])
@auth_required('member admin', 'OR')
@format_response
def get_similarity():
    args = similarity_parser.parse_args()
    text1 = args['text1']
    text2 = args['text2']
    from recommender.blueprints.article.tasks import compute_between
    similarity = compute_between(text1, text2)
    return {'similarity': similarity}, 200


@article.route('/recommend/text', methods=['GET'])
@auth_required('member admin', 'OR')
@format_response
def recommend_by_text():
    args = text_parser.parse_args()

    text = args['text']
    amount = args['amount']
    from recommender.blueprints.article.tasks import compute_by
    recommend_list = compute_by(text)
    return assert_valid_amount(amount, recommend_list), 200


@article.route('/cache', methods=['PATCH'])
@auth_required('admin')
@format_response
def backend_all():
    from recommender.blueprints.article.tasks import compute_all
    compute_all.delay()
    return 'ok', 200
