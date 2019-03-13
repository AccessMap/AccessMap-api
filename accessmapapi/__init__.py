import os

from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from . import auth
from . import jwt
from .models import db
from . import blueprints


def create_app():
    app = Flask(__name__)

    # Config
    # TODO: do checks on env variable inputs
    load_dotenv()  # TODO: make optional / part of dev only? Try/except/fail?
    app.config.from_mapping(
        SECRET_KEY=os.getenv("FLASK_SECRET"),
        SQLALCHEMY_DATABASE_URI=os.getenv("SQLALCHEMY_DATABASE_URI"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        OAUTH_CACHE_DIR=os.getenv("OAUTH_CACHE_DIR"),
        JWT_SECRET_KEY=os.getenv("JWT_SECRET"),
        JWT_IDENTITY_CLAIM="sub",
        OSM_CLIENT_ID=os.getenv("OSM_CLIENT_ID"),
        OSM_CLIENT_SECRET=os.getenv("OSM_CLIENT_SECRET"),
        OSM_URI=os.getenv("OSM_URI"),
        CONSUMER_CALLBACK_URI=os.getenv("CONSUMER_CALLBACK_URI"),
        APPLICATION_ROOT=os.getenv("APPLICATION_ROOT")
    )

    # Attach database
    db.init_app(app)

    # Migrate database
    # FIXME: move db creation stuff into a separate, trackable migration framework
    with app.app_context():
        db.create_all()

    # Add oauth interface
    auth.init_app(app)

    # Add JWT
    jwt.init_app(app)

    # Add views
    app.register_blueprint(blueprints.auth.bp)
    app.register_blueprint(blueprints.profiles.bp)
    app.register_blueprint(blueprints.user.bp)

    return app
