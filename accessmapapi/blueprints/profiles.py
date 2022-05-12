from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from ..models import Profile


bp = Blueprint("profiles", __name__, url_prefix="/profiles")


@bp.route("/", methods=["PUT"], strict_slashes=False)
@jwt_required
def set_profile():
    current_user = get_jwt_identity()

    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    uphill_max = request.json.get("uphill_max", None)
    if uphill_max is None:
        return jsonify({"msg": "Missing uphill_max"}), 400

    downhill_max = request.json.get("downhill_max", None)
    if downhill_max is None:
        return jsonify({"msg": "Missing downhill_max"}), 400

    avoid_curbs = request.json.get("avoid_curbs", None)
    if avoid_curbs is None:
        return jsonify({"msg": "Missing avoid_curbs"}), 400

    Profile.save(
        user_id=current_user,
        uphill_max=uphill_max,
        downhill_max=downhill_max,
        avoid_curbs=avoid_curbs,
    )

    return jsonify({"msg": "Successfully added/updated profile"}), 200


@bp.route("/", methods=["GET"], strict_slashes=False)
@jwt_required
def get_profile():
    """Get user routing profiles. Note that while only one is currently
    stored/retrieved, this function has been written in anticipation of storing
    multiple profiles."""
    current_user = get_jwt_identity()
    profile = Profile.query.filter_by(user_id=current_user).first()
    if profile is None:
        profiles = []
    else:
        profiles = [
            {
                "uphill_max": profile.uphill_max,
                "downhill_max": profile.downhill_max,
                "avoid_curbs": profile.avoid_curbs,
            }
        ]
    return jsonify({"profiles": profiles}), 200
