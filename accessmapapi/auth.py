import os

from authlib.flask.client import OAuth
from flask import g, session

from .models import OpenStreetMapToken, cache


# def get_current_user():
#     user = getattr(g, 'current_user', None)
#     if user:
#         return user
#
#     sid = session.get('sid')
#     if not sid:
#         return None
#
#     user = User.query.get(sid)
#     if not user:
#         logout()
#         return None
#
#     g.current_user = user
#     return user
#
#
# current_user = LocalProxy(get_current_user)
#
#
# def fetch_token(osm_uid):
#     user = get_current_user()
#     osm_token = OpenStreetMapToken.query.filter_by(
#         osm_uid=osm_uid
#     ).first()
#     return osm_token.to_dict()


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
