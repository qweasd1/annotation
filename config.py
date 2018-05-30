import os
basedir = os.path.abspath(os.path.dirname(__file__))
database_url = os.environ.get('DATABASE_URL')
if database_url:
    database_url = database_url#.replace("%","%%")
print(database_url)
class Config(object):
    # ...
    SQLALCHEMY_DATABASE_URI = database_url or 'postgresql://phdacareadmin:%Gv5xy?yMsR;2D9M@localhost:9999/phdacare' # or 'postgresql://root:root@localhost:5432/upmc-nlp-annotation'
    # SQLALCHEMY_DATABASE_URI = 'postgresql://root:root@localhost:5432/upmc-nlp-annotation'


    SQLALCHEMY_TRACK_MODIFICATIONS = True
    UPLOAD_FOLDER = os.path.join(basedir,"uploads")


if not os.path.exists(Config.UPLOAD_FOLDER):
    os.makedirs(Config.UPLOAD_FOLDER)