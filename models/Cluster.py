from app import db
from models.DictSerializable import DictSerializable


class Cluster(db.Model,DictSerializable):
    __tablename__ = 'cluster'
    cluster_abbr_id = db.Column(db.INTEGER, primary_key=True)
    cluster_id = db.Column(db.Integer, primary_key=True)
    count = db.Column(db.INT)
    left = db.Column(db.INT)