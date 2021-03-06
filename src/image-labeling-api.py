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

app.config['THIRD_PARTY_API_KEY'] = os.environ['THIRD_PARTY_API_KEY'].strip()

db = SQLAlchemy(app)

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
    label_1 = db.Column(db.String)
    label_2 = db.Column(db.String)
    label_3 = db.Column(db.String)


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
               'video_id': self.video_id,
               'label_1': self.label_1,
               'label_2': self.label_2,
               'label_3': self.label_3}
        return tmp


def create_label_list(response):
    top_three = [i for i in json.loads(response).keys()][:3]

    out = ["", "", ""]
    for i in range(len(top_three)):
        out[i] = top_three[i]
    return out

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

    url = "https://image-labeling1.p.rapidapi.com/img/label"

    payload = '{"url" : "' + video_path + '"}'

    headers = {
        'content-type': "application/json",
        'x-rapidapi-key': app.config['THIRD_PARTY_API_KEY'],
        'x-rapidapi-host': "image-labeling1.p.rapidapi.com"
    }
    response = requests.request("POST", url, data=payload, headers=headers)

    labels = create_label_list(response.text)

    video = Video.query.filter_by(video_id=video_id).first()
    video.label_1 = labels[0]
    video.label_2 = labels[1]
    video.label_3 = labels[2]

    db.session.add(video)
    db.session.commit()

    logger.info("[image-labeling-api][{}] Got the labels from 3rd party API".format(request_id))

    return make_response({'msg': 'ok'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
