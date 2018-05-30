from app import db
from models.DictSerializable import DictSerializable


class ClusterAbbr(db.Model,DictSerializable):
    __tablename__ = 'cluster_abbr'
    id = db.Column(db.Integer,db.Sequence("cluster_abbr_id"), primary_key=True)
    abbr = db.Column(db.String(128))
    count = db.Column(db.INT)
    left  = db.Column(db.INT)
    source_id = db.Column(db.INT)