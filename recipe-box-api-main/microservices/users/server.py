
"""Users microservice for Recipe"""

from flask import Flask, request
import datetime

import jwt
from werkzeug.security import check_password_hash, generate_password_hash
from microservices.users.config import UsersConfig
from microservices.users.extensions import db, migrate


def create_users_app():
    app = Flask(__name__)

    app.config.from_object(UsersConfig)

    db.init_app(app)
    migrate.init_app(app, db)

    # Register the User model for migrations
    from microservices.users.models import User

    @app.get("/health")
    def health():
        return {"status": "users-ok"}

    @app.post("/register")
    def register():
        data = request.get_json() or {}

        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return {"error": "Email and password are required"}, 400

        from sqlalchemy import inspect

        print("SERVER INSTANCE:", app.instance_path)
        print("SERVER DATABASE:", db.engine.url)
        print("SERVER TABLES:", inspect(db.engine).get_table_names())

        if User.query.filter_by(email=email).first():
            return {"error": "Email already registered"}, 409

        user = User(
            email=email,
            password_hash=generate_password_hash(password)
        )

        db.session.add(user)
        db.session.commit()

        return {
            "message": "User registered successfully",
            "user": {
                "id": user.id,
                "email": user.email
            }
        }, 201

    @app.post("/login")
    def login():
        data = request.get_json() or {}
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return {"error": "Email and password are required"}, 400

        user = User.query.filter_by(email=email).first()
        if user is None or not check_password_hash(user.password_hash, password):
            return {"error": "Invalid email or password"}, 401

        now = datetime.datetime.now(datetime.timezone.utc)
        payload = {
            "sub": str(user.id),
            "iat": now,
            "exp": now + datetime.timedelta(
                minutes=app.config["JWT_EXPIRES_MINUTES"]
            ),
        }
        token = jwt.encode(payload, app.config["JWT_SECRET"], algorithm="HS256")
        return {"access_token": token}, 200

    return app


app = create_users_app()

if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5001,
        debug=False,
    )
