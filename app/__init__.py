import os
import logging

from flask_session import Session
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
    db_url = 'sqlite:///../main.db'
    app = Flask(__name__)
    CORS(app)  # add CORS
    app.secret_key = "super secret key"
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config["TEMPLATES_AUTO_RELOAD"] = True
    app.config["SESSION_PERMANENT"] = False
    app.config["SESSION_TYPE"] = "filesystem"
    Session(app)
    
    if not database_exists(db_url):
        create_database(db_url)

    from app.models import db

    db.init_app(app)  # initialize Flask SQLALchemy with this flask app
    Migrate(app, db)

    from app.routes import main

    # why blueprints http://flask.pocoo.org/docs/1.0/blueprints/
    app.register_blueprint(main.main)

    return app