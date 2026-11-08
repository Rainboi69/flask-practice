import os


class UsersConfig:
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///users.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET = os.environ.get("JWT_SECRET")
    JWT_EXPIRES_MINUTES = 60
