"""Users microservice for Recipe Box API."""

from flask import Flask

from app.config import DevelopmentConfig
from app.extensions import db


def create_users_app():
    app = Flask(__name__)
    app.config.from_object(DevelopmentConfig)

    db.init_app(app)

    from app import main
    from app.routes.auth import auth_bp

    app.register_blueprint(auth_bp)
    app.teardown_appcontext(main.close_db)

    return app


app = create_users_app()


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5001,
        debug=False,
    )