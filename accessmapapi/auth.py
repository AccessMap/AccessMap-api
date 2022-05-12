import os

from authlib.flask.client import OAuth

from .models import cache


oauth = OAuth(cache=cache)


def init_app(app):
    client_id = app.config["OSM_CLIENT_ID"]
    client_secret = app.config["OSM_CLIENT_SECRET"]
    request_token_url = os.path.join(
        app.config["OSM_URI"], "oauth/request_token"
    )
    access_token_url = os.path.join(
        app.config["OSM_URI"], "oauth/access_token"
    )
    authorize_url = os.path.join(app.config["OSM_URI"], "oauth/authorize")
    api_url = os.path.join(app.config["OSM_URI"], "api/0.6/")

    oauth.register(
        name="openstreetmap",
        client_id=client_id,
        client_secret=client_secret,
        request_token_url=request_token_url,
        request_token_params=None,
        access_token_url=access_token_url,
        access_token_params=None,
        refresh_token_url=None,
        authorize_url=authorize_url,
        api_base_url=api_url,
        client_kwargs=None,
    )

    oauth.init_app(app)
