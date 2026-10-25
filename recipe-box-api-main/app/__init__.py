
from flask import Flask
from sqlalchemy import event

from .config import DevelopmentConfig, TestingConfig, ProductionConfig
from .extensions import db, migrate, cache, limiter

from .models.user import User
from .models.recipe import Recipe

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
    migrate.init_app(app, db)
    cache.init_app(app)
    limiter.init_app(app)

    with app.app_context():
        engine = db.engine

    @event.listens_for(engine, "connect")
    def enable_sqlite_foreign_keys(dbapi_connection, connection_record):
        """Enable SQLite foreign-key enforcement."""
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys = ON")
        cursor.close()

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
