from flask import Flask

from .config import DevelopmentConfig, TestingConfig, ProductionConfig
from .extensions import db


def create_app(config_name):
    """Application factory."""
    app = Flask(__name__)

    configurations = {
        "development": DevelopmentConfig,
        "testing": TestingConfig,
        "production": ProductionConfig,
    }

    app.config.from_object(configurations[config_name])

    # Connect SQLAlchemy to this application.
    db.init_app(app)

    from . import main
    from .routes.auth import auth_bp
    from .routes.recipes import recipes_bp

    # Keep the original routes working.
    app.register_blueprint(main.bp)

    # Register the feature blueprints.
    app.register_blueprint(auth_bp, url_prefix="")
    app.register_blueprint(recipes_bp, url_prefix="")

    # Keep existing SQLite connection cleanup working.
    app.teardown_appcontext(main.close_db)

    return app