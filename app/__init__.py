import os
import logging

from flask import Flask, request
from flask_cors import CORS
from flask_migrate import Migrate
from sqlalchemy_utils import create_database, database_exists


class RequestFormatter(logging.Formatter):
    def format(self, record):
        record.url = request.url
        record.remote_addr = request.remote_addr
        return super().format(record)



def create_app():

    app = Flask(__name__)

    CORS(app)  # add CORS

    db_url = 'sqlite:///main.db'
    if not database_exists(db_url):
        create_database(db_url)

    from app.models import db

    db.init_app(app)  # initialize Flask SQLALchemy with this flask app
    Migrate(app, db)

    from app.views import main

    # why blueprints http://flask.pocoo.org/docs/1.0/blueprints/
    app.register_blueprint(main.main)

    return app