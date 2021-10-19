from flask_jwt_extended import JWTManager

from .models import User, OpenStreetMapToken


# JWT
jwt = JWTManager()


@jwt.user_claims_loader
def add_claims_to_access_token(identity):
    user = User.query.get(identity)
    osm_token = OpenStreetMapToken.query.filter_by(
        user_id=user.user_id
    ).first()

    return {
        "user_id": user.user_id,
        "display_name": osm_token.display_name,
        "role": "accessmap_user",
    }


def init_app(app):
    jwt.init_app(app)
