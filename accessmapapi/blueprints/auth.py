from xml.etree import ElementTree as ET

from flask import Blueprint, current_app, jsonify, redirect, url_for
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_refresh_token_required,
)
from authlib.client import OAuth1Session

from ..auth import oauth
from ..models import OpenStreetMapToken


bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.route("/login")
def login():
    redirect_uri = url_for("auth.authorize", _external=True)
    redir = oauth.openstreetmap.authorize_redirect(redirect_uri)
    return redir


@bp.route("/authorize")
def authorize():
    token_resp = oauth.openstreetmap.authorize_access_token()
    token = token_resp["oauth_token"]
    token_secret = token_resp["oauth_token_secret"]

    resp = oauth.openstreetmap.get("user/details")
    if resp.status_code != 200:
        # Bad request of some kind - report failure
        # FIXME: Use proper status code
        return jsonify(msg="Bad Oauth Request"), 400
    xml = resp.text
    etree = ET.fromstring(xml)
    user = etree.findall("user")[0]
    osm_uid = user.attrib["id"]
    display_name = user.attrib["display_name"]

    osm_token_row = OpenStreetMapToken.save(
        osm_uid=osm_uid,
        display_name=display_name,
        oauth_token=token,
        oauth_token_secret=token_secret,
    )

    identity = osm_token_row.user_id

    # FIXME: identity should be a hash, not user ID.
    # FIXME: User ID should also be a hash - though not the same as identity.
    access_token = create_access_token(identity)
    refresh_token = create_refresh_token(identity)
    # TODO: create a whitelist of callback URIs, allow callback URI to be
    # issued at /login endpoint. Should also create an API key that is
    # associated with a given callback URI - new clients are registered by
    # creating a new pair of:
    #    - API Key
    #    - (short) list of allowed callback URIs
    consumer_callback_uri = current_app.config.get("OSM_CONSUMER_CALLBACK_URI")

    url = "{}?access_token={}&refresh_token={}".format(
        consumer_callback_uri, access_token, refresh_token
    )

    return redirect(url)


@bp.route("/refresh", methods=["POST"])
@jwt_refresh_token_required
def refresh():
    current_user = get_jwt_identity()
    ret = {"access_token": create_access_token(current_user)}
    return jsonify(ret), 200


def verify_osm_access_token(osm_access_token, osm_access_token_secret):
    # OSM access tokens do not expire, so there is no manual expiry check here
    # - it is sufficient to look up the row in the database. If we want to
    # block a user, we can just prevent their JWT access and drop the OSM
    # access row.

    # Check the DB for an entry - if it matches, we're happy.
    oauth_token_row = OpenStreetMapToken.query.filter_by(
        osm_access_token=osm_access_token,
        osm_access_token_secret=osm_access_token_secret,
    ).first()

    # This might be a new user requesting access. We will use their OSM access
    # token and secret to retrieve their user_id, demonstrating that the tokens
    # work and producing the necessary info for storing their account
    if oauth_token_row is None:
        session = OAuth1Session(
            CLIENT_ID,
            CLIENT_SECRET,
            token=osm_access_token,
            token_secret=osm_access_token_secret,
        )
        # Need to create new user - fetch from OSM
        resp = session.get(OSM_USER_DETAILS_URL)

        try:
            # TODO: this code is replicated twice - consolidate
            xml = resp.text
            etree = ET.fromstring(xml)
            user = etree.findall("user")[0]
            user_dict = dict(user.attrib)
            osm_uid = user_dict["id"]
            osm_display_name = user_dict["display_name"]
        except:
            return False
    else:
        osm_uid = oauth_token_row.osm_uid
        osm_display_name = oauth_token_row.display_name

    return osm_uid, osm_display_name
