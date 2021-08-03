import os

from dotenv import load_dotenv
from flask import Flask
from flask_migrate import Migrate

from . import auth
from . import jwt
from .exceptions import MissingConfigError
from .models import db, init_app as db_init_app
from . import blueprints


REQUIRED = [
    "SECRET_KEY",
    "SQLALCHEMY_DATABASE_URI",
    "OAUTH_CACHE_DIR",
    "JWT_SECRET_KEY",
    "OSM_CLIENT_ID",
    "OSM_CLIENT_SECRET",
    "OSM_URI",
    "OSM_CONSUMER_CALLBACK_URI"
]


DEFAULTS = {
    "SQLALCHEMY_DATABASE_URI": "sqlite:////tmp/accessmap-api.db",
    "OAUTH_CACHE_DIR": "/tmp/accessmap-api-cache",
    "OSM_URI": "https://master.apis.dev.openstreetmap.org/"
}


def create_app():
    app = Flask(__name__)

    # Config
    # TODO: do checks on env variable inputs
    load_dotenv()  # TODO: make optional / part of dev only? Try/except/fail?
    app.config.from_mapping(
        SECRET_KEY=os.getenv("SECRET_KEY"),
        SQLALCHEMY_DATABASE_URI=os.getenv("SQLALCHEMY_DATABASE_URI", DEFAULTS["SQLALCHEMY_DATABASE_URI"]),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SQLALCHEMY_ENGINE_OPTIONS={"pool_size": 5, "pool_pre_ping": True},
        OAUTH_CACHE_DIR=os.getenv("OAUTH_CACHE_DIR", DEFAULTS["OAUTH_CACHE_DIR"]),
        JWT_SECRET_KEY=os.getenv("JWT_SECRET_KEY"),
        JWT_IDENTITY_CLAIM="sub",
        OSM_CLIENT_ID=os.getenv("OSM_CLIENT_ID"),
        OSM_CLIENT_SECRET=os.getenv("OSM_CLIENT_SECRET"),
        OSM_URI=os.getenv("OSM_URI", DEFAULTS["OSM_URI"]),
        OSM_CONSUMER_CALLBACK_URI=os.getenv("OSM_CONSUMER_CALLBACK_URI")
    )
    for env_var in REQUIRED:
        env = app.config.get(env_var, None)
        if env is None:
            raise MissingConfigError("{} environment variable not set.".format(env_var))

    # Attach database
    db.init_app(app)

    # Attach migration scripts (Alembic / Flask-Migrate)
    migrate = Migrate(app, db)

    # Add oauth interface
    auth.init_app(app)

    # Add JWT
    jwt.init_app(app)

    # Add views
    app.register_blueprint(blueprints.auth.bp)
    app.register_blueprint(blueprints.profiles.bp)
    app.register_blueprint(blueprints.user.bp)

    return app
