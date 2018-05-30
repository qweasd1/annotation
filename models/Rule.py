from app import db


class Rule(db.Model):
    __tablename__ = 'rule'
    id = db.Column(db.Integer,db.Sequence("rule_id_seq"), primary_key=True)
    definition = db.Column(db.Text)
    user = db.Column(db.String(255), nullable=False)
    sense = db.Column(db.Text)
    sense_id = db.Column(db.Text)

