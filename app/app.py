
   
import os
import logging

from flask import Flask, request
from flask_cors import CORS
from flask_migrate import Migrate
from sqlalchemy_utils import create_database, database_exists

from api.config import config
from api.core import all_exception_handler


class RequestFormatter(logging.Formatter):
    def format(self, record):
        record.url = request.url
        record.remote_addr = request.remote_addr
        return super().format(record)


def create_app(test_config=None):

    app = Flask(__name__)

    CORS(app)  # add CORS

    env = os.environ.get("FLASK_ENV", "dev")
    if test_config:
        app.config.from_mapping(**test_config)
    else:
        app.config.from_object(config[env])  

    # logging
    formatter = RequestFormatter(
        "%(asctime)s %(remote_addr)s: requested %(url)s: %(levelname)s in [%(module)s: %(lineno)d]: %(message)s"
    )
    if app.config.get("LOG_FILE"):
        fh = logging.FileHandler(app.config.get("LOG_FILE"))
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)
        app.logger.addHandler(fh)

    strm = logging.StreamHandler()
    strm.setLevel(logging.DEBUG)
    strm.setFormatter(formatter)

    app.logger.addHandler(strm)
    app.logger.setLevel(logging.DEBUG)

    root = logging.getLogger("core")
    root.addHandler(strm)

    # decide whether to create database
    if env != "prod":
        db_url = app.config["SQLALCHEMY_DATABASE_URI"]
        if not database_exists(db_url):
            create_database(db_url)

    # register sqlalchemy to this app
    from api.models import db

    db.init_app(app)  # initialize Flask SQLALchemy with this flask app
    Migrate(app, db)

    # import and register blueprints
    from api.views import main

    # why blueprints http://flask.pocoo.org/docs/1.0/blueprints/
    app.register_blueprint(main.main)

    # register error Handler
    app.register_error_handler(Exception, all_exception_handler)

    return app