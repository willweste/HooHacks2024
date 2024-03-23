from flask import Flask
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

from config import Config
from .jwt_config import setup_jwt

db = SQLAlchemy()
bcrypt = Bcrypt()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    bcrypt.init_app(app)
    setup_jwt(app)

    from app.models import User
    with app.app_context():
        db.create_all()

    from .routes import setup_routes
    setup_routes(app)
    return app