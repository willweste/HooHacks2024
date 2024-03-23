import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(os.path.abspath(os.path.dirname(__file__)), "BioGuard.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False