from flask import *
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
import requests
import datetime
import string
import random
from elasticsearch import Elasticsearch


# logging imports
import logging
from logstash_async.handler import AsynchronousLogstashHandler
from logstash_async.handler import LogstashFormatter


route = '/v1'
app = Flask(__name__)
CORS(app, resources={r"/v1/*": {"origins": "*"}})
# DB settings
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DB_URI']
app.config['USERS_API_URI'] = 'http://users-api:8080/v1' # environ['USERS_API_URI']

db = SQLAlchemy(app)
es = Elasticsearch(cloud_id=app.config['ES_CLOUD_ID'], http_auth=('elastic', app.config['ES_PASSWD']))

# getting media directory ready
app.config['MEDIA_DIR'] = './media/'
if not os.path.exists(app.config['MEDIA_DIR']):
    os.mkdir(app.config['MEDIA_DIR'])

# -------------------------------------------
# Logging setup
# -------------------------------------------
# Create the logger and set it's logging level
logger = logging.getLogger("logstash")
logger.setLevel(logging.INFO)        

log_endpoint_uri = str(os.environ["LOGS_URI"]).strip()
log_endpoint_port = int(os.environ["LOGS_PORT"].strip())


# Create the handler
handler = AsynchronousLogstashHandler(
    host=log_endpoint_uri,
    port=log_endpoint_port, 
    ssl_enable=True, 
    ssl_verify=False,
    database_path='')

# Here you can specify additional formatting on your log record/message
formatter = LogstashFormatter()
handler.setFormatter(formatter)

# Assign handler to the logger
logger.addHandler(handler)


# models
class Video(db.Model):
    __tablename__ = 'videos'

    video_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer)
    title = db.Column(db.String)
    description = db.Column(db.String)
    width = db.Column(db.String)
    height = db.Column(db.String)
    created_on = db.Column(db.String)
    path = db.Column(db.String)

    def __init__(self, user_id, title, description, w, h, path):
        self.user_id = user_id
        self.title = title
        self.description = description
        self.width = w
        self.height = h
        self.created_on = str(datetime.datetime.utcnow())
        self.path = path

    def to_dict(self):
        tmp = {'title': self.title,
               'user_id': self.user_id,
               'description': self.description,
               'width': self.width,
               'height': self.height,
               'created_on': self.created_on,
               'path': self.path,
               'video_id': self.video_id}
        return tmp


# views
@app.route(route + '/image-labeling/<int:video_id>', methods=['GET'])
def image_labeling(video_id):
    """
    This method receives the path of the image and forwards the request to the 3rd
    party API, which labels the image. Then, the labels are saved to the database.
    :return:
    """
    request_id = None
    if 'X-Request-ID' in request.headers:
        request_id = request.headers.get('X-Request-ID')
    video_path = Video.query.filter_by(video_id=video_id).first().path

    payload = "{\n    \"url\": \"https://www.inferdo.com/img/label-1.jpg\"\n}"
    headers = {
        'content-type': "application/json",
        'x-rapidapi-key': "f6c69cec91msha413c5b0abb8a20p13497ejsnade379e02f39",
        'x-rapidapi-host': "image-labeling1.p.rapidapi.com"
    }
    response = requests.request("POST", video_path, data=payload, headers=headers)
    print(response.text)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
