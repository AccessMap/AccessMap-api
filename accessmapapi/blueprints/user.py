from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required

from ..models import User, OpenStreetMapToken


bp = Blueprint("user", __name__, url_prefix="/user")


@bp.route("/profile", methods=["GET"])
@jwt_required
def user_profile():
    current_user = get_jwt_identity()
    print("Current user:", current_user)
    user = User.query.get(current_user)
    return jsonify(user_id=user.user_id)
