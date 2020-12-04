from recommender.app import create_redis_app
from recommender.blueprints.article.models import Article, ItemSimilarity
import simplejson as json
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy import or_
from recommender.extensions import celery_app as celery
from recommender.blueprints.article.lib.util_nlp import infer_vec, segment

r_cursor = create_redis_app()

SIMILARITY = 'similarity'
VECTORS = 'vectors'

DEFAULT_CACHE_AMOUNT = 15


def cache_vector(article=None):
    if article:
        vector = {
            'id': article.id,
            'vector': infer_vec(segment(article.content))
        }
        vector = json.dumps(vector)
        r_cursor.hsetnx(VECTORS, str(article.id), vector)
    else:
        for article in Article.get_all():
            vector = {
                'id': article.id,
                'vector': infer_vec(segment(article.content))
            }
            vector = json.dumps(vector)
            r_cursor.hsetnx(VECTORS, str(article.id), vector)


def get_vector(id=None, json_dict=None):
    if id:
        vector = r_cursor.hget(VECTORS, str(id))
    elif json_dict:
        vector = json_dict

    vector = json.loads(vector)
    return vector['vector']


def del_vector_and_similarity(id):
    r_cursor.hdel(VECTORS, str(id))
    ItemSimilarity.delete_by_article_id(id)
    return True


def compute_matrix():
    _, vector_list = r_cursor.hscan(f'{VECTORS}')
    vector_list = list(vector_list.items())

    for i, kv in enumerate(vector_list):
        article_id_i, vector_i = kv[0], kv[1]
        vector_i = get_vector(json_dict=vector_i)
        for j in range(i + 1, len(vector_list)):
            article_id_j, vector_j = vector_list[j]
            if not ItemSimilarity.check_exist(article_id_i, article_id_j):
                vector_j = get_vector(json_dict=vector_j)
                similarity = cosine_similarity([vector_i], [vector_j])
                ItemSimilarity(article_id_i, article_id_j,
                               similarity[0][0].item()).save()


def cache_result_doc(amount=DEFAULT_CACHE_AMOUNT):
    article_list = Article.get_all()
    for _ in article_list:
        i = _.id
        result = ItemSimilarity.query\
        .filter(
            or_(
            ItemSimilarity.article_id1 == i,
            ItemSimilarity.article_id2 == i
            )
            ) \
        .order_by(ItemSimilarity.similarity_doc.desc()) \
        .limit(amount).all()

        if result:
            recommend_list = []
            for s in result:
                if s.article_id1 != i:
                    recommend_list.append(s.article_id1)
                else:
                    recommend_list.append(s.article_id2)

            r_cursor.hset(SIMILARITY, str(i),
                          json.dumps({'similarity_doc': recommend_list}))


def compute_by(text, omit_id=None, amount=DEFAULT_CACHE_AMOUNT):
    vector_i = infer_vec(segment(text))
    id_vector_map = {}
    for k, v in r_cursor.hscan_iter(f'{VECTORS}'):
        if omit_id and str(omit_id) == k:
            continue
        vector_j = get_vector(json_dict=v)
        id_vector_map[k] = cosine_similarity([vector_i],
                                             [vector_j])[0][0].item()
    return sort_by_value(id_vector_map, amount)


def compute_between(text1, text2):
    vector_i, vector_j = infer_vec(segment(text1)), infer_vec(segment(text2))
    similarity = cosine_similarity([vector_i], [vector_j])
    return similarity[0][0].item()


def sort_by_value(d, amount, reverse=True):
    """sort according to value of dictionary
    
    Arguments:
        d {dict} -- dict with values
    
    Keyword Arguments:
        reverse {bool} -- descending (default: {True})
    
    Returns:
        list -- list of ids
    """

    items = d.items()
    backitems = [[v[1], v[0]] for v in items]
    backitems.sort(reverse=reverse)
    if amount < len(backitems):
        return [backitems[i][1] for i in range(0, amount)]
    else:
        return [backitems[i][1] for i in range(0, len(backitems))]


def get_recommend_list(article_id, sim_type):
    recommend_list = r_cursor.hget(SIMILARITY, str(article_id))
    if recommend_list is None:
        return None
    recommend_list = json.loads(recommend_list)
    return recommend_list[sim_type]


@celery.task()
def compute_all():
    cache_vector()
    compute_matrix()
    cache_result_doc()



