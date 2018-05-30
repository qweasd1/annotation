import os
from flask import Flask, jsonify, request, Response
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS



# app = Flask(__name__)
app = Flask(__name__,static_url_path="")
CORS(app)
app.config.from_object(Config)
db = SQLAlchemy(app)



from models import Article, Sense, Rule, ClusterAbbr, ClusterDocument, ClusterInstance, Cluster

migrate = Migrate(app, db)
import tempfile



# import sqlalchemy
# from sqlalchemy import create_engine
# from sqlalchemy import Column, Integer, String, Sequence, Text, JSON
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import Session
# Base = declarative_base()
#
# engine = create_engine('postgresql://root:root@localhost:5432/upmc-nlp-annotation', echo=True)
#
#
#
# class Article(Base):
#     __tablename__ = 'article'
#     id = Column(Integer, primary_key=True)
#     text = Column(Text,nullable=False)
#     user = Column(String(255),nullable=False)
#     annotated_text = Column(Text)
#     annotated_json = Column(JSON)
#
# class Rule(Base):
#     __tablename__ = 'rule'
#     id = Column(Integer,Sequence("rule_id_seq"), primary_key=True)
#     definition = Column(Text)
#     description = Column(Text)
#     user = Column(String(255), nullable=False)
#     structure = Column(JSON)
#
#
# Base.metadata.create_all(engine)
#
#
# session = Session(bind=engine)
# # session.add(User(name="tony"))
#
# # session.query(User).filter_by(name="tony").first()

def _recusive_to_json(data):
    if type(data) == list:
        return [ _recusive_to_json(x) for x in data]
    else:
        return data._asdict()

def to_json(data):
    return jsonify(_recusive_to_json(data))

@app.route("/api/articles", methods=["GET","POST","PATCH"])
def articles():
    from algorithm import generate_annotation_text
    if request.method == "GET":
        from algorithm import genereate_annotation_text_json
        if "user" in request.args:
            user = request.args["user"]
            query = Article.query.filter(db.or_(Article.state == 0,db.and_(Article.state== 1,Article.user == user)))
        elif "state" in request.args:
            state = int(request.args["state"])
            query = Article.query.filter(Article.state == state)
        else:
            query = Article.query.filter(Article.state == 0)

        page = 1
        if "page" in request.args:
            page = int(request.args["page"])

        page_size = 10
        if "pageSize" in request.args:
            page_size = int(request.args["pageSize"])

        if "source" in request.args:
            source = request.args["source"].strip()
            if source:
                query = query.filter(Article.source == source)

        if "search" in request.args:
            search = request.args["search"]
            if search:
                query = query.filter(Article.text.like("%" + search + "%"))
        result = query.order_by(db.desc(Article.state)).paginate(page,page_size,False)

        for article in result.items:
            if not article.annotated_json:
                article.annotated_json = genereate_annotation_text_json(article.text)
        query.session.commit()

        return jsonify({
            "total":result.total,
            "hasNext":result.has_next,
            "data":[x._asdict() for x in result.items]
        })

    elif request.method == "POST":
        body = request.get_json()
        if type(body) == dict:
            db.session.add(Article(**body,state = 0))
            db.session.commit()
            return jsonify({
                "success":True
            })
    elif request.method == "PATCH":
        bodies = request.get_json()
        for body in bodies:
            if "annotated_json" in body:
                body["annotated_text"] = generate_annotation_text(body["annotated_json"])
            Article.query.filter(Article.id == body["id"]).update(body)
        Article.query.session.commit()
        return jsonify({
            "success": True
        })

@app.route("/api/articles/sources",methods=["GET"])
def artilce_types():
    return jsonify([x[0] for x in db.session.query(Article.source).distinct(Article.source).all()])


@app.route("/api/articles/<article_id>", methods=["PATCH","GET"])
def artilce_one(article_id):
    from algorithm import generate_annotation_text
    article_id = int(article_id)
    if request.method == "GET":
        return to_json(Article.query.filter(Article.id == article_id).first())
    if request.method == "PATCH":
        body = request.get_json()
        if "annotated_json" in body:
            body["annotated_text"] = generate_annotation_text(body["annotated_json"])
        Article.query.filter(Article.id == article_id).update(body)
        Article.query.session.commit()
        return jsonify({
            "success": True
        })


@app.route("/api/load-data",methods=["POST"])
def loadData():

    file = request.files["file"]
    source = "<Unknown>"
    if "source" in request.values:
        source = request.values["source"]
    _,save_path = tempfile.mkstemp(dir=app.config['UPLOAD_FOLDER'])
    file.save(save_path)
    counter = 0
    with open(save_path) as data:
        for line in data:
            db.session.add(Article(text = line,source=source,state=0))
            counter +=1
            if counter == 3000:
                db.session.commit()
                counter = 0
    db.session.commit()

    return jsonify({
        "success":True
    })


@app.route("/api/senses",methods=["GET","POST"])
def sense_all():
    if request.method == "GET":
        query = Sense.query
        if "search" in request.args:
            search = request.args["search"]
            query = query.filter(Sense.abbr.ilike(search))
        if "sense" in request.args:
            sense = request.args["sense"]
            query = query.filter(Sense.sense.ilike("%" + sense + "%"))
        return to_json(query.all())
    elif request.method == "POST":
        from algorithm import get_sense_inventory
        body = request.get_json()
        sense = Sense(**body)
        db.session.add(sense)
        db.session.commit()
        get_sense_inventory().add(body["abbr"])
        sense.sense_id = str(sense.id)
        db.session.commit()
        return to_json(sense)

@app.route("/api/download/training-data",methods=["GET"])
def download_training_data():
    query = Article.query.filter(Article.state == 2)
    if "source" in request.args:
        source = request.args["source"].strip()
        if source:
            query = query.filter(Article.source == source)

    if "search" in request.args:
        search = request.args["search"]
        if search:
            query = query.filter(Article.text.like("%" + search + "%"))
    if "size" in request.args:
        size = request.args["size"]
        if size:
            size = int(size)
            query = query.limit(size)
    result = query.all()

    def generate():
        for record in result:
            yield record.annotated_text.replace("\n","<EOL>") + "\n"
    return Response(generate(),mimetype="text/plain")

@app.route("/api/download/sense-inventory",methods=["GET"])
def download_sense_inventory():
    result = db.engine.execute("select abbr, sense_id,sense from sense")

    def generate():
        for record in result:
            yield record[0] + "|" + record[1] + "|" + record[2] + "\n"
    return Response(generate(),mimetype="text/plain")

@app.route("/api/cluster/abbrs",methods=["GET"])
def search_cluster_abbrs():

    source_id = int(request.args["source_id"])
    if "search" in request.args:
        search = request.args["search"]
    else:
        search = ""
    query = ClusterAbbr.query.filter(ClusterAbbr.source_id == source_id, ClusterAbbr.abbr.like("%" + search + "%")).order_by(db.desc(ClusterAbbr.left))
    return to_json(query.all())

@app.route("/api/abbrs/<abbr_id>/clusters",methods=["GET"])
def search_cluster(abbr_id):

    abbr_id = int(abbr_id)

    query = Cluster.query.filter(Cluster.cluster_abbr_id == abbr_id).order_by(db.desc(Cluster.left))
    return to_json(query.all())

@app.route("/api/abbrs/<abbr_id>/clusters/<cluster_id>",methods=["GET","POST"])
def get_one_cluster(abbr_id, cluster_id):
    abbr_id = int(abbr_id)
    cluster_id = int(cluster_id)
    if request.method == "GET":
        ClusterInstance.query.filter()
        query = ClusterInstance.query.filter(ClusterInstance.abbr_id == abbr_id,ClusterInstance.cluster_id == cluster_id,ClusterInstance.sense_id == None)
        instances = query.all()
        docs = ClusterDocument.query.filter(ClusterDocument.doc_id.in_(set([instance.doc_id for instance in instances]))).all()
        return jsonify({
            "docs":_recusive_to_json(docs),
            "instances":_recusive_to_json(instances)
        })
    elif request.method == "POST":
        body = request.get_json()
        sense_id = body["sense_id"]
        instance_ids = body["instance_ids"]

        # update sense
        db.session.bulk_update_mappings(ClusterInstance,[{"id":id,"sense_id":sense_id} for id in instance_ids])
        db.session.flush()
        db.session.commit()

        # update left count
        instance_count = len(instance_ids)
        Cluster.query.filter(Cluster.cluster_id == cluster_id).update({"left":Cluster.left - instance_count})
        Cluster.query.session.commit()

        ClusterAbbr.query.filter(ClusterAbbr.id == abbr_id).update({"left": ClusterAbbr.left - instance_count})
        ClusterAbbr.query.session.commit()
        return jsonify({
            "success":True
        })

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    return app.send_static_file('index.html')


if __name__ == "__main__":
    app.run(port=5000)
