"""Recipes microservice for Recipe Box API."""

import hmac
import os

from dotenv import load_dotenv
from flask import Flask, jsonify, request

from app.config import DevelopmentConfig
from app.extensions import db

load_dotenv()


def create_recipes_app():
    app = Flask(__name__)
    app.config.from_object(DevelopmentConfig)

    db.init_app(app)

    from app import main
    from app.routes.recipes import recipes_bp

    app.register_blueprint(recipes_bp)
    app.teardown_appcontext(main.close_db)

    @app.before_request
    def verify_internal_service_token():
        expected_token = os.getenv("INTERNAL_SERVICE_TOKEN")
        supplied_token = request.headers.get("INTERNAL_SERVICE_TOKEN", "")

        if not expected_token:
            return jsonify({
                "error": "internal service authentication not configured"
            }), 503

        if not hmac.compare_digest(supplied_token, expected_token):
            return jsonify({
                "error": "invalid internal service token"
            }), 403

    return app


app = create_recipes_app()


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5002,
        debug=False,
    )