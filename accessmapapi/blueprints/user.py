from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required

from ..models import User, OpenStreetMapToken


bp = Blueprint("user", __name__, url_prefix="/user")


@bp.route("/profile", methods=["GET"])
@jwt_required
def user_profile():
    current_user = get_jwt_identity()
    user = User.query.get(current_user)
    osm_token = OpenStreetMapToken.query.filter_by(
        user_id=user.user_id
    ).first()

    return jsonify(user_id=user.user_id, display_name=osm_token.display_name)
