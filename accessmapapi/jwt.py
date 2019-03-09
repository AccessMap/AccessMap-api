from flask_jwt_extended import JWTManager

# JWT
jwt = JWTManager()


def init_app(app):
    jwt.init_app(app)
