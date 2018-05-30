from app import db
from models.DictSerializable import DictSerializable


class ClusterDocument(db.Model,DictSerializable):
    __tablename__ = 'cluster_document'

    source_id = db.Column(db.Integer,primary_key=True)
    doc_id = db.Column(db.Integer,primary_key=True)
    data = db.Column(db.TEXT)
