from app import db
from models.DictSerializable import DictSerializable


class ClusterInstance(db.Model,DictSerializable):
    __tablename__ = 'cluster_instance'
    id = db.Column(db.Integer,db.Sequence("cluster_instance_id"), primary_key=True)
    instance_id = db.Column(db.INTEGER)
    doc_id = db.Column(db.INTEGER)
    cluster_id = db.Column(db.INTEGER)
    abbr_id = db.Column(db.INTEGER)
    segement_position = db.Column(db.INT)
    fulltext_position = db.Column(db.INT)
    sense_id =  db.Column(db.INT,nullable=True)

db.Index("abbr_id_cluster_id_index",ClusterInstance.abbr_id,ClusterInstance.cluster_id)