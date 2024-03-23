from datetime import timedelta
from flask import redirect, url_for
from flask_jwt_extended import JWTManager

def setup_jwt(app):
    app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
    app.config["JWT_COOKIE_SECURE"] = False  # Set to True in production for HTTPS
    app.config["JWT_COOKIE_CSRF_PROTECT"] = True
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)

    jwt = JWTManager(app)

    @jwt.unauthorized_loader
    def missing_jwt_response(callback):
        return redirect(url_for("login"))

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return redirect(url_for("login"))