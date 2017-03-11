from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import redis


db = SQLAlchemy()
redis_db = None
# redis_db = redis.StrictRedis(host=app.config["REDIS_HOST"], port=app.config["REDIS_PORT"], db=0)


def create_app():
    app = Flask(__name__)
    app.config.from_object('config')
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    from .api import api as api_blueprint
    app.register_blueprint(api_blueprint)
    
    return app
