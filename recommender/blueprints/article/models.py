from lib.utils_sqlalchemy import ResourceMixin
from recommender.extensions import db
from werkzeug.security import gen_salt
from sqlalchemy import or_, and_


class Article(db.Model, ResourceMixin):
    __tablename__ = 'articles'
    id = db.Column(db.Integer, primary_key=True, index=True)
    title = db.Column(db.String(100), nullable=False, unique=True)
    content = db.Column(db.Text(collation='utf8mb4_bin'))
    ask = db.Column(db.Text(collation='utf8mb4_bin'))
    answer = db.Column(db.Text(collation='utf8mb4_bin'))
    type = db.Column(db.String(100))
    division = db.Column(db.String(100))
    tag = db.Column(db.Text)
    is_delete = db.Column(db.Boolean(), nullable=False, server_default='0')

    def __init__(self, title, type, division, ask='', answer='', **kwargs):
        self.title = title
        self.ask = ask
        self.answer = answer
        self.type = type
        self.division = division
        self.tag = kwargs.get('tag')
        self.key = gen_salt(15)

        _content = f'民眾提問:\n{ask}\n醫師回答:\n{answer}'
        self.content = kwargs.get('content') or _content

    @property
    def info(self):
        return {
            'id': self.id,
            'type': self.type,
            'division': self.division,
            'title': self.title,
            'content': self.content,
            'ask': self.ask,
            'answer': self.answer,
            'created_on': self.created_on,
            'updated_on': self.updated_on
        }

    @classmethod
    def get_all(cls):
        return cls.query.filter(cls.is_delete == 0).all()

    def update(self, **kwargs):
        from recommender.blueprints.article.tasks import del_vector_and_similarity, cache_vector
        fix_contnet = False
        if kwargs.get('title'):
            self.title = kwargs.get('title')

        if kwargs.get('ask'):
            self.ask = kwargs.get('ask')
            fix_contnet = True

        if kwargs.get('asnwer'):
            self.asnwer = kwargs.get('asnwer')
            fix_contnet = True

        if kwargs.get('type'):
            self.type = kwargs.get('type')

        if kwargs.get('division'):
            self.division = kwargs.get('division')

        if kwargs.get('tag'):
            self.tag = kwargs.get('tag')

        if fix_contnet:
            _content = f'民眾提問:\n{self.ask}\n醫師回答:\n{self.answer}'
            self.content = _content

        if kwargs.get('content'):
            self.content = kwargs.get('content')
        del_vector_and_similarity(self.id)
        cache_vector(self)
        self.save()


class ItemSimilarity(ResourceMixin, db.Model):
    #TODO use hybrid property
    __tablename__ = 'item_similarity'
    id = db.Column(db.Integer, primary_key=True)

    article_id1 = db.Column(db.Integer, nullable=False)
    article_id2 = db.Column(db.Integer, nullable=False)
    similarity_doc = db.Column(db.Float, nullable=False)

    def __init__(self, id1, id2, similarity_doc):
        self.article_id1 = id1
        self.article_id2 = id2
        self.similarity_doc = similarity_doc

    @classmethod
    def check_exist(cls, id1, id2):

        if cls.query \
        .filter(
            or_(
            and_(cls.article_id1 == id1 \
                ,cls.article_id2 == id2),
                and_(cls.article_id1 == id2 \
                    ,cls.article_id2 == id1)
            )
        ).first():
            return True
        else:
            return False

    @classmethod
    def delete_by_article_id(cls, article_id):
        delete_count = cls.query.filter(
            or_(cls.article_id1 == article_id,
                cls.article_id2 == article_id)).delete(
                    synchronize_session=False)
        db.session.commit()

        return True