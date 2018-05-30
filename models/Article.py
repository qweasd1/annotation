import enum


from app import db
from sqlalchemy.dialects import postgresql
from .DictSerializable import DictSerializable

def create_tsvector(*args):
    exp = args[0]
    for e in args[1:]:
        exp += ' ' + e
    return db.func.to_tsvector('english', exp)


class ArticleState(enum.Enum):
    clean = 0
    draft = 1
    submit = 2


class Article(db.Model, DictSerializable):
    __tablename__ = 'article'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    user = db.Column(db.String(255))
    annotated_text = db.Column(db.Text)
    annotated_json = db.Column(db.JSON)
    source = db.Column(db.Text)
    state = db.Column(db.SmallInteger, default=0)

    # __ts_vector__ = create_tsvector(
    #     db.cast(db.func.coalesce(text, ''), postgresql.TEXT)
    # )
    #
    # __table_args__ = (
    #     db.Index(
    #         'idx_article_fts',
    #         __ts_vector__,
    #         postgresql_using='gin'
    #     ),
    # )
