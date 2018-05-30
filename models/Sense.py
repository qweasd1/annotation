from app import db
from .DictSerializable import  DictSerializable

class Sense(db.Model,DictSerializable):
    id = db.Column(db.INTEGER,db.Sequence("sense_id_seq"),primary_key=True)
    abbr = db.Column(db.Text,index=True)
    sense_id = db.Column(db.Text,index=True)
    sense = db.Column(db.Text,index=True)

