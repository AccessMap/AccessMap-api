import os
from xml.etree import ElementTree as ET

from flask import Blueprint, current_app, jsonify, redirect, request, url_for
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from authlib.client import OAuth1Session
from authlib.flask.client import OAuth

from ..auth import oauth
from ..models import User, OpenStreetMapToken


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
        oauth_token_secret=token_secret
    )

    access_token = create_access_token(identity=osm_token_row.user_id)
    return jsonify(access_token=access_token), 200


@bp.route("/token", methods=["POST"])
def token():
    """Exchange an OSM access token for an AccessMap access JWT."""

    # Verify inputs
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    osm_access_token = request.json.get("osm_access_token", None)
    if osm_access_token is None:
        return jsonify({"msg": "Missing OpenStreetMap Access Token"}), 400

    osm_access_token_secret = request.json.get("osm_access_token_secret", None)
    if osm_access_token_secret is None:
        return jsonify({"msg": "Missing OpenStreetMap Access Token Secret"}), 400

    # Verify that their access token is legit - function checks DB or asks OSM itself.
    osm_uid, osm_display_name = verify_osm_access_token(osm_access_token, osm_access_token_secret)
    if not osm_uid:
        return jsonify({"msg": "Invalid OpenStreetMap Access Token"}), 400

    # If there is no user / OSM token entry in the db, create one
    # TODO: make this less redundant? verify_osm_access_token already runs some of
    # the queries in .save()
    osm_token_row = OpenStreetMapToken.save(
        osm_uid=osm_uid,
        display_name=osm_name,
        oauth_token=osm_access_token,
        oauth_token_secret=osm_access_token_secret
    )

    access_token = create_access_token(identity=osm_token_row.user_id)
    return jsonify(access_token=access_token), 200


def verify_osm_access_token(osm_access_token, osm_access_token_secret):
    # OSM access tokens do not expire, so there is no manual expiry check here - it is
    # sufficient to look up the row in the database. If we want to block a user, we can
    # just prevent their JWT access and drop the OSM access row.

    # Check the DB for an entry - if it matches, we're happy.
    oauth_token_row = OpenStreetMapToken.query.filter_by(
        osm_access_token=osm_access_token,
        osm_access_token_secret=osm_access_token_secret
    ).first()

    # This might be a new user requesting access. We will use their OSM access token
    # and secret to retrieve their user_id, demonstrating that the tokens work and
    # producing the necessary info for storing their account
    if item is None:
        session = OAuth1Session(
            CLIENT_ID,
            CLIENT_SECRET,
            token=item.osm_token,
            token_secret=item.osm_token_secret
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
